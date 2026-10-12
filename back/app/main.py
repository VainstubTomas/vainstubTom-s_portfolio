from fastapi import FastAPI
from app import models
from app.database import Base, engine
from app.routers import projects, resume

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

# Include API routers
app.include_router(projects.router)
app.include_router(resume.router)
