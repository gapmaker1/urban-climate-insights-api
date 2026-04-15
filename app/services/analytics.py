from __future__ import annotations

from datetime import date
from statistics import fmean, pstdev

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.entities import City, UrbanClimateRecord
from app.schemas.analytics import (
    AnomalyPoint,
    AnomalyResponse,
    CityComparisonRow,
    CitySummary,
    HottestDay,
    TrendPoint,
    TrendResponse,
)


def _apply_filters(
    stmt: Select[tuple[UrbanClimateRecord]],
    city_id: int,
    start_date: date | None,
    end_date: date | None,
) -> Select[tuple[UrbanClimateRecord]]:
    stmt = stmt.where(UrbanClimateRecord.city_id == city_id)
    if start_date is not None:
        stmt = stmt.where(UrbanClimateRecord.record_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(UrbanClimateRecord.record_date <= end_date)
    return stmt.order_by(UrbanClimateRecord.record_date)


def _fetch_city(session: Session, city_id: int) -> City:
    city = session.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return city


def get_city_records(
    session: Session,
    city_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> tuple[City, list[UrbanClimateRecord]]:
    city = _fetch_city(session, city_id)
    stmt = _apply_filters(select(UrbanClimateRecord), city_id, start_date, end_date)
    records = list(session.scalars(stmt))
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No records found for the requested city and date range",
        )
    return city, records


def _average(values: list[float | None]) -> float | None:
    cleaned = [value for value in values if value is not None]
    return round(fmean(cleaned), 2) if cleaned else None


def _sum(values: list[float | None]) -> float | None:
    cleaned = [value for value in values if value is not None]
    return round(sum(cleaned), 2) if cleaned else None


def build_city_summary(
    session: Session,
    city_id: int,
    start_date: date | None,
    end_date: date | None,
) -> CitySummary:
    city, records = get_city_records(session, city_id, start_date, end_date)
    hottest_record = max(
        (record for record in records if record.temperature_max_c is not None),
        key=lambda record: record.temperature_max_c,
        default=None,
    )

    return CitySummary(
        city_id=city.id,
        city_name=city.name,
        start_date=records[0].record_date,
        end_date=records[-1].record_date,
        record_count=len(records),
        avg_temp_max_c=_average([record.temperature_max_c for record in records]),
        avg_temp_min_c=_average([record.temperature_min_c for record in records]),
        total_precipitation_mm=_sum([record.precipitation_sum_mm for record in records]),
        avg_pm2_5=_average([record.pm2_5 for record in records]),
        avg_pm10=_average([record.pm10 for record in records]),
        avg_nitrogen_dioxide=_average([record.nitrogen_dioxide for record in records]),
        avg_ozone=_average([record.ozone for record in records]),
        max_european_aqi=max((record.european_aqi for record in records if record.european_aqi is not None), default=None),
        hottest_day=(
            HottestDay(
                record_date=hottest_record.record_date,
                temperature_max_c=round(hottest_record.temperature_max_c, 2),
            )
            if hottest_record and hottest_record.temperature_max_c is not None
            else None
        ),
    )


def build_city_trend(
    session: Session,
    city_id: int,
    start_date: date | None,
    end_date: date | None,
) -> TrendResponse:
    city, records = get_city_records(session, city_id, start_date, end_date)
    return TrendResponse(
        city_id=city.id,
        city_name=city.name,
        start_date=records[0].record_date,
        end_date=records[-1].record_date,
        points=[
            TrendPoint(
                record_date=record.record_date,
                temperature_max_c=record.temperature_max_c,
                pm2_5=record.pm2_5,
                european_aqi=record.european_aqi,
            )
            for record in records
        ],
    )


def build_city_comparison(
    session: Session,
    city_ids: list[int],
    start_date: date | None,
    end_date: date | None,
) -> list[CityComparisonRow]:
    if not city_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one city_id must be provided")

    comparison_rows: list[CityComparisonRow] = []
    for city_id in city_ids:
        city, records = get_city_records(session, city_id, start_date, end_date)
        comparison_rows.append(
            CityComparisonRow(
                city_id=city.id,
                city_name=city.name,
                avg_temp_max_c=_average([record.temperature_max_c for record in records]),
                avg_pm2_5=_average([record.pm2_5 for record in records]),
                total_precipitation_mm=_sum([record.precipitation_sum_mm for record in records]),
                max_european_aqi=max(
                    (record.european_aqi for record in records if record.european_aqi is not None),
                    default=None,
                ),
            )
        )
    return comparison_rows


def detect_anomalies(
    session: Session,
    city_id: int,
    metric: str,
    threshold: float,
    start_date: date | None,
    end_date: date | None,
) -> AnomalyResponse:
    metric_map = {
        "temperature_max_c": "temperature_max_c",
        "precipitation_sum_mm": "precipitation_sum_mm",
        "pm2_5": "pm2_5",
        "european_aqi": "european_aqi",
    }
    if metric not in metric_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported metric '{metric}'",
        )

    city, records = get_city_records(session, city_id, start_date, end_date)
    values = [getattr(record, metric_map[metric]) for record in records if getattr(record, metric_map[metric]) is not None]
    if not values:
        return AnomalyResponse(
            city_id=city.id,
            city_name=city.name,
            metric=metric,
            threshold=threshold,
            mean=None,
            standard_deviation=None,
            anomalies=[],
        )

    mean_value = fmean(values)
    std_dev = pstdev(values) if len(values) > 1 else 0.0
    if std_dev == 0:
        return AnomalyResponse(
            city_id=city.id,
            city_name=city.name,
            metric=metric,
            threshold=threshold,
            mean=round(mean_value, 2),
            standard_deviation=0.0,
            anomalies=[],
        )

    anomalies: list[AnomalyPoint] = []
    for record in records:
        value = getattr(record, metric_map[metric])
        if value is None:
            continue
        deviation = value - mean_value
        z_score = deviation / std_dev
        if abs(z_score) >= threshold:
            anomalies.append(
                AnomalyPoint(
                    record_date=record.record_date,
                    value=round(value, 2),
                    deviation=round(deviation, 2),
                    z_score=round(z_score, 2),
                )
            )

    anomalies.sort(key=lambda item: abs(item.z_score), reverse=True)
    return AnomalyResponse(
        city_id=city.id,
        city_name=city.name,
        metric=metric,
        threshold=threshold,
        mean=round(mean_value, 2),
        standard_deviation=round(std_dev, 2),
        anomalies=anomalies,
    )

