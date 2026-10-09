from datetime import datetime, timezone
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

def utcnow(): return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_es: Mapped[str]
    title_en: Mapped[str]
    title_pr: Mapped[str]
    description_es: Mapped[str]
    description_en: Mapped[str]
    description_pr: Mapped[str]
    link: Mapped[str | None]
    github: Mapped[str | None]
    image: Mapped[str | None]
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
