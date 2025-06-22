"""API personnalisée pour les besoins spécifiques manga"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import base64
import io
from PIL import Image
import numpy as np
import torch
import json

app = FastAPI()

# Import ComfyUI modules
import sys
sys.path.append('/app')
import execution
import folder_paths
from nodes import NODE_CLASS_MAPPINGS

class MangaGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 512
    height: int = 768
    steps: int = 25
    cfg_scale: float = 7.0
    sampler: str = "DPM++ 2M Karras"
    seed: int = -1
    loras: List[Dict[str, Any]] = []
    story_mode: bool = False
    context_embeddings: Optional[str] = None
    panel_type: str = "standard"

class StoryDiffusionRequest(BaseModel):
    panels: List[Dict[str, Any]]
    style_reference: Optional[str] = None
    character_loras: Dict[str, str] = {}
    maintain_consistency: bool = True

@app.post("/api/generate")
async def generate_manga_panel(request: MangaGenerationRequest):
    """Génère une case de manga avec cohérence"""
    
    # Construction du workflow ComfyUI
    workflow = build_manga_workflow(request)
    
    # Exécution
    prompt_id = execution.queue_prompt(workflow)[1]
    
    # Attente du résultat
    result = await wait_for_result(prompt_id)
    
    return JSONResponse({
        "image": result["image"],
        "seed": result["seed"],
        "embeddings": result.get("embeddings")
    })

@app.post("/api/story_generate")
async def generate_story_sequence(request: StoryDiffusionRequest):
    """Génère une séquence cohérente de cases"""
    
    results = []
    context = None
    
    for panel in request.panels:
        # Workflow avec contexte de cohérence
        workflow = build_story_workflow(
            panel,
            context,
            request.character_loras,
            request.style_reference
        )
        
        prompt_id = execution.queue_prompt(workflow)[1]
        result = await wait_for_result(prompt_id)
        
        results.append(result)
        context = result.get("embeddings")
    
    return JSONResponse({"panels": results})

@app.post("/api/train_lora")
async def train_character_lora(request: Dict[str, Any]):
    """Lance l'entraînement d'un LoRA personnage"""
    
    # Configuration du training
    training_config = {
        "model_name": request["model_name"],
        "dataset": request["dataset"],
        "base_model": request.get("base_model", "anything-v5"),
        "steps": request.get("training_steps", 1000),
        "batch_size": request.get("batch_size", 2),
        "learning_rate": request.get("learning_rate", 1e-4),
        "rank": 32,
        "alpha": 16,
    }
    
    # Lancement asynchrone du training
    task_id = await launch_lora_training(training_config)
    
    return JSONResponse({
        "task_id": task_id,
        "status": "training_started",
        "estimated_time": training_config["steps"] * 2  # secondes estimées
    })

@app.post("/api/compose_page")
async def compose_manga_page(request: Dict[str, Any]):
    """Compose une page manga à partir des cases"""
    
    panels = [decode_base64_image(p) for p in request["panels"]]
    layout = request["layout"]
    page_size = tuple(request["page_size"])
    margins = request["margins"]
    gutter = request["gutter"]
    
    # Création de la page
    page = Image.new("RGB", page_size, "white")
    
    # Placement des cases selon le layout
    for i, (panel, layout_info) in enumerate(zip(panels, layout["panels"])):
        x = margins["left"] + layout_info["x"]
        y = margins["top"] + layout_info["y"]
        
        # Redimensionnement si nécessaire
        panel_resized = panel.resize(
            (layout_info["width"], layout_info["height"]),
            Image.LANCZOS
        )
        
        # Ajout d'une bordure
        bordered = add_panel_border(panel_resized, thickness=3)
        
        page.paste(bordered, (x, y))
    
    # Conversion en base64
    buffer = io.BytesIO()
    page.save(buffer, format="PNG", dpi=(600, 600))
    composed_image = base64.b64encode(buffer.getvalue()).decode()
    
    return JSONResponse({
        "composed_image": composed_image,
        "layout": layout
    })

def build_manga_workflow(request: MangaGenerationRequest) -> Dict:
    """Construit un workflow ComfyUI pour génération manga"""
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "anything-v5-fp16.safetensors"
            }
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": f"{request.prompt}, manga style, high quality",
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": request.negative_prompt,
                "clip": ["1", 1]
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": request.width,
                "height": request.height,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": request.seed if request.seed != -1 else np.random.randint(0, 2**32),
                "steps": request.steps,
                "cfg": request.cfg_scale,
                "sampler_name": request.sampler,
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": "manga_panel"
            }
        }
    }
    
    # Ajout des LoRA si présents
    if request.loras:
        for i, lora in enumerate(request.loras):
            lora_node_id = str(10 + i)
            workflow[lora_node_id] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": lora["path"],
                    "strength_model": lora["strength"],
                    "strength_clip": lora["strength"],
                    "model": ["1", 0] if i == 0 else [str(10 + i - 1), 0],
                    "clip": ["1", 1] if i == 0 else [str(10 + i - 1), 1]
                }
            }
            # Mise à jour des références
            workflow["5"]["inputs"]["model"] = [lora_node_id, 0]
            workflow["2"]["inputs"]["clip"] = [lora_node_id, 1]
            workflow["3"]["inputs"]["clip"] = [lora_node_id, 1]
    
    return workflow

async def wait_for_result(prompt_id: str, timeout: int = 300):
    """Attend le résultat d'une génération"""
    
    start_time = asyncio.get_event_loop().time()
    
    while True:
        if asyncio.get_event_loop().time() - start_time > timeout:
            raise HTTPException(status_code=408, detail="Generation timeout")
        
        # Vérification du statut
        history = execution.get_history(prompt_id)
        if prompt_id in history:
            outputs = history[prompt_id]["outputs"]
            if "7" in outputs:  # Node SaveImage
                images = outputs["7"]["images"]
                if images:
                    # Lecture de l'image générée
                    image_path = folder_paths.get_annotated_filepath(images[0]["filename"])
                    with open(image_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode()
                    
                    return {
                        "image": image_data,
                        "seed": history[prompt_id]["outputs"]["5"]["seed"],
                        "embeddings": None  # TODO: extraire les embeddings
                    }
        
        await asyncio.sleep(0.5)

def decode_base64_image(base64_string: str) -> Image.Image:
    """Décode une image base64"""
    img_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(img_data))

def add_panel_border(image: Image.Image, thickness: int = 2) -> Image.Image:
    """Ajoute une bordure noire style manga"""
    bordered = Image.new("RGB", 
        (image.width + thickness*2, image.height + thickness*2), 
        "black"
    )
    bordered.paste(image, (thickness, thickness))
    return bordered
