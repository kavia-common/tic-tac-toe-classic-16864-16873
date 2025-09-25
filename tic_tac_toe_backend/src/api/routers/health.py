"""
Health endpoints.
"""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/",
    summary="Health Check",
    description="Returns a simple status payload indicating the service is up.",
    responses={200: {"description": "Service is healthy"}},
)
# PUBLIC_INTERFACE
def health_check():
    """Health check endpoint returning service status."""
    return {"message": "Healthy", "theme": {"primary": "#2563EB", "secondary": "#F59E0B"}}
