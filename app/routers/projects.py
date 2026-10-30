from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.schemas.project import ProjectResponse


router = APIRouter(prefix="/api/v1/projects",tags=["Projects"])


@router.get("/",response_model=list[ProjectResponse])
def get_projects(db:Session = Depends(get_db)):
    statement=(
        select(Project)
        .where(Project.is_published.is_(True))
        .order_by(Project.featured.desc(),Project.id.desc())
        
    )
    
    return db.scalars(statement).all()


@router.post("/seed", response_model=ProjectResponse)
def seed_project(db: Session = Depends(get_db)):
    existing_project = db.scalar(
        select(Project).where(Project.slug == "stillalive-sos")
    )

    if existing_project:
        raise HTTPException(
            status_code=409,
            detail="Project already exists",
        )

    project = Project(
        title="StillAlive-SOS",
        slug="stillalive-sos",
        description=(
            "A personal safety check-in application "
            "with a React Native mobile app and FastAPI backend."
        ),
        tech_stack="React Native, FastAPI, Python, PostgreSQL",
        github_url="https://github.com/aditya-kumar96/StillAliveSOS_mobile",
        featured=True,
        is_published=True,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project

@router.get("/{slug}",response_model=ProjectResponse)
def get_project_by_slug(
    slug:str,
    db:Session = Depends(get_db)
                        ):
    statement = select(Project).where(
        Project.slug == slug,
        Project.is_published.is_(True)
    )
    
    project = db.scalar(statement)
    
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
        
    return project



