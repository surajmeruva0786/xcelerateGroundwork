from functools import lru_cache
from typing import List

from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Use a .env file in development and real environment variables in production.
    """

    # FastAPI
    PROJECT_NAME: str = "Industrial Land Compliance Monitoring"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field("csidc_industrial", env="POSTGRES_DB")
    POSTGRES_USER: str = Field("csidc_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("csidc_password", env="POSTGRES_PASSWORD")

    # Google Earth Engine / GCP (optional - can be set up later)
    GEE_SERVICE_ACCOUNT: str = Field("", env="GEE_SERVICE_ACCOUNT")
    GEE_PRIVATE_KEY_PATH: str = Field("", env="GEE_PRIVATE_KEY_PATH")

    # Scheduler
    ANALYSIS_CRON: str = Field("0 3 1 * *", env="ANALYSIS_CRON")  # 1st of month at 03:00

    # Security / misc
    SECRET_KEY: str = Field("CHANGE_ME", env="SECRET_KEY")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


