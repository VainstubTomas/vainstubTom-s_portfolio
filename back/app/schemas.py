from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime

class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=300)
    link: HttpUrl | None = None
    github: HttpUrl | None = None
    image: str | None = None
    tags: list[str] = Field(default_factory=list)

class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=300)
    link: HttpUrl | None = None
    github: HttpUrl | None = None
    image: str | None = None
    tags: list[str] | None = None

class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    link: str | None
    github: str | None
    image: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
