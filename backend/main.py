from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from redis import asyncio as aioredis
from celery import Celery

from api.routers import projects, generation, characters, export
from core.config import settings
from core.database import engine, Base

# Initialisation Celery
celery_app = Celery(
    "manga_factory",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = await aioredis.from_url(settings.REDIS_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await app.state.redis.close()

app = FastAPI(
    title="Manga Factory API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(generation.router, prefix="/api/v1/generation", tags=["generation"])
app.include_router(characters.router, prefix="/api/v1/characters", tags=["characters"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])

# WebSocket pour updates temps réel
@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await websocket.accept()
    redis = app.state.redis
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"project:{project_id}")
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_json(message["data"])
    except:
        await pubsub.unsubscribe()
