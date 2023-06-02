from fastapi import FastAPI
from mangum import Mangum

from backend.apps.api.routers import bookings
from backend.apps.api.routers import parkinglots
from backend.apps.api.routers import searcher

app = FastAPI()
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(parkinglots.router, prefix="/parkinglots", tags=["parkinglots"])
app.include_router(searcher.router, prefix="/searcher", tags=["searcher"])

handler = Mangum(app, lifespan="off")
