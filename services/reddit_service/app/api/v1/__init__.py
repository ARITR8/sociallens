# app/api/v1/__init__.py
from fastapi import APIRouter
from .endpoints.fetcher import router as fetcher_router

router = APIRouter()
router.include_router(fetcher_router, prefix="/fetcher", tags=["fetcher"])