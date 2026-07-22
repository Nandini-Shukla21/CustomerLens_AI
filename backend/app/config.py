from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    app_name: str = Field(default=os.getenv("APP_NAME", "CustomerLens AI Backend"))
    app_version: str = Field(default=os.getenv("APP_VERSION", "0.1.0"))
    debug: bool = Field(default=os.getenv("DEBUG", "false").lower() == "true")
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    postgres_url: str = Field(
        default=os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/customerlens")
    )
    upload_dir: str = Field(default=os.getenv("UPLOAD_DIR", "./uploads"))
    vector_store_path: str = Field(default=os.getenv("VECTOR_STORE_PATH", "./vector_store"))
    groq_api_key: str = Field(default=os.getenv("GROQ_API_KEY", ""))
    groq_model: str = Field(default=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"))

    class Config:
        extra = "ignore"


settings = Settings()
