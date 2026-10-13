import httpx
import pytest

import app.routers.projects as projects_router
from app.config import settings

PROJECT = {
    "title_es": "t", "title_en": "t", "title_pr": "t",
    "description_es": "d", "description_en": "d", "description_pr": "d",
    "image": "/projects/viejo.webp", "tags": ["Astro"],
}
PNG = b"\x89PNG\r\n\x1a\n" + b"datos"
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 datos"
JPEG = b"\xff\xd8\xff\xe0datos"


@pytest.fixture
def uploads(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "supabase")
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://abc.supabase.co")
    sent = []

    def fake_upload(name, content, content_type):
        sent.append((name, content, content_type))
        return f"https://abc.supabase.co/storage/v1/object/public/projects/{name}"

    monkeypatch.setattr(projects_router.storage, "upload_image", fake_upload)
    return sent


def create(client, auth):
    return client.post("/projects/", json=PROJECT, headers=auth).json()["id"]


@pytest.mark.parametrize("content,mime,ext", [(PNG, "image/png", ".png"), (WEBP, "image/webp", ".webp"), (JPEG, "image/jpeg", ".jpg")])
def test_subir_imagen_guarda_la_url_publica(client, auth, uploads, content, mime, ext):
    pid = create(client, auth)
    r = client.patch(f"/projects/{pid}/image", files={"file": ("x", content, mime)}, headers=auth)
    assert r.status_code == 200
    assert r.json()["image"].startswith("https://abc.supabase.co/storage/v1/object/public/projects/")
    assert r.json()["image"].endswith(ext)
    assert uploads[0][1] == content
    assert client.get(f"/projects/{pid}").json()["image"] == r.json()["image"]


def test_sin_key_da_401(client, auth, uploads):
    pid = create(client, auth)
    assert client.patch(f"/projects/{pid}/image", files={"file": ("x", PNG, "image/png")}).status_code == 401


def test_proyecto_inexistente_da_404(client, auth, uploads):
    assert client.patch("/projects/9999/image", files={"file": ("x", PNG, "image/png")}, headers=auth).status_code == 404


def test_tipo_no_permitido_da_415(client, auth, uploads):
    pid = create(client, auth)
    r = client.patch(f"/projects/{pid}/image", files={"file": ("x.txt", b"hola", "text/plain")}, headers=auth)
    assert r.status_code == 415


def test_imagen_falsa_con_content_type_correcto_da_400(client, auth, uploads):
    pid = create(client, auth)
    r = client.patch(f"/projects/{pid}/image", files={"file": ("x.png", b"no soy png", "image/png")}, headers=auth)
    assert r.status_code == 400
    assert uploads == []


def test_imagen_demasiado_grande_da_413(client, auth, uploads, monkeypatch):
    monkeypatch.setattr(settings, "MAX_IMAGE_MB", 1)
    pid = create(client, auth)
    grande = PNG + b"0" * (1024 * 1024)
    r = client.patch(f"/projects/{pid}/image", files={"file": ("x.png", grande, "image/png")}, headers=auth)
    assert r.status_code == 413


def test_modo_local_da_501(client, auth, monkeypatch):
    pid = create(client, auth)
    r = client.patch(f"/projects/{pid}/image", files={"file": ("x.png", PNG, "image/png")}, headers=auth)
    assert r.status_code == 501


def test_fallo_de_supabase_da_502_y_no_toca_la_imagen(client, auth, uploads, monkeypatch):
    def falla(*a, **k):
        raise httpx.ConnectError("sin red")
    monkeypatch.setattr(projects_router.storage, "upload_image", falla)
    pid = create(client, auth)
    r = client.patch(f"/projects/{pid}/image", files={"file": ("x.png", PNG, "image/png")}, headers=auth)
    assert r.status_code == 502
    assert client.get(f"/projects/{pid}").json()["image"] == "/projects/viejo.webp"
