from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytics import AnomalyResponse, CityComparisonRow, CitySummary, TrendResponse
from app.services.analytics import build_city_comparison, build_city_summary, build_city_trend, detect_anomalies

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/cities/{city_id}/summary", response_model=CitySummary)
def get_city_summary(
    city_id: int,
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
) -> CitySummary:
    return build_city_summary(db, city_id, start_date, end_date)


@router.get("/cities/{city_id}/trend", response_model=TrendResponse)
def get_city_trend(
    city_id: int,
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
) -> TrendResponse:
    return build_city_trend(db, city_id, start_date, end_date)


@router.get("/compare", response_model=list[CityComparisonRow])
def compare_cities(
    db: Annotated[Session, Depends(get_db)],
    city_ids: Annotated[list[int], Query(..., description="Provide the city_id query parameter multiple times.")],
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[CityComparisonRow]:
    return build_city_comparison(db, city_ids, start_date, end_date)


@router.get("/cities/{city_id}/anomalies", response_model=AnomalyResponse)
def get_city_anomalies(
    city_id: int,
    db: Annotated[Session, Depends(get_db)],
    metric: str = Query(default="temperature_max_c"),
    threshold: float = Query(default=1.5, ge=0.5, le=5.0),
    start_date: date | None = None,
    end_date: date | None = None,
) -> AnomalyResponse:
    return detect_anomalies(db, city_id, metric, threshold, start_date, end_date)
