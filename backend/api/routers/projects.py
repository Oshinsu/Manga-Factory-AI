from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from core.database import get_db
from core.security import get_current_user
from models.project import Project, ProjectStatus, MangaStyle
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crée un nouveau projet de manga"""
    
    project = Project(
        user_id=current_user["id"],
        title=project_data.title,
        synopsis=project_data.synopsis,
        style=project_data.style,
        generation_params=project_data.generation_params or {}
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return project

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Liste les projets de l'utilisateur"""
    
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user["id"])
        .order_by(Project.updated_at.desc())
    )
    projects = result.scalars().all()
    
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Récupère un projet spécifique"""
    
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if str(project.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    updates: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Met à jour un projet"""
    
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if str(project.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return project

@router.delete("/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Supprime un projet"""
    
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if str(project.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    await db.delete(project)
    await db.commit()
    
    return {"message": "Project deleted successfully"}
