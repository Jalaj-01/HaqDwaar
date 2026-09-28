"""Configuration management for the LexiLaw backend."""

from pathlib import Path
from typing import List, Optional, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute paths resolved relative to the backend directory, never current working directory
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LEGAL_PROVISIONS_PATH = DATA_DIR / "legal_provisions.json"
LEGAL_TERMS_PATH = DATA_DIR / "legal_terms.json"
CASE_DOCS_DIR = DATA_DIR / "case_documents"
TESTS_DIR = BASE_DIR / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8000
    environment: str = "development"
    cors_origins: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Model settings
    spacy_model: str = "en_core_web_sm"
    semantic_model_name_or_path: str = "all-MiniLM-L6-v2"
    disable_semantic_model: bool = False

    # Constraints and limits
    max_text_length: int = 20000
    max_top_k: int = 20
    default_top_k: int = 5
    max_pdf_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    max_pdf_pages: int = 50
    max_request_body_bytes: int = 15 * 1024 * 1024  # 15 MB

    # Security & Rate Limiting
    enable_rate_limiting: bool = True
    rate_limit_analyze: int = 30  # requests per window
    rate_limit_transform: int = 30
    rate_limit_case_analysis: int = 20
    rate_limit_extract: int = 15
    rate_limit_term_lookup: int = 60
    rate_limit_window_seconds: int = 60

    # Optional API Key for protected deployments (None = open for academic demo)
    api_key: Optional[str] = None

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def validate_production_cors(self) -> "Settings":
        """In production, prohibit unrestricted wildcards with credentials."""
        if self.environment == "production":
            origins = self.cors_origins if isinstance(self.cors_origins, list) else [self.cors_origins]
            if "*" in origins:
                raise ValueError(
                    "Production configuration error: Wildcard CORS origin '*' is not permitted "
                    "when credentials are enabled. Please specify exact domain origins."
                )
        return self


settings = Settings()
