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
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project

@router.post(
    "/", 
    response_model=ProjectOut, 
    status_code=201,
    dependencies=[Depends(verify_api_key)],
)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        title_es=payload.title_es,
        title_en=payload.title_en,
        title_pr=payload.title_pr,
        description_es=payload.description_es,
        description_en=payload.description_en,
        description_pr=payload.description_pr,
        link=str(payload.link) if payload.link else None,
        github=str(payload.github) if payload.github else None,
        image=payload.image,
        tags=payload.tags,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    projects = db.scalars(select(Project).order_by(Project.id)).all()
    return projects

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return get_project_or_404(db, project_id)

@router.patch(
    "/{project_id}",
    response_model=ProjectOut,
    dependencies=[Depends(verify_api_key)],
)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        if field in ("link", "github") and value is not None:
            value = str(value)
        if value is None and field not in ("link", "github", "image"):
            raise HTTPException(status_code=422, detail=f"{field} no puede ser null")
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project

@router.delete(
    "/{project_id}",
    status_code=204,
    dependencies=[Depends(verify_api_key)],
)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id)
    db.delete(project)
    db.commit()
