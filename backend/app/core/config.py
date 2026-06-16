"""
Troy Backend — Application Settings
Uses pydantic-settings for type-safe configuration management.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Troy Engineering Copilot"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///data/troy.db"
    DATABASE_ECHO: bool = False  # Log SQL statements

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ── Paths ────────────────────────────────────────────────────
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    OUTPUT_DIR: Path = BASE_DIR / "output"

    # ── Calculation Engine ───────────────────────────────────────
    MAX_CALCULATION_TIME_MS: int = 5000  # 5 second timeout
    DEFAULT_UNIT_SYSTEM: str = "SI"
    DECIMAL_PRECISION: int = 6

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    def ensure_dirs(self) -> None:
        """Create required directories if they don't exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Singleton settings instance
settings = Settings()
