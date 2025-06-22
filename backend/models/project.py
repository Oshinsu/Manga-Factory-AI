from sqlalchemy import Column, String, Text, JSON, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from core.database import Base

class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"

class MangaStyle(str, enum.Enum):
    SHONEN = "shonen"
    SHOJO = "shojo"
    SEINEN = "seinen"
    JOSEI = "josei"
    KODOMO = "kodomo"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(255), nullable=False)
    synopsis = Column(Text)
    style = Column(Enum(MangaStyle), default=MangaStyle.SHONEN)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    
    # Métadonnées de génération
    generation_params = Column(JSON, default={})
    
    # Relations
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    number = Column(Integer, nullable=False)
    title = Column(String(255))
    synopsis = Column(Text)
    script = Column(JSON)  # Découpage détaillé par page
    
    project = relationship("Project", back_populates="chapters")
    pages = relationship("Page", back_populates="chapter", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"))
    page_number = Column(Integer, nullable=False)
    layout = Column(JSON)  # Structure des cases
    
    chapter = relationship("Chapter", back_populates="pages")
    panels = relationship("Panel", back_populates="page", cascade="all, delete-orphan")

class Panel(Base):
    __tablename__ = "panels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey("pages.id"))
    panel_number = Column(Integer, nullable=False)
    
    # Contenu
    description = Column(Text)  # Description de la scène
    dialogue = Column(JSON)  # Bulles de dialogue
    image_url = Column(String(500))
    
    # Métadonnées de génération
    prompt = Column(Text)
    seed = Column(Integer)
    generation_params = Column(JSON)
    
    page = relationship("Page", back_populates="panels")
