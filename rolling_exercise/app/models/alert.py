from datetime import date

from sqlalchemy import String, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    city: Mapped[str] = mapped_column(String(100))
    aqi: Mapped[int] = mapped_column(Integer)