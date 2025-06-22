from typing import List, Dict, Any
import asyncio
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import base64

from core.config import settings

class MangaExporter:
    def __init__(self):
        self.dpi = settings.DEFAULT_DPI
        self.page_size = A4  # (595, 842) points at 72dpi
        
    async def export_to_pdf(
        self,
        project_id: str,
        pages: List[Dict[str, Any]],
        export_format: str = "print"
    ) -> str:
        """Exporte le manga en PDF haute qualité"""
        
        # Buffer pour le PDF
        pdf_buffer = io.BytesIO()
        
        # Création du canvas
        c = canvas.Canvas(
            pdf_buffer,
            pagesize=self.page_size
        )
        
        # Métadonnées
        c.setAuthor("Manga Factory AI")
        c.setTitle(f"Manga Project {project_id}")
        
        # Ajout des pages
        for i, page_data in enumerate(pages):
            if i > 0:
                c.showPage()
            
            # Conversion haute résolution
            page_image = await self._prepare_page_for_print(
                page_data["full_page_image"],
                export_format
            )
            
            # Ajout au PDF
            img_reader = ImageReader(page_image)
            c.drawImage(
                img_reader,
                0, 0,
                width=self.page_size[0],
                height=self.page_size[1],
                preserveAspectRatio=True
            )
        
        # Finalisation
        c.save()
        pdf_buffer.seek(0)
        
        # Upload vers S3
        pdf_url = await self._upload_to_s3(
            pdf_buffer.getvalue(),
            f"exports/{project_id}/manga.pdf"
        )
        
        return pdf_url
    
    async def export_to_webtoon(
        self,
        project_id: str,
        pages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Exporte au format webtoon (vertical scroll)"""
        
        # Concaténation verticale des pages
        webtoon_strips = []
        
        for chapter_pages in self._group_by_chapter(pages):
            strip = await self._create_webtoon_strip(chapter_pages)
            webtoon_strips.append(strip)
        
        return {
            "format": "webtoon",
            "strips": webtoon_strips,
            "dimensions": {
                "width": 800,
                "height": "variable"
            }
        }
    
    async def _prepare_page_for_print(
        self,
        page_image_b64: str,
        format: str
    ) -> Image.Image:
        """Prépare une page pour l'impression haute qualité"""
        
        # Décodage
        img_data = base64.b64decode(page_image_b64)
        img = Image.open(io.BytesIO(img_data))
        
        if format == "print":
            # Redimensionnement à 600 DPI
            target_width = int(8.27 * self.dpi)  # A4 width in inches
            target_height = int(11.69 * self.dpi)  # A4 height in inches
            
            img = img.resize(
                (target_width, target_height),
                Image.LANCZOS
            )
            
            # Conversion CMYK pour impression
            if img.mode != "CMYK":
                img = img.convert("CMYK")
        
        return img
    
    async def create_animated_preview(
        self,
        panels: List[Dict[str, Any]],
        animation_params: Dict[str, Any]
    ) -> str:
        """Crée un GIF animé à partir de certaines cases"""
        
        animated_panels = [
            p for p in panels 
            if p.get("animate", False)
        ]
        
        if not animated_panels:
            return None
        
        # Utilisation d'AnimateDiff v3
        animations = []
        for panel in animated_panels:
            anim = await self._generate_panel_animation(
                panel,
                animation_params
            )
            animations.append(anim)
        
        # Composition en GIF
        gif_url = await self._compose_gif(animations)
        
        return gif_url
