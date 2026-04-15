from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RecordBase(BaseModel):
    city_id: int = Field(gt=0)
    record_date: date
    temperature_max_c: float | None = None
    temperature_min_c: float | None = None
    precipitation_sum_mm: float | None = Field(default=None, ge=0)
    wind_speed_max_kmh: float | None = Field(default=None, ge=0)
    pm2_5: float | None = Field(default=None, ge=0)
    pm10: float | None = Field(default=None, ge=0)
    nitrogen_dioxide: float | None = Field(default=None, ge=0)
    ozone: float | None = Field(default=None, ge=0)
    european_aqi: float | None = Field(default=None, ge=0)
    source: str = Field(default="manual", max_length=100)

    @model_validator(mode="after")
    def validate_temperature_range(self) -> "RecordBase":
        if (
            self.temperature_max_c is not None
            and self.temperature_min_c is not None
            and self.temperature_max_c < self.temperature_min_c
        ):
            raise ValueError("temperature_max_c must be greater than or equal to temperature_min_c")
        return self


class RecordCreate(RecordBase):
    pass


class RecordUpdate(BaseModel):
    temperature_max_c: float | None = None
    temperature_min_c: float | None = None
    precipitation_sum_mm: float | None = Field(default=None, ge=0)
    wind_speed_max_kmh: float | None = Field(default=None, ge=0)
    pm2_5: float | None = Field(default=None, ge=0)
    pm10: float | None = Field(default=None, ge=0)
    nitrogen_dioxide: float | None = Field(default=None, ge=0)
    ozone: float | None = Field(default=None, ge=0)
    european_aqi: float | None = Field(default=None, ge=0)
    source: str | None = Field(default=None, max_length=100)


class RecordRead(RecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ImportRequest(BaseModel):
    start_date: date
    end_date: date
    overwrite_existing: bool = False

    @model_validator(mode="after")
    def validate_date_order(self) -> "ImportRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class ImportResult(BaseModel):
    city_id: int
    city_name: str
    start_date: date
    end_date: date
    imported: int
    skipped: int

