from datetime import date

from pydantic import BaseModel


class HottestDay(BaseModel):
    record_date: date
    temperature_max_c: float


class CitySummary(BaseModel):
    city_id: int
    city_name: str
    start_date: date
    end_date: date
    record_count: int
    avg_temp_max_c: float | None
    avg_temp_min_c: float | None
    total_precipitation_mm: float | None
    avg_pm2_5: float | None
    avg_pm10: float | None
    avg_nitrogen_dioxide: float | None
    avg_ozone: float | None
    max_european_aqi: float | None
    hottest_day: HottestDay | None


class TrendPoint(BaseModel):
    record_date: date
    temperature_max_c: float | None
    pm2_5: float | None
    european_aqi: float | None


class TrendResponse(BaseModel):
    city_id: int
    city_name: str
    start_date: date
    end_date: date
    points: list[TrendPoint]


class CityComparisonRow(BaseModel):
    city_id: int
    city_name: str
    avg_temp_max_c: float | None
    avg_pm2_5: float | None
    total_precipitation_mm: float | None
    max_european_aqi: float | None


class AnomalyPoint(BaseModel):
    record_date: date
    value: float
    deviation: float
    z_score: float


class AnomalyResponse(BaseModel):
    city_id: int
    city_name: str
    metric: str
    threshold: float
    mean: float | None
    standard_deviation: float | None
    anomalies: list[AnomalyPoint]
