from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "Manga Factory"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Services
    OPENAI_API_KEY: str
    REPLICATE_API_TOKEN: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    # Storage
    S3_BUCKET: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str = "us-east-1"
    
    # GPU Services
    LAMBDA_LABS_API_KEY: Optional[str] = None
    GPU_ENDPOINT: Optional[str] = None
    
    # Generation Settings
    MAX_PAGES_PER_CHAPTER: int = 30
    MAX_PANELS_PER_PAGE: int = 8
    DEFAULT_DPI: int = 600
    
    class Config:
        env_file = ".env"

settings = Settings()
