from typing import List, Dict, Any
import asyncio
from openai import AsyncOpenAI
import json

from core.config import settings
from models.project import Chapter, Page, Panel

class ScenarioGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def generate_chapter_outline(
        self, 
        synopsis: str, 
        style: str,
        chapter_number: int = 1
    ) -> Dict[str, Any]:
        """Génère le découpage d'un chapitre"""
        
        system_prompt = f"""Tu es un scénariste expert en manga {style}.
        Crée un découpage détaillé pour le chapitre {chapter_number}.
        
        Format de sortie JSON:
        {{
            "title": "Titre du chapitre",
            "synopsis": "Résumé du chapitre",
            "pages": [
                {{
                    "page_number": 1,
                    "panels": [
                        {{
                            "panel_number": 1,
                            "type": "establishing_shot|close_up|action|dialogue",
                            "description": "Description visuelle détaillée",
                            "dialogue": [
                                {{"character": "Nom", "text": "Dialogue"}}
                            ],
                            "sound_effects": ["SFX1", "SFX2"]
                        }}
                    ]
                }}
            ]
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Synopsis: {synopsis}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def enhance_panel_description(
        self,
        panel_data: Dict[str, Any],
        character_refs: List[Dict[str, Any]]
    ) -> str:
        """Enrichit la description d'une case pour la génération d'image"""
        
        character_descriptions = "\n".join([
            f"{char['name']}: {char['visual_description']}"
            for char in character_refs
        ])
        
        prompt = f"""Transforme cette description de case manga en prompt détaillé pour génération d'image.
        
        Personnages disponibles:
        {character_descriptions}
        
        Description originale: {panel_data['description']}
        Type de case: {panel_data['type']}
        
        Génère un prompt qui inclut:
        - Style manga/anime
        - Composition de la case
        - Expressions des personnages
        - Éléments de décor
        - Éclairage et ambiance
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        return response.choices[0].message.content
