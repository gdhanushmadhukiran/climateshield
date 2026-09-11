"""Telemetry ingestion and SSE event schemas."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TelemetryPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message_id: str = Field(..., description="Unique message UUID for deduplication")
    node_code: str = Field(..., description="Sensor node code, e.g. RN-01, RIV-UP-01")
    timestamp: datetime = Field(..., description="Timezone-aware observation timestamp in UTC")

    water_level_m: Optional[float] = Field(None, description="Water level in meters (>= 0)")
    rainfall_mm: Optional[float] = Field(None, description="Cumulative rainfall in mm (>= 0)")
    temperature_c: Optional[float] = Field(None, description="Ambient temperature in Celsius (-20 to 70)")

    latitude: Optional[float] = Field(None, description="GPS Latitude (-90 to 90)")
    longitude: Optional[float] = Field(None, description="GPS Longitude (-180 to 180)")

    battery_percent: Optional[int] = Field(None, description="Battery level percent (0 to 100)")
    signal_percent: Optional[int] = Field(None, description="Signal strength percent (0 to 100)")

    battery_voltage: Optional[float] = Field(None, description="Direct hardware battery voltage in Volts")
    signal_dbm: Optional[float] = Field(None, description="Direct wireless RSSI signal in dBm")
    rate_of_change_temp: Optional[float] = Field(None, description="Temperature derivative")
    reading_stuck_count: Optional[int] = Field(None, description="Count of consecutive stuck readings")

    is_simulated: bool = Field(False, description="Explicit flag indicating simulated telemetry")


    @field_validator("timestamp")
    @classmethod
    def validate_utc_timestamp(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            # Assume UTC if naive
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    @field_validator("water_level_m")
    @classmethod
    def validate_water_level(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0.0:
            raise ValueError("water_level_m must be non-negative (>= 0.0)")
        return v

    @field_validator("rainfall_mm")
    @classmethod
    def validate_rainfall(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0.0:
            raise ValueError("rainfall_mm must be non-negative (>= 0.0)")
        return v

    @field_validator("temperature_c")
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-20.0 <= v <= 70.0):
            raise ValueError("temperature_c must be within physical range [-20.0, 70.0]")
        return v

    @field_validator("battery_percent", "signal_percent")
    @classmethod
    def validate_percentages(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (0 <= v <= 100):
            raise ValueError("Percentage must be within [0, 100]")
        return v

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-90.0 <= v <= 90.0):
            raise ValueError("latitude must be within [-90.0, 90.0]")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-180.0 <= v <= 180.0):
            raise ValueError("longitude must be within [-180.0, 180.0]")
        return v


class TelemetryIngestResponse(BaseModel):
    status: str = "success"
    message_id: str
    node_code: str
    deduplicated: bool = False
    observations_persisted: int = 0
    rate_of_rise_m_per_hour: Optional[float] = None
    time_to_threshold_minutes: Optional[float] = None
    quality: str = "VALID"
    received_at: str
    is_anomaly: Optional[bool] = None
    anomaly_score: Optional[float] = None
    ml_model_version: Optional[str] = None
    ml_inference_latency_ms: Optional[float] = None


class RiverUpdateEvent(BaseModel):
    nodeCode: str
    segment: str
    waterLevelM: float
    thresholdM: float
    rateOfRiseMPerHour: float
    timeToThresholdMinutes: Optional[float] = None
    status: str
    dataQuality: str
    isSimulated: bool = False
    timestamp: str


class SensorStatusEvent(BaseModel):
    nodeCode: str
    status: str
    batteryPercent: int
    signalPercent: int
    lastPacketAt: str


class RiskTriggerEvent(BaseModel):
    zoneId: str
    reason: str
    nodeCode: str
    timestamp: str
