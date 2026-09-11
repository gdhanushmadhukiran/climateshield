"""ClimateShield Backend Configuration."""

from typing import List, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    PROJECT_NAME: str = "ClimateShield API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./climateshield_dev.db"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "climateshield"
    POSTGRES_USER: str = "climateshield"
    POSTGRES_PASSWORD: str = "climateshield"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        elif isinstance(v, list):
            return v
        return ["*"]

    # Health Simulation Overrides
    RISK_SERVICE_STATUS: str = "HEALTHY"
    WEATHER_SERVICE_STATUS: str = "HEALTHY"
    IOT_SERVICE_STATUS: str = "HEALTHY"
    GIS_SERVICE_STATUS: str = "HEALTHY"

    # MQTT Ingestion Configuration
    MQTT_BROKER_HOST: str = "127.0.0.1"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_TOPIC_PREFIX: str = "climateshield/v1"
    MQTT_CLIENT_ID: str = "climateshield-backend-worker"

    # Sensor Freshness and Health Thresholds (in minutes)
    SENSOR_FRESH_MINUTES: int = 5
    SENSOR_AGING_MINUTES: int = 15
    SENSOR_STALE_MINUTES: int = 30
    SENSOR_OFFLINE_MINUTES: int = 60

    # Rate limiting & bounds
    TELEMETRY_RATE_LIMIT: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
