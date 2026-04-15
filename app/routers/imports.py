from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import City, UrbanClimateRecord, User
from app.schemas.climate import ImportRequest, ImportResult
from app.services.open_meteo import OpenMeteoService

router = APIRouter(prefix="/imports", tags=["Data Import"])


@router.post("/cities/{city_id}/historical", response_model=ImportResult, status_code=status.HTTP_201_CREATED)
async def import_historical_city_data(
    city_id: int,
    payload: ImportRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ImportResult:
    city = db.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    service = OpenMeteoService()
    combined_history = await service.fetch_combined_history(
        latitude=city.latitude,
        longitude=city.longitude,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )

    imported = 0
    skipped = 0
    for day, metrics in combined_history.items():
        record_date = date.fromisoformat(day)
        existing = db.scalar(
            select(UrbanClimateRecord).where(
                UrbanClimateRecord.city_id == city_id,
                UrbanClimateRecord.record_date == record_date,
            )
        )
        if existing is None:
            existing = UrbanClimateRecord(city_id=city_id, record_date=record_date, source="open-meteo")
            db.add(existing)
        elif not payload.overwrite_existing:
            skipped += 1
            continue

        for field, value in metrics.items():
            setattr(existing, field, value)
        existing.source = "open-meteo"
        imported += 1

    db.commit()
    return ImportResult(
        city_id=city.id,
        city_name=city.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        imported=imported,
        skipped=skipped,
    )

