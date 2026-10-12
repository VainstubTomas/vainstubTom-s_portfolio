import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.security import verify_api_key

router = APIRouter(prefix="/resume", tags=["resume"])
RESUME_PATH = Path(settings.RESUME_PATH)

@router.patch("", dependencies=[Depends(verify_api_key)])
def replace_resume(file: UploadFile):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="El archivo debe ser un PDF")

    header = file.file.read(5)
    if header != b"%PDF-":
        raise HTTPException(status_code=400, detail="El archivo no es un PDF válido")
    file.file.seek(0)

    return {"detail": "validaciones ok"}


@router.get("")
def get_resume():
    if not RESUME_PATH.exists():
        raise HTTPException(status_code=404, detail="El CV aún no existe")
    return FileResponse(RESUME_PATH, media_type="application/pdf", filename="Vainstub_Tomas_Resume.pdf")