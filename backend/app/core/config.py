import os

from pydantic_settings import BaseSettings

# Lấy thư mục gốc của dự án (thư mục backend/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    # OpenRouter
    OPENROUTER_KEY: str = ""
    OPENROUTER_URL: str = "https://openrouter.ai/api/v1"

    # Models
    LOW_MODEL: str  = "anthropic/claude-haiku-4-5"
    HIGH_MODEL: str = "anthropic/claude-sonnet-4-5"

    # Database — Dùng đường dẫn tuyệt đối để tránh nhầm lẫn CWD
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'data', 'app.db')}"

    # App
    APP_NAME: str = "TechScout"
    APP_URL: str  = "http://localhost:8000"
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    WEB_CONTENT_MAX_LENGTH: int = 5000

    # Discord Webhooks
    DISCORD_WEBHOOK_RAW_FEED:          str = ""
    DISCORD_WEBHOOK_MARKET_SIGNALS:    str = ""
    DISCORD_WEBHOOK_STRATEGIC_REPORTS: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Đảm bảo DATABASE_URL luôn là đường dẫn tuyệt đối trỏ tới backend/data/app.db để tránh nhầm lẫn CWD
if "sqlite" in settings.DATABASE_URL:
    settings.DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'data', 'app.db')}"

