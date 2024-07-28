import os

from dotenv import load_dotenv
from pydantic import BaseConfig


load_dotenv()


class Settings(BaseConfig):
    # TG BOT CREDS
    TG_TOKEN: str = os.getenv("TG_TOKEN")

    # GOOGLE SHEETS TOKEN
    GGL_SHEET_TOKEN: str = os.getenv("GGL_SHEET_TOKEN")

    # DATABASE
    DATABASE_URL: str = "mongodb://mongo:27017/"

    # REDIS
    REDIS_URL: str = "redis://redis/0"


settings = Settings()
