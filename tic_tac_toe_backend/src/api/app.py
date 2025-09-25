"""
FastAPI application setup for Tic Tac Toe backend.

This module assembles the FastAPI app, configures CORS, registers routers,
and sets up OpenAPI metadata following the "Ocean Professional" style guide.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .routers import games
from .routers import health


def _build_openapi_schema(app: FastAPI) -> dict:
    """
    Construct a custom OpenAPI schema with project metadata and tags.
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Tic Tac Toe Classic API",
        version="1.0.0",
        description=(
            "Modern, minimalistic Tic Tac Toe backend with Blue & Amber accents.\n\n"
            "Features:\n"
            "- Create games (player vs player or vs computer)\n"
            "- Make moves and auto-respond with AI when vs computer\n"
            "- Retrieve current game state and outcome\n\n"
            "Style: Ocean Professional — Blue (#2563EB) & Amber (#F59E0B) accents."
        ),
        routes=app.routes,
    )
    schema["tags"] = [
        {
            "name": "Health",
            "description": "Service health and readiness.",
            "x-meta": {"accent": "#2563EB"},
        },
        {
            "name": "Games",
            "description": "Create and play Tic Tac Toe games.",
            "x-meta": {"accent": "#F59E0B"},
        },
    ]
    app.openapi_schema = schema
    return app.openapi_schema


def create_app() -> FastAPI:
    """
    Factory to create the FastAPI application instance.
    """
    app = FastAPI(
        title="Tic Tac Toe Classic API",
        description="A clean, modern FastAPI backend for the classic Tic Tac Toe game.",
        version="1.0.0",
        contact={
            "name": "Tic Tac Toe",
            "url": "https://example.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_tags=[
            {"name": "Health", "description": "Health check endpoints."},
            {"name": "Games", "description": "Game lifecycle and moves."},
        ],
        swagger_ui_parameters={
            "docExpansion": "list",
            "displayRequestDuration": True,
            "syntaxHighlight.theme": "monokai",
            "persistAuthorization": False,
        },
    )

    # CORS configuration - open for demo; refine in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router)
    app.include_router(games.router)

    # Attach custom OpenAPI schema
    app.openapi = lambda: _build_openapi_schema(app)

    return app


# PUBLIC_INTERFACE
def get_app() -> FastAPI:
    """Return a configured FastAPI app instance."""
    return create_app()
