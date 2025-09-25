from fastapi import FastAPI

from .app import get_app

# PUBLIC_INTERFACE
def app_factory() -> FastAPI:
    """Return the configured FastAPI app (for ASGI servers)."""
    return get_app()


# Instantiate for uvicorn discovery: `uvicorn src.api.main:app`
app = get_app()
