import httpx
import pytest

from app import storage
from app.config import settings


@pytest.fixture(autouse=True)
def supabase_settings(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://abc.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_SERVICE_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "SUPABASE_BUCKET", "resume")


def fake_response(status_code, content=b""):
    request = httpx.Request("GET", "https://abc.supabase.co")
    return httpx.Response(status_code, content=content, request=request)


def test_upload_pdf_sends_expected_request(tmp_path, monkeypatch):
    pdf = tmp_path / "cv.pdf"
    pdf.write_bytes(b"%PDF-1.4 hola")
    sent = {}

    def fake_post(url, headers, content, timeout):
        sent.update(url=url, headers=headers, content=content)
        return fake_response(200)

    monkeypatch.setattr(storage.httpx, "post", fake_post)
    storage.upload_pdf(pdf)

    assert sent["url"] == "https://abc.supabase.co/storage/v1/object/resume/resume.pdf"
    assert sent["headers"]["Authorization"] == "Bearer clave-de-prueba"
    assert sent["headers"]["x-upsert"] == "true"
    assert sent["headers"]["Content-Type"] == "application/pdf"
    assert sent["content"] == b"%PDF-1.4 hola"


def test_upload_pdf_raises_on_error(tmp_path, monkeypatch):
    pdf = tmp_path / "cv.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(storage.httpx, "post", lambda *a, **k: fake_response(403))
    with pytest.raises(httpx.HTTPStatusError):
        storage.upload_pdf(pdf)


def test_download_pdf_returns_bytes(monkeypatch):
    monkeypatch.setattr(storage.httpx, "get", lambda *a, **k: fake_response(200, b"%PDF-1.4 x"))
    assert storage.download_pdf() == b"%PDF-1.4 x"


@pytest.mark.parametrize("status", [400, 404])
def test_download_pdf_missing_returns_none(monkeypatch, status):
    monkeypatch.setattr(storage.httpx, "get", lambda *a, **k: fake_response(status))
    assert storage.download_pdf() is None


def test_download_pdf_raises_on_server_error(monkeypatch):
    monkeypatch.setattr(storage.httpx, "get", lambda *a, **k: fake_response(500))
    with pytest.raises(httpx.HTTPStatusError):
        storage.download_pdf()
