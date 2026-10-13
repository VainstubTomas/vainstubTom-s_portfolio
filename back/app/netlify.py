import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def trigger_rebuild() -> None:
    """Avisa a Netlify que reconstruya el sitio. Nunca lanza: corre en segundo plano
    y la escritura que lo disparó ya quedó guardada."""
    if not settings.NETLIFY_BUILD_HOOK_URL:
        return
    try:
        httpx.post(settings.NETLIFY_BUILD_HOOK_URL, timeout=10).raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("No se pudo disparar el build de Netlify: %s", exc)
