import httpx

import app.netlify as netlify_module
from app.config import settings

PROJECT = {
    "title_es": "t", "title_en": "t", "title_pr": "t",
    "description_es": "d", "description_en": "d", "description_pr": "d",
    "image": "/projects/x.webp", "tags": ["Astro"],
}


def test_rebuild_se_dispara_tras_escribir(client, auth, monkeypatch):
    llamadas = []
    monkeypatch.setattr(settings, "NETLIFY_BUILD_HOOK_URL", "https://hook.test/abc")
    monkeypatch.setattr(
        netlify_module.httpx, "post",
        lambda url, **kw: llamadas.append(url) or httpx.Response(200, request=httpx.Request("POST", url)),
    )
    r = client.post("/projects/", json=PROJECT, headers=auth)
    assert r.status_code == 201
    assert llamadas == ["https://hook.test/abc"]


def test_sin_hook_configurado_no_llama_a_nadie(client, auth, monkeypatch):
    monkeypatch.setattr(settings, "NETLIFY_BUILD_HOOK_URL", "")
    def boom(*a, **kw):
        raise AssertionError("no debería llamar")
    monkeypatch.setattr(netlify_module.httpx, "post", boom)
    assert client.post("/projects/", json=PROJECT, headers=auth).status_code == 201


def test_si_netlify_falla_la_escritura_sigue_ok(client, auth, monkeypatch):
    monkeypatch.setattr(settings, "NETLIFY_BUILD_HOOK_URL", "https://hook.test/abc")
    def falla(*a, **kw):
        raise httpx.ConnectError("sin red")
    monkeypatch.setattr(netlify_module.httpx, "post", falla)
    assert client.post("/projects/", json=PROJECT, headers=auth).status_code == 201
