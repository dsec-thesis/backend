from fastapi import APIRouter
from backend.apps.api.routers.public import parkinglots

router = APIRouter()

router.include_router(parkinglots.router, prefix="/parkinglots", tags=["Parkinglots"])
