import httpx

from app.config import settings

OBJECT_NAME = "resume.pdf"


def _object_url() -> str:
    return f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{OBJECT_NAME}"


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}


def upload_pdf(path) -> None:
    """Sube (o reemplaza) el PDF del archivo local `path` al bucket."""
    with open(path, "rb") as f:
        r = httpx.post(
            _object_url(),
            headers={**_auth_headers(), "Content-Type": "application/pdf", "x-upsert": "true"},
            content=f.read(),
            timeout=30,
        )
    r.raise_for_status()


def download_pdf() -> bytes | None:
    """Devuelve los bytes del PDF, o None si todavía no existe."""
    r = httpx.get(_object_url(), headers=_auth_headers(), timeout=30)
    if r.status_code in (400, 404):
        return None
    r.raise_for_status()
    return r.content


def public_image_url(name: str) -> str:
    return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_IMAGES_BUCKET}/{name}"


def upload_image(name: str, content: bytes, content_type: str) -> str:
    """Sube una imagen al bucket público y devuelve su URL pública."""
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_IMAGES_BUCKET}/{name}"
    r = httpx.post(
        url,
        headers={**_auth_headers(), "Content-Type": content_type, "x-upsert": "true"},
        content=content,
        timeout=30,
    )
    r.raise_for_status()
    return public_image_url(name)
