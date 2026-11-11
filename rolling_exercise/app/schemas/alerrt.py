from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class AlertResponse(BaseModel):
    id: int
    date: date
    city: str
    aqi: int = Field(gt=300, le=500)

    model_config = ConfigDict(from_attributes=True)