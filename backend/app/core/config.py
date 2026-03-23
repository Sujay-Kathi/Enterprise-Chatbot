"""Application configuration using Pydantic Settings v2."""

from functools import lru_cache
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # NVIDIA NIM
    nvidia_api_key: str = ""
    nim_model: str = "meta/llama-3.1-8b-instruct"

    # JWT
    jwt_secret_key: str = "dev-secret-change-in-production-please"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Email / OTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    otp_expire_minutes: int = 10

    # FastAPI
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:8501"

    # Streamlit
    backend_url: str = "http://localhost:8000"

    # FAISS & Embeddings
    faiss_index_path: str = "./data/faiss_index"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Hybrid RAG+CAG
    raw_docs_path: str = "./data/raw_documents"
    cache_registry_path: str = "./data/cache_registry.json"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
