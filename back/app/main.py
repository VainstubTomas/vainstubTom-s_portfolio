from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.config import settings
from app.database import Base, engine
from app.routers import projects, resume

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

# CORS simple config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET"],
)

# Include API routers
app.include_router(projects.router)
app.include_router(resume.router)
