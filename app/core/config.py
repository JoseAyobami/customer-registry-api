from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()



















# import logging
# from functools import lru_cache
# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     """Application configuration from environment variables."""
    
#     DATABASE_URL: str = "sqlite:///./customers.db"
#     LOG_LEVEL: str = "INFO"
#     ENV: str = "development"
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False


# @lru_cache()
# def get_settings() -> Settings:
#     """Get cached settings instance."""
#     return Settings()


# def setup_logging(log_level: str = "INFO") -> None:
#     """Configure structured logging for the application."""
#     logging.basicConfig(
#         level=log_level,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     )

