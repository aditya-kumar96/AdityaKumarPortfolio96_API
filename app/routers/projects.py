from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Literal

from app.db.session import get_db
from app.models.project import Project
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    featured: bool | None = None,
    search: str | None = Query(default=None, min_length=1, max_length=150),
    sort_by: Literal["title", "id", "featured"] | None = None,
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db)
):
    return project_service.get_all_published_projects(
        db=db, 
        skip=skip, 
        limit=limit,
        featured=featured,
        search=search,
        sort_by=sort_by,
        order=order
        )


@router.get("/{slug}", response_model=ProjectResponse)
def get_project_by_slug(slug: str, db: Session = Depends(get_db)):
    project = project_service.get_project_by_slug(db, slug)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Project not found"
        )
    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db, project_data)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int, project_data: ProjectUpdate, db: Session = Depends(get_db)
):
    return project_service.update_project(db, project_id, project_data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project_service.delete_project(db, project_id)
