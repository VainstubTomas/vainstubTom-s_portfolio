from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime

class ProjectCreate(BaseModel):
    title_es: str = Field(min_length=1, max_length=100)
    title_en: str = Field(min_length=1, max_length=100)
    title_pr: str = Field(min_length=1, max_length=100)
    description_es: str = Field(min_length=1, max_length=300)
    description_en: str = Field(min_length=1, max_length=300)
    description_pr: str = Field(min_length=1, max_length=300)
    link: HttpUrl | None = None
    github: HttpUrl | None = None
    image: str | None = None
    tags: list[str] = Field(default_factory=list)

class ProjectUpdate(BaseModel):
    title_es: str | None = Field(default=None, min_length=1, max_length=100)
    title_en: str | None = Field(default=None, min_length=1, max_length=100)
    title_pr: str | None = Field(default=None, min_length=1, max_length=100)
    description_es: str | None = Field(default=None, min_length=1, max_length=300)
    description_en: str | None = Field(default=None, min_length=1, max_length=300)
    description_pr: str | None = Field(default=None, min_length=1, max_length=300)
    link: HttpUrl | None = None
    github: HttpUrl | None = None
    image: str | None = None
    tags: list[str] | None = None

class ProjectOut(BaseModel):
    id: int
    title_es: str
    title_en: str
    title_pr: str
    description_es: str
    description_en: str
    description_pr: str
    link: str | None
    github: str | None
    image: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
