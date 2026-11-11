from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class AirQualityBase(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    date: date
    pm25: float = Field(ge=0)
    no2: float = Field(ge=0)
    co2: float = Field(ge=0)


class AirQualityCreate(AirQualityBase):
    aqi: int = Field(ge=0, le=500)
    aqi_level: str


class AirQualityResponse(AirQualityCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)