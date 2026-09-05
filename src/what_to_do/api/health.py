"""Health check (standard endpoint)."""

from fastapi import APIRouter, status

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "ok"}
