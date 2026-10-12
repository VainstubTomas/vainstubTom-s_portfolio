PROJECT = {
    "title_es": "Portfolio",
    "title_en": "Portfolio",
    "title_pr": "Portfolio",
    "description_es": "Mi sitio",
    "description_en": "My site",
    "description_pr": "Meu site",
    "link": "https://example.com",
    "tags": ["Astro", "Tailwind CSS"],
}


def create(client, auth, **overrides):
    return client.post("/projects/", json={**PROJECT, **overrides}, headers=auth)


def test_create_project(client, auth):
    r = create(client, auth)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["title_es"] == "Portfolio"
    assert body["link"].startswith("https://example.com")
    assert body["tags"] == ["Astro", "Tailwind CSS"]


def test_create_without_key_is_401(client):
    assert client.post("/projects/", json=PROJECT).status_code == 401


def test_create_with_wrong_key_is_401(client):
    r = client.post("/projects/", json=PROJECT, headers={"X-API-Key": "incorrecta"})
    assert r.status_code == 401


def test_create_invalid_payload_is_422(client, auth):
    assert create(client, auth, title_es="").status_code == 422
    assert create(client, auth, link="no-es-una-url").status_code == 422
    r = client.post("/projects/", json={"title_es": "solo esto"}, headers=auth)
    assert r.status_code == 422


def test_list_and_get_are_public(client, auth):
    create(client, auth)
    create(client, auth, title_es="Segundo")

    r = client.get("/projects/")
    assert r.status_code == 200
    assert [p["id"] for p in r.json()] == [1, 2]

    r = client.get("/projects/2")
    assert r.status_code == 200
    assert r.json()["title_es"] == "Segundo"


def test_get_missing_is_404(client):
    assert client.get("/projects/9999").status_code == 404


def test_patch_is_partial(client, auth):
    create(client, auth)
    r = client.patch("/projects/1", json={"title_es": "Nuevo"}, headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["title_es"] == "Nuevo"
    assert body["title_en"] == "Portfolio"
    assert body["tags"] == ["Astro", "Tailwind CSS"]
    assert body["link"].startswith("https://example.com")


def test_patch_can_clear_optional_field(client, auth):
    create(client, auth)
    r = client.patch("/projects/1", json={"link": None}, headers=auth)
    assert r.status_code == 200
    assert r.json()["link"] is None


def test_patch_null_required_field_is_422(client, auth):
    create(client, auth)
    r = client.patch("/projects/1", json={"title_es": None}, headers=auth)
    assert r.status_code == 422


def test_patch_without_key_is_401(client, auth):
    create(client, auth)
    assert client.patch("/projects/1", json={"title_es": "X"}).status_code == 401


def test_patch_missing_is_404(client, auth):
    r = client.patch("/projects/9999", json={"title_es": "X"}, headers=auth)
    assert r.status_code == 404


def test_delete_without_key_is_401(client, auth):
    create(client, auth)
    assert client.delete("/projects/1").status_code == 401


def test_delete_missing_is_404(client, auth):
    assert client.delete("/projects/9999", headers=auth).status_code == 404


def test_delete_ok_then_get_is_404(client, auth):
    create(client, auth)
    assert client.delete("/projects/1", headers=auth).status_code == 204
    assert client.get("/projects/1").status_code == 404
