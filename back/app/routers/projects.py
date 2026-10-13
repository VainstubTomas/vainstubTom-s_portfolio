import uuid

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import storage
from app.config import settings
from app.database import get_db
from app.models import Project
from app.netlify import trigger_rebuild
from app.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.security import verify_api_key

router = APIRouter(prefix="/projects", tags=["projects"])

# content-type -> (extensión, verificador de magic bytes sobre los primeros 12 bytes)
IMAGE_TYPES = {
    "image/webp": (".webp", lambda h: h[:4] == b"RIFF" and h[8:12] == b"WEBP"),
    "image/png": (".png", lambda h: h[:8] == b"\x89PNG\r\n\x1a\n"),
    "image/jpeg": (".jpg", lambda h: h[:3] == b"\xff\xd8\xff"),
}

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
def create_project(payload: ProjectCreate, background: BackgroundTasks, db: Session = Depends(get_db)):
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
    background.add_task(trigger_rebuild)
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
def update_project(project_id: int, payload: ProjectUpdate, background: BackgroundTasks, db: Session = Depends(get_db)):
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
    background.add_task(trigger_rebuild)
    return project

@router.delete(
    "/{project_id}",
    status_code=204,
    dependencies=[Depends(verify_api_key)],
)
def delete_project(project_id: int, background: BackgroundTasks, db: Session = Depends(get_db)):
    project = get_project_or_404(db, project_id)
    db.delete(project)
    db.commit()
    background.add_task(trigger_rebuild)


@router.patch(
    "/{project_id}/image",
    response_model=ProjectOut,
    dependencies=[Depends(verify_api_key)],
)
def upload_project_image(
    project_id: int,
    file: UploadFile,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(db, project_id)

    if settings.STORAGE_BACKEND != "supabase":
        raise HTTPException(status_code=501, detail="Subir imágenes requiere STORAGE_BACKEND=supabase")

    kind = IMAGE_TYPES.get(file.content_type)
    if kind is None:
        raise HTTPException(status_code=415, detail="La imagen debe ser WebP, PNG o JPEG")
    extension, has_valid_header = kind

    max_bytes = settings.MAX_IMAGE_MB * 1024 * 1024
    content = file.file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"La imagen supera {settings.MAX_IMAGE_MB} MB")
    if not has_valid_header(content[:12]):
        raise HTTPException(status_code=400, detail="El archivo no es una imagen válida")

    name = f"project-{project_id}-{uuid.uuid4().hex[:8]}{extension}"
    try:
        project.image = storage.upload_image(name, content, file.content_type)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="No se pudo guardar la imagen en el almacenamiento")

    db.commit()
    db.refresh(project)
    background.add_task(trigger_rebuild)
    return project
