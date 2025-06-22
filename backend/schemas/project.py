from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from models.project import ProjectStatus, MangaStyle

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    synopsis: Optional[str] = None
    style: MangaStyle = MangaStyle.SHONEN

class ProjectCreate(ProjectBase):
    generation_params: Optional[Dict[str, Any]] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    synopsis: Optional[str] = None
    style: Optional[MangaStyle] = None
    status: Optional[ProjectStatus] = None
    generation_params: Optional[Dict[str, Any]] = None

class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None
    visual_description: str
    personality: Optional[str] = None
    backstory: Optional[str] = None

class CharacterResponse(CharacterBase):
    id: uuid.UUID
    lora_status: str
    reference_images: List[str]
    
    class Config:
        from_attributes = True

class ChapterBase(BaseModel):
    number: int
    title: Optional[str] = None
    synopsis: Optional[str] = None

class PageBase(BaseModel):
    page_number: int
    layout: Dict[str, Any]

class PanelBase(BaseModel):
    panel_number: int
    description: Optional[str] = None
    dialogue: Optional[List[Dict[str, str]]] = None
    image_url: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: uuid.UUID
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    characters: List[CharacterResponse] = []
    
    class Config:
        from_attributes = True
