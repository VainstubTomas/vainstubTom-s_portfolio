from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_KEY: str
    DATABASE_URL: str = "sqlite:///./portfolio.db"
    CORS_ORIGINS: list[str] = []
    MAX_PDF_MB: int = 5
    RESUME_PATH: str = "storage/resume.pdf"
    STORAGE_BACKEND: str = "supabase"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_BUCKET: str = "resume"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
