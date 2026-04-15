from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class City(Base):
    __tablename__ = "cities"
    __table_args__ = (UniqueConstraint("name", "country_code", name="uq_city_name_country"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    country_code: Mapped[str] = mapped_column(String(2), default="GB")
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    records: Mapped[list["UrbanClimateRecord"]] = relationship(
        back_populates="city",
        cascade="all, delete-orphan",
    )


class UrbanClimateRecord(Base):
    __tablename__ = "urban_climate_records"
    __table_args__ = (UniqueConstraint("city_id", "record_date", name="uq_city_record_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"), index=True)
    record_date: Mapped[date] = mapped_column(Date, index=True)
    temperature_max_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_min_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_sum_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_speed_max_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pm2_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    pm10: Mapped[float | None] = mapped_column(Float, nullable=True)
    nitrogen_dioxide: Mapped[float | None] = mapped_column(Float, nullable=True)
    ozone: Mapped[float | None] = mapped_column(Float, nullable=True)
    european_aqi: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    city: Mapped[City] = relationship(back_populates="records")

