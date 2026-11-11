from sqlalchemy import String, Float, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date

from app.db.database import Base

class AirQuality(Base):
    __tablename__ = "air_quality"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(100))
    date: Mapped[date] = mapped_column(Date)
    pm25: Mapped[float] = mapped_column(Float)
    no2: Mapped[float] = mapped_column(Float)
    co2: Mapped[float] = mapped_column(Float)
    aqi: Mapped[int] = mapped_column(Integer)
    aqi_level: Mapped[str] = mapped_column(String(50))