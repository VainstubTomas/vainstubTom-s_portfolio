from fastapi import FastAPI
from app import models
from app.database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}
