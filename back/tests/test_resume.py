import app.routers.resume as resume_router
from app.config import settings

PDF = b"%PDF-1.4\n" + b"contenido" * 10


def upload(client, auth, content=PDF, content_type="application/pdf", name="cv.pdf"):
    return client.patch(
        "/resume",
        headers=auth,
        files={"file": (name, content, content_type)},
    )


def test_get_without_resume_is_404(client):
    assert client.get("/resume").status_code == 404


def test_upload_valid_pdf_and_get_it_back(client, auth):
    r = upload(client, auth)
    assert r.status_code == 200

    r = client.get("/resume")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content == PDF


def test_upload_replaces_previous_resume(client, auth):
    upload(client, auth)
    nuevo = b"%PDF-1.7\nnuevo"
    assert upload(client, auth, content=nuevo).status_code == 200
    assert client.get("/resume").content == nuevo


def test_upload_leaves_no_tmp_file(client, auth):
    upload(client, auth)
    names = [p.name for p in resume_router.RESUME_PATH.parent.iterdir()]
    assert names == ["resume.pdf"]


def test_upload_without_key_is_401(client):
    r = client.patch(
        "/resume", files={"file": ("cv.pdf", PDF, "application/pdf")}
    )
    assert r.status_code == 401


def test_upload_wrong_content_type_is_415(client, auth):
    r = upload(client, auth, content=b"hola", content_type="text/plain", name="a.txt")
    assert r.status_code == 415


def test_upload_fake_pdf_is_400(client, auth):
    r = upload(client, auth, content=b"esto no es un pdf")
    assert r.status_code == 400
    assert client.get("/resume").status_code == 404


def test_upload_too_big_is_413_and_cleans_up(client, auth, monkeypatch):
    monkeypatch.setattr(settings, "MAX_PDF_MB", 1)
    big = b"%PDF-" + b"x" * (1024 * 1024 + 10)
    r = upload(client, auth, content=big)
    assert r.status_code == 413
    assert not resume_router.RESUME_PATH.exists()
    assert not resume_router.RESUME_PATH.with_suffix(".pdf.tmp").exists()


def test_failed_upload_keeps_previous_resume(client, auth, monkeypatch):
    upload(client, auth)
    monkeypatch.setattr(settings, "MAX_PDF_MB", 1)
    big = b"%PDF-" + b"x" * (1024 * 1024 + 10)
    assert upload(client, auth, content=big).status_code == 413
    assert client.get("/resume").content == PDF
