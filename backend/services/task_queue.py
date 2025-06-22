from celery import Celery, Task
from celery.result import AsyncResult
import asyncio
from typing import Dict, Any
import uuid

from core.config import settings
from modules.scenario.generator import ScenarioGenerator
from modules.character_design.designer import CharacterDesigner
from modules.page_generation.generator import PageGenerator
from modules.lettering.letterer import Letterer
from modules.export.exporter import MangaExporter

celery_app = Celery(
    "manga_factory",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 heure max par tâche
    task_soft_time_limit=3300,
)

class CallbackTask(Task):
    """Tâche avec callbacks pour progress tracking"""
    def on_success(self, retval, task_id, args, kwargs):
        """Succès"""
        pass
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Échec"""
        pass

@celery_app.task(bind=True, base=CallbackTask, name="generate_manga")
def generate_manga_task(self, project_id: str) -> Dict[str, Any]:
    """Tâche principale de génération de manga"""
    
    # Conversion en async
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            _generate_manga_async(self, project_id)
        )
        return result
    finally:
        loop.close()

async def _generate_manga_async(task: Task, project_id: str):
    """Logique async de génération"""
    
    # Update progress
    task.update_state(
        state='PROGRESS',
        meta={'current': 0, 'total': 100, 'status': 'Initialisation...'}
    )
    
    # 1. Génération du scénario
    scenario_gen = ScenarioGenerator()
    task.update_state(
        state='PROGRESS',
        meta={'current': 10, 'total': 100, 'status': 'Génération du scénario...'}
    )
    
    # 2. Design des personnages
    character_designer = CharacterDesigner()
    task.update_state(
        state='PROGRESS',
        meta={'current': 30, 'total': 100, 'status': 'Création des personnages...'}
    )
    
    # 3. Génération des pages
    page_gen = PageGenerator()
    task.update_state(
        state='PROGRESS',
        meta={'current': 60, 'total': 100, 'status': 'Génération des planches...'}
    )
    
    # 4. Lettrage
    letterer = Letterer()
    task.update_state(
        state='PROGRESS',
        meta={'current': 80, 'total': 100, 'status': 'Ajout du lettrage...'}
    )
    
    # 5. Export final
    exporter = MangaExporter()
    task.update_state(
        state='PROGRESS',
        meta={'current': 95, 'total': 100, 'status': 'Export en cours...'}
    )
    
    return {'status': 'completed', 'project_id': project_id}

def enqueue_generation_task(project_id: str) -> str:
    """Lance une tâche de génération"""
    task = generate_manga_task.delay(str(project_id))
    return task.id

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Récupère le statut d'une tâche"""
    result = AsyncResult(task_id, app=celery_app)
    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result,
        'info': result.info
    }
