import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Open Router Config
    OPENROUTER_KEY: str = os.getenv("OPENROUTER_KEY")
    OPENROUTER_URL: str = os.getenv("OPENROUTER_URL")

    # Model
    LOW_MODEL: str = os.getenv("LOW_MODEL")
    HIGH_MODEL: str = os.getenv("HIGH_MODEL")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    APP_NAME: str = os.getenv("APP_NAME")
    APP_URL: str = os.getenv("APP_URL")
    DATA_DIR: str = os.getenv("DATA_DIR", "../../data")

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")
    WEB_CONTENT_MAX_LENGTH: int = 5000


settings = Settings()
