# ──────────────────────────────────────────────
# config.py — Centralised settings loaded from .env
# All modules should import from here, NOT hardcode values
# ──────────────────────────────────────────────

import os
from dotenv import load_dotenv

# Load .env file if present (ignored in production where env vars are set directly)
load_dotenv()


def _require(key: str) -> str:
    """Read a required env var; raise a clear error if it's the example placeholder."""
    val = os.getenv(key, "").strip()
    if not val or val == "CHANGE_ME_USE_A_LONG_RANDOM_STRING":
        raise RuntimeError(
            f"Environment variable '{key}' is not set or is still the placeholder value.\n"
            f"Copy backend/.env.example to backend/.env and set a real value."
        )
    return val


class Settings:
    # ── JWT ───────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "medicore-dev-secret-key-NOT-for-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # ── CORS ──────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:3000").split(",")
        if o.strip()
    ]

    # ── Database ──────────────────────────────
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./medicore.db")

    # ── Environment ───────────────────────────
    APP_ENV: str = os.getenv("APP_ENV", "development")

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    def validate_production(self):
        """Call this at startup in production to ensure insecure defaults are not used."""
        if self.is_production:
            _require("SECRET_KEY")  # Will raise if still the default


settings = Settings()
