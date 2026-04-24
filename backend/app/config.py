import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENROUTER_URL: str = os.getenv("OPENROUTER_URL")
    OPENROUTER_KEY: str = os.getenv("OPENROUTER_KEY")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL")

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    APP_NAME: str = os.getenv("APP_NAME")
    APP_URL: str = os.getenv("APP_URL")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")


settings = Settings()
