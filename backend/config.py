import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME")
    OPENROUTER_URL: str = os.getenv("OPENROUTER_URL")
    OPENROUTER_KEY: str = os.getenv("OPENROUTER_KEY")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    DATA_DIR: str = "data"

    WEB_CONTENT_MAX_LENGTH: int = 4000


settings = Settings()
