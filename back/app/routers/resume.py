import os
import httpx
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response

from app import storage
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

    RESUME_PATH.parent.mkdir(exist_ok=True)
    tmp = RESUME_PATH.with_suffix(".pdf.tmp")
    max_bytes = settings.MAX_PDF_MB * 1024 * 1024
    total = 0

    with open(tmp, "wb") as out:
        while chunk := file.file.read(1024 * 1024):
            total += len(chunk)
            if total > max_bytes:
                break
            out.write(chunk)

    if total > max_bytes:
        tmp.unlink()
        raise HTTPException(status_code=413, detail=f"El PDF supera {settings.MAX_PDF_MB} MB")

    try:
        if settings.STORAGE_BACKEND == "supabase":
            storage.upload_pdf(tmp)
        else:
            os.replace(tmp, RESUME_PATH)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="No se pudo guardar el CV en el almacenamiento")
    finally:
        tmp.unlink(missing_ok=True)

    return {"detail": "CV actualizado"}


@router.get("")
def get_resume():
    if settings.STORAGE_BACKEND == "supabase":
        try:
            content = storage.download_pdf()
        except httpx.HTTPError:
            raise HTTPException(status_code=502, detail="No se pudo leer el CV del almacenamiento")
        if content is None:
            raise HTTPException(status_code=404, detail="El CV aún no existe")
        return Response(
            content,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="Vainstub_Tomas_Resume.pdf"'},
        )
    
    if not RESUME_PATH.exists():
        raise HTTPException(status_code=404, detail="El CV aún no existe")
    return FileResponse(RESUME_PATH, media_type="application/pdf", filename="Vainstub_Tomas_Resume.pdf")