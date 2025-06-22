from typing import List, Dict, Any
import asyncio
import aiohttp
import json

from core.config import settings
from modules.character_design.designer import CharacterDesigner

class PageGenerator:
    def __init__(self):
        self.sd_endpoint = settings.GPU_ENDPOINT or "http://localhost:7860"
        self.character_designer = CharacterDesigner()
        
    async def generate_page(
        self,
        page_data: Dict[str, Any],
        characters: List[Dict[str, Any]],
        style_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère une page complète avec cohérence"""
        
        # Extraction des LoRA des personnages
        character_loras = {
            char["name"]: char["lora_path"] 
            for char in characters 
            if "lora_path" in char
        }
        
        # Génération séquentielle des cases avec contexte
        generated_panels = []
        context_embeddings = None
        
        for panel in page_data["panels"]:
            # Génération avec StoryDiffusion pour cohérence
            panel_result = await self._generate_panel_with_context(
                panel,
                character_loras,
                context_embeddings,
                style_params
            )
            
            generated_panels.append(panel_result)
            context_embeddings = panel_result["embeddings"]
        
        # Composition de la page
        page_layout = await self._compose_page_layout(
            generated_panels,
            page_data.get("layout", "standard")
        )
        
        return {
            "page_number": page_data["page_number"],
            "panels": generated_panels,
            "layout": page_layout,
            "full_page_image": page_layout["composed_image"]
        }
    
    async def _generate_panel_with_context(
        self,
        panel: Dict[str, Any],
        character_loras: Dict[str, str],
        context: Any,
        style_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère une case avec cohérence contextuelle"""
        
        # Construction du prompt avec style manga
        prompt = f"""{panel['enhanced_description']},
        manga panel, {style_params['style']} style,
        {style_params.get('additional_tags', '')}
        """
        
        # Ajout des LoRA des personnages présents
        active_loras = []
        for dialogue in panel.get("dialogue", []):
            char_name = dialogue.get("character")
            if char_name in character_loras:
                active_loras.append({
                    "path": character_loras[char_name],
                    "strength": 0.8
                })
        
        # Paramètres StoryDiffusion
        generation_params = {
            "prompt": prompt,
            "negative_prompt": "bad anatomy, blurry, low quality",
            "width": 512,
            "height": 768,
            "steps": 25,
            "cfg_scale": 7,
            "sampler": "DPM++ 2M Karras",
            "loras": active_loras,
            "story_mode": True,
            "context_embeddings": context,
            "panel_type": panel.get("type", "standard")
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.sd_endpoint}/api/story_generate",
                json=generation_params
            ) as resp:
                result = await resp.json()
        
        return {
            "panel_number": panel["panel_number"],
            "image": result["image"],
            "embeddings": result["embeddings"],
            "seed": result["seed"],
            "prompt_used": prompt
        }
    
    async def _compose_page_layout(
        self,
        panels: List[Dict[str, Any]],
        layout_type: str
    ) -> Dict[str, Any]:
        """Compose les cases selon le layout manga"""
        
        # Utilisation de YOLO-Layout ou heuristiques
        if layout_type == "standard":
            layout_config = self._get_standard_layout(len(panels))
        else:
            layout_config = await self._detect_optimal_layout(panels)
        
        # Composition avec PIL
        compose_params = {
            "panels": [p["image"] for p in panels],
            "layout": layout_config,
            "page_size": (2480, 3508),  # A4 600dpi
            "margins": {"top": 100, "bottom": 100, "left": 80, "right": 80},
            "gutter": 20  # Espace entre cases
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.sd_endpoint}/api/compose_page",
                json=compose_params
            ) as resp:
                result = await resp.json()
        
        return result
