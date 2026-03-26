from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
from logging.config import dictConfig
from typing import Any, Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_display_name: str = Field(default="Broker", alias="APP_DISPLAY_NAME")

    app_env: Literal["dev", "staging","prod", "test"] = Field(default="dev", alias="APP_ENV")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v:str)-> str:
        level = v.upper()
        if level not in logging._nameToLevel:
            raise ValueError(f"Invalid log level: {v}")
        return level
    
    database_url:str = Field(default="sqlite:///./app.db",alias = "DATABASE_URL")
    database_connect_timeout: int = Field(default=5, alias = "DATABASE_CONNECT_TIMEOUT")
    auto_create_schema: bool = Field(default=True, alias ="AUTO_CREATE_SCHEMA")
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v:str)-> str:
        value = v.strip()
        if not value:
            raise ValueError("DATABASE_URL must not be empty")
        return value
    
    @field_validator("database_connect_timeout")
    @classmethod
    def validate_database_connect_timeout(cls, v:int)-> int:
        if v<=0:
            raise ValueError("DATABASE_CONNECT_TIMEOUT must be greater than 0")
        return v
    
    jwt_secret_key:str = Field(alias = "JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias = "JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    
settings = Settings()

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def _build_logging_config(level: str) -> dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": LOG_FORMAT, "datefmt": DATE_FORMAT},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {"level": level, "handlers": ["console"]},
    }

def configure_logging(level: str | None = None) -> None:
    """
    Configure application logging. Safe to call multiple times.
    Call once at app startup.
    """
    resolved_level = (level or settings.log_level).upper()
    dictConfig(_build_logging_config(resolved_level))