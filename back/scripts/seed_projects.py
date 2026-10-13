"""Carga única: migra los proyectos hardcodeados del front a la API.

Lee títulos y descripciones de los i18n del front (es/en/pr) y publica cada
proyecto con POST /projects/. Es idempotente: si ya existe un proyecto con el
mismo title_es, lo saltea.

Uso, desde back/ con el venv activo:

    # validar sin tocar la red
    python scripts/seed_projects.py --dry-run

    # cargar en la API (la clave se pide sin mostrarla)
    read -s "API_KEY?API key: "; export API_KEY
    API_URL=https://<tu-servicio>.onrender.com python scripts/seed_projects.py
"""
import json
import os
import sys
from pathlib import Path

import httpx

BACK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACK))
from app.schemas import ProjectCreate  # noqa: E402

I18N = BACK.parent / "front" / "src" / "i18n"
LANGS = ("es", "en", "pr")

# Lo que no vive en los i18n: replica el array PROJECTS de Projects.astro.
# Los tags usan los nombres exactos del diccionario TAGS del front.
EXTRA = {
    1: {
        "link": None,
        "github": "https://github.com/VainstubTomas/vainstubTom-s_portfolio.git",
        "image": "/projects/portfolio.webp",
        "tags": ["Astro", "Tailwind CSS"],
    },
    2: {
        "link": None,
        "github": None,
        "image": "/projects/trainer.webp",
        "tags": ["React", "Tailwind CSS", "TypeScript"],
    },
    3: {
        "link": None,
        "github": "https://github.com/VainstubTomas/Trabajo_Protocolos_Comunicacion_Industrial.git",
        "image": "/projects/pci.webp",
        "tags": ["Python", "C++", "JavaScript"],
    },
    4: {
        "link": "https://ivolutionx.com/",
        "github": None,
        "image": "/projects/ivolutionX.webp",
        "tags": ["Next.js", "React"],
    },
}


def build_payloads() -> list[dict]:
    texts = {
        lang: json.loads((I18N / lang / f"{lang}.json").read_text(encoding="utf-8"))
        for lang in LANGS
    }
    payloads = []
    for n, extra in EXTRA.items():
        payload = dict(extra)
        for lang in LANGS:
            payload[f"title_{lang}"] = texts[lang][f"proyectos.p{n}"]
            payload[f"description_{lang}"] = texts[lang][f"proyectos.descrip_p{n}"]
        payloads.append(payload)
    return payloads


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    payloads = build_payloads()

    errors = 0
    for p in payloads:
        try:
            ProjectCreate.model_validate(p)
        except Exception as exc:
            errors += 1
            print(f"INVALIDO  {p['title_es']}")
            for e in exc.errors():
                print(f"          {e['loc'][0]}: {e['msg']}")
    if errors:
        print(f"\n{errors} proyecto(s) no pasan el schema. Corregí el schema o los textos.")
        return 1
    print(f"{len(payloads)} proyectos válidos según ProjectCreate.")
    if dry_run:
        return 0

    api_url = os.environ.get("API_URL", "").rstrip("/")
    api_key = os.environ.get("API_KEY", "")
    if not api_url or not api_key:
        print("Faltan las variables API_URL y/o API_KEY.")
        return 1

    headers = {"X-API-Key": api_key}
    # timeout largo: el plan gratuito puede estar dormido (cold start)
    with httpx.Client(base_url=api_url, headers=headers, timeout=120) as client:
        existing = {p["title_es"] for p in client.get("/projects/").raise_for_status().json()}
        for p in payloads:
            if p["title_es"] in existing:
                print(f"saltado   {p['title_es']} (ya existe)")
                continue
            r = client.post("/projects/", json=p)
            r.raise_for_status()
            print(f"creado    id={r.json()['id']}  {p['title_es']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
