"""Platform-level probes exposed at root; diagnostic API health stays under /api/health/*."""

from fastapi import APIRouter

router = APIRouter(tags=["readiness"])


@router.get("/healthz", summary="Liveness probe for Azure")
async def healthz():
    return {"ok": True}


@router.get("/readyz", summary="Readiness probe for Azure")
async def readyz():
    """Lightweight readiness probe; full DB check remains at /api/health/db."""
    return {"ok": True}
