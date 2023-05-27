from fastapi import FastAPI
from mangum import Mangum

from backend.apps.api.routers import bookings

app = FastAPI()
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
handler = Mangum(app, lifespan="off")
