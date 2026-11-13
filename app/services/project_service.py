from app.core.logging import logger
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

from app.models.project import Project

# Allowed sorting columns
SORT_COLUMNS = {"title": Project.title, "id": Project.id, "featured": Project.featured}


def get_all_published_projects(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    featured: bool | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    order: str = "asc",
):
    statement = select(Project).where(Project.is_published.is_(True))

    # Filter by feature status
    if featured is not None:
        statement = statement.where(Project.featured.is_(featured))

    # Search by project title
    if search and search.strip():
        statement = statement.where(Project.title.ilike(f"%{search.strip()}%"))

    # Sorting
    if sort_by:
        sort_column = SORT_COLUMNS[sort_by]

        if order == "desc":
            statement = statement.order_by(sort_column.desc())
        else:
            statement = statement.order_by(sort_column.asc())

        # Stable ordering when multiple records have same value
        if sort_by != "id":
            statement = statement.order_by(Project.id.desc())
    else:
        # Preserve the existing default ordering
        statement = statement.order_by(Project.featured.desc(), Project.id.desc())

    # Pagination
    statement = statement.offset(skip).limit(limit)

    return db.scalars(statement).all()


def get_project_by_slug(db: Session, slug: str):
    statement = select(Project).where(
        Project.slug == slug, Project.is_published.is_(True)
    )

    return db.scalars(statement)


def create_project(db: Session, project_data):
    existing_project = db.scalar(
        select(Project).where(Project.slug == project_data.slug)
    )
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with this slug is already exists",
        )

    project = Project(**project_data.model_dump(mode="json"))
    try:
        db.add(project)
        db.commit()
        db.refresh(project)
    except IntegrityError:
        db.rollback()
        logger.warning(
            "Project creation failed due to duplicate slug: %s", project_data.slug
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with this slug is already exists",
        )
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating project")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create Project",
        )
    return project


def update_project(db: Session, project_id: int, project_data):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    update_data = project_data.model_dump(exclude_unset=True, mode="json")

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Field provide for update",
        )

    non_nullable_filed = {"title", "slug", "description", "tech_stack"}

    for field in non_nullable_filed:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"{field} cannot be null",
            )
    if "slug" in update_data:
        existing_project = db.scalar(
            select(Project).where(
                Project.slug == update_data["slug"], Project.id != project_id
            )
        )
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project with this slug already exists",
            )
    try:
        for field, value in update_data.items():
            setattr(project, field, value)

        db.commit()
        db.refresh(project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A database constraint was violated",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update project",
        )
    return project


def delete_project(db: Session, project_id: int):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    try:
        db.delete(project)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete project",
        )
