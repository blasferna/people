from pydantic import BaseSettings


class Settings(BaseSettings):
    PEOPLE_DB_URL: str = None
    RUC_DB_URL: str = None

    class Config:
        env_file = ".env"

settings = Settings()
