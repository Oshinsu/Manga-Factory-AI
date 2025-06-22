from typing import List, Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import asyncio
import aiohttp

from core.config import settings

class Letterer:
    def __init__(self):
        self.fonts = {
            "dialogue": "assets/fonts/manga_dialogue.ttf",
            "narration": "assets/fonts/manga_narration.ttf",
            "sfx": "assets/fonts/manga_sfx.ttf"
        }
        self.bubble_detector = BubbleDetector()
        
    async def add_lettering_to_page(
        self,
        page_image: str,
        panels_data: List[Dict[str, Any]]
    ) -> str:
        """Ajoute le lettrage complet à une page"""
        
        # Chargement de l'image
        img = self._decode_image(page_image)
        
        # Détection des bulles
        bubbles = await self.bubble_detector.detect_bubbles(img)
        
        # Association bulles-dialogues
        bubble_assignments = self._assign_dialogues_to_bubbles(
            bubbles, 
            panels_data
        )
        
        # Ajout du texte
        for bubble, dialogue in bubble_assignments:
            img = self._add_text_to_bubble(
                img,
                bubble,
                dialogue
            )
        
        # Ajout des onomatopées
        for panel in panels_data:
            if panel.get("sound_effects"):
                img = await self._add_sound_effects(
                    img,
                    panel
                )
        
        return self._encode_image(img)
    
    def _add_text_to_bubble(
        self,
        img: np.ndarray,
        bubble: Dict[str, Any],
        dialogue: Dict[str, Any]
    ) -> np.ndarray:
        """Ajoute du texte dans une bulle"""
        
        # Conversion en PIL
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        # Calcul de la taille optimale
        font_size = self._calculate_optimal_font_size(
            dialogue["text"],
            bubble["bounds"]
        )
        
        font = ImageFont.truetype(
            self.fonts["dialogue"],
            font_size
        )
        
        # Texte vertical pour le japonais
        if dialogue.get("language", "ja") == "ja":
            text_img = self._draw_vertical_text(
                dialogue["text"],
                font,
                bubble["bounds"]
            )
            pil_img.paste(text_img, bubble["bounds"][:2], text_img)
        else:
            # Texte horizontal avec word wrap
            wrapped_text = self._wrap_text(
                dialogue["text"],
                font,
                bubble["bounds"][2] - bubble["bounds"][0]
            )
            
            y_offset = bubble["bounds"][1]
            for line in wrapped_text:
                draw.text(
                    (bubble["bounds"][0], y_offset),
                    line,
                    font=font,
                    fill="black"
                )
                y_offset += font.getsize(line)[1] + 5
        
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    async def _add_sound_effects(
        self,
        img: np.ndarray,
        panel: Dict[str, Any]
    ) -> np.ndarray:
        """Ajoute les onomatopées avec style manga"""
        
        for sfx in panel["sound_effects"]:
            if settings.USE_IDEOGRAM:
                # Génération avec Ideogram 3.0
                sfx_image = await self._generate_sfx_ideogram(
                    sfx["text"],
                    sfx.get("style", "impact")
                )
            else:
                # Utilisation de font locale
                sfx_image = self._create_sfx_local(
                    sfx["text"],
                    sfx.get("style", "impact")
                )
            
            # Placement intelligent
            position = self._find_sfx_position(
                img,
                sfx_image,
                panel["bounds"]
            )
            
            # Fusion avec l'image
            img = self._blend_sfx(img, sfx_image, position)
        
        return img

class BubbleDetector:
    """Détecteur de bulles de dialogue"""
    
    def __init__(self):
        self.min_area = 500
        self.max_area = 50000
        
    async def detect_bubbles(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """Détecte les bulles dans l'image"""
        
        # Preprocessing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        
        # Détection des contours
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        bubbles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area < area < self.max_area:
                # Vérification forme elliptique
                if self._is_bubble_shape(contour):
                    x, y, w, h = cv2.boundingRect(contour)
                    bubbles.append({
                        "bounds": (x, y, x+w, y+h),
                        "area": area,
                        "contour": contour
                    })
        
        return bubbles
    
    def _is_bubble_shape(self, contour) -> bool:
        """Vérifie si le contour ressemble à une bulle"""
        
        # Approximation polygonale
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
        # Ratio d'aspect
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Circularité
        area = cv2.contourArea(contour)
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        return (
            len(approx) > 6 and  # Forme arrondie
            0.5 < aspect_ratio < 2.0 and  # Pas trop allongé
            circularity > 0.6  # Relativement circulaire
        )
