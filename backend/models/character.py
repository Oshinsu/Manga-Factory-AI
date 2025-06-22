from sqlalchemy import Column, String, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from core.database import Base

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    
    # Informations de base
    name = Column(String(100), nullable=False)
    description = Column(Text)
    personality = Column(Text)
    backstory = Column(Text)
    
    # Design visuel
    visual_description = Column(Text, nullable=False)
    reference_images = Column(JSON, default=list)  # URLs des images
    
    # LoRA training
    lora_path = Column(String(500))
    lora_trigger_word = Column(String(100))
    training_status = Column(String(50), default="pending")
    training_params = Column(JSON)
    
    # Features extraites pour cohérence
    visual_features = Column(JSON)  # Embeddings, couleurs, etc.
    
    # Relations
    project = relationship("Project", back_populates="characters")
