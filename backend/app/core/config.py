import os

from pydantic_settings import BaseSettings

# Lấy thư mục gốc của dự án (thư mục backend/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    # LLM Provider (OpenAI-compatible)
    LLM_API_KEY: str = ""
    LLM_API_BASE: str = ""

    # Models
    LOW_MODEL: str  = "deepseek-v4-flash-free"
    HIGH_MODEL: str = "deepseek-v4-flash-free"

    # Database — Dùng đường dẫn tuyệt đối để tránh nhầm lẫn CWD
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'data', 'app.db')}"

    # App
    APP_NAME: str = "TechScout"
    APP_URL: str  = "http://localhost:8000"
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    WEB_CONTENT_MAX_LENGTH: int = 5000
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:8000",
    ]

    # Discord Webhooks
    DISCORD_WEBHOOK_RAW_FEED:          str = ""
    DISCORD_WEBHOOK_MARKET_SIGNALS:    str = ""
    DISCORD_WEBHOOK_STRATEGIC_REPORTS: str = ""

    # Pipeline magic numbers
    PIPELINE_INTERVAL_HOURS: int = 4
    HIGH_PRIORITY_SCAN_MINUTES: int = 45
    GATEKEEPER_BATCH_SIZE: int = 10
    REACT_MAX_ITERATIONS: int = 5
    STAGE3_DELAY_SECONDS: int = 5
    LLM_CALL_DELAY: int = 3
    MIN_CONTENT_LENGTH: int = 300
    SCOUT_TIME_WINDOW_HOURS: int = 72

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Đảm bảo DATABASE_URL luôn là đường dẫn tuyệt đối trỏ tới backend/data/app.db để tránh nhầm lẫn CWD
if "sqlite" in settings.DATABASE_URL:
    settings.DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'data', 'app.db')}"

