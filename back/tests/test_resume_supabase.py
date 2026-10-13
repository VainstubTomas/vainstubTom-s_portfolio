import httpx
import pytest

import app.routers.resume as resume_router
from app import storage
from app.config import settings

PDF = b"%PDF-1.4\n" + b"contenido" * 10


@pytest.fixture
def bucket(client, monkeypatch):
    """Modo supabase con un bucket falso en memoria (no hay red)."""
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "supabase")
    state = {"pdf": None, "fail": False}

    def fake_upload(path):
        if state["fail"]:
            raise httpx.ConnectError("sin red")
        with open(path, "rb") as f:
            state["pdf"] = f.read()

    def fake_download():
        if state["fail"]:
            raise httpx.ConnectError("sin red")
        return state["pdf"]

    monkeypatch.setattr(storage, "upload_pdf", fake_upload)
    monkeypatch.setattr(storage, "download_pdf", fake_download)
    return state


def upload(client, auth, content=PDF, content_type="application/pdf"):
    return client.patch(
        "/resume", headers=auth, files={"file": ("cv.pdf", content, content_type)}
    )


def test_upload_goes_to_bucket_not_local_disk(client, auth, bucket):
    assert upload(client, auth).status_code == 200
    assert bucket["pdf"] == PDF
    assert not resume_router.RESUME_PATH.exists()


def test_upload_leaves_no_tmp_file(client, auth, bucket):
    upload(client, auth)
    parent = resume_router.RESUME_PATH.parent
    assert not parent.exists() or list(parent.iterdir()) == []


def test_get_returns_pdf_from_bucket(client, bucket):
    bucket["pdf"] = PDF
    r = client.get("/resume")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content == PDF


def test_get_without_pdf_in_bucket_is_404(client, bucket):
    assert client.get("/resume").status_code == 404


def test_upload_replaces_pdf_in_bucket(client, auth, bucket):
    upload(client, auth)
    nuevo = b"%PDF-1.7\nnuevo"
    upload(client, auth, content=nuevo)
    assert client.get("/resume").content == nuevo


def test_validations_still_apply(client, auth, bucket):
    assert upload(client, auth, content_type="text/plain").status_code == 415
    assert upload(client, auth, content=b"no es pdf").status_code == 400
    assert bucket["pdf"] is None


def test_upload_without_key_is_401(client, bucket):
    r = client.patch("/resume", files={"file": ("cv.pdf", PDF, "application/pdf")})
    assert r.status_code == 401
    assert bucket["pdf"] is None


def test_storage_failure_on_upload_is_502_and_cleans_tmp(client, auth, bucket):
    bucket["fail"] = True
    assert upload(client, auth).status_code == 502
    parent = resume_router.RESUME_PATH.parent
    assert not parent.exists() or list(parent.iterdir()) == []


def test_storage_failure_on_get_is_502(client, bucket):
    bucket["fail"] = True
    assert client.get("/resume").status_code == 502
