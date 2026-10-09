from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.security import verify_api_key

router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, deatils="Proyecto no encontrado")
    return project

@router.post(
    "/", 
    response_model=ProjectOut, 
    status_code=201,
    dependencies=[Depends(verify_api_key)],
)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        title=payload.title,
        description=payload.description,
        link=str(payload.link) if payload.link else None,
        github=str(payload.github) if payload.link else None,
        image=payload.image,
        tags=payload.tags
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
