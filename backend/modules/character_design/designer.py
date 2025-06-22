import aiohttp
import asyncio
from typing import Dict, Any, List
import base64
from PIL import Image
import io

from core.config import settings

class CharacterDesigner:
    def __init__(self):
        self.sd_endpoint = settings.GPU_ENDPOINT or "http://localhost:7860"
        self.lora_models = {
            "shonen": "anime_shonen_v1.safetensors",
            "shojo": "anime_shojo_v1.safetensors",
            "seinen": "anime_seinen_v1.safetensors"
        }
    
    async def create_character_reference(
        self,
        name: str,
        description: str,
        style: str = "shonen",
        variations: int = 4
    ) -> Dict[str, Any]:
        """Crée une fiche de référence pour un personnage"""
        
        # Prompt de base pour character sheet
        base_prompt = f"""anime character reference sheet, {description},
        multiple views, front view, side view, back view, 3/4 view,
        full body, consistent design, white background,
        {style} manga style, high quality, detailed
        """
        
        negative_prompt = """inconsistent, different characters, blurry,
        low quality, cropped, incomplete, watermark"""
        
        # Génération via ComfyUI/SD
        async with aiohttp.ClientSession() as session:
            payload = {
                "prompt": base_prompt,
                "negative_prompt": negative_prompt,
                "width": 1024,
                "height": 1024,
                "steps": 30,
                "cfg_scale": 7.5,
                "sampler": "DPM++ 2M Karras",
                "seed": -1,
                "batch_size": variations,
                "lora": self.lora_models.get(style),
                "lora_strength": 0.8
            }
            
            async with session.post(
                f"{self.sd_endpoint}/api/generate",
                json=payload
            ) as resp:
                result = await resp.json()
        
        # Traitement et sauvegarde des références
        character_data = {
            "name": name,
            "description": description,
            "style": style,
            "reference_sheet": result["images"][0],
            "variations": result["images"],
            "seed": result["seed"],
            "generation_params": payload
        }
        
        # Extraction des features pour LoRA training
        character_data["lora_dataset"] = await self._prepare_lora_dataset(
            character_data["variations"]
        )
        
        return character_data
    
    async def _prepare_lora_dataset(
        self,
        images: List[str]
    ) -> Dict[str, Any]:
        """Prépare le dataset pour l'entraînement LoRA"""
        
        dataset = {
            "images": [],
            "captions": []
        }
        
        for i, img_b64 in enumerate(images):
            # Conversion et preprocessing
            img_data = base64.b64decode(img_b64)
            img = Image.open(io.BytesIO(img_data))
            
            # Redimensionnement pour training
            img_resized = img.resize((512, 512), Image.LANCZOS)
            
            # Sauvegarde temporaire
            buffer = io.BytesIO()
            img_resized.save(buffer, format="PNG")
            
            dataset["images"].append(base64.b64encode(buffer.getvalue()).decode())
            dataset["captions"].append(f"character reference {i+1}")
        
        return dataset
    
    async def train_character_lora(
        self,
        character_id: str,
        dataset: Dict[str, Any]
    ) -> str:
        """Entraîne un LoRA spécifique pour un personnage"""
        
        training_config = {
            "model_name": f"character_{character_id}",
            "base_model": "animefull-final-pruned",
            "dataset": dataset,
            "training_steps": 1000,
            "learning_rate": 1e-4,
            "batch_size": 2,
            "gradient_accumulation_steps": 2
        }
        
        # Lancement du training asynchrone
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.sd_endpoint}/api/train_lora",
                json=training_config
            ) as resp:
                result = await resp.json()
        
        return result["lora_path"]
