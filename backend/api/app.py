from fastapi import FastAPI

from mangum import Mangum

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Worlds"}

handler = Mangum(app, lifespan="off")
