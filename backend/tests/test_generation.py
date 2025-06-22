import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from main import app
from models.project import Project, ProjectStatus
from core.database import get_db

@pytest.fixture
async def test_project(db_session: AsyncSession):
    """Crée un projet de test"""
    project = Project(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Test Manga",
        synopsis="Un manga de test",
        style="shonen"
    )
    db_session.add(project)
    await db_session.commit()
    return project

@pytest.mark.asyncio
async def test_start_generation(
    client: AsyncClient,
    test_project: Project,
    mock_auth
):
    """Test le lancement de génération"""
    
    response = await client.post(
        f"/api/v1/generation/start/{test_project.id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "generation_started"

@pytest.mark.asyncio
async def test_regenerate_panel(
    client: AsyncClient,
    test_panel,
    mock_auth
):
    """Test la regénération d'une case"""
    
    modifications = {
        "description": "Nouvelle description",
        "dialogue": [
            {"character": "Hero", "text": "Nouveau dialogue!"}
        ]
    }
    
    response = await client.post(
        f"/api/v1/generation/regenerate/panel/{test_panel.id}",
        json=modifications,
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "regenerated"
