from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import City, UrbanClimateRecord, User
from app.schemas.climate import RecordCreate, RecordRead, RecordUpdate

router = APIRouter(prefix="/records", tags=["Climate Records"])


@router.get("", response_model=list[RecordRead])
def list_records(
    db: Annotated[Session, Depends(get_db)],
    city_id: int | None = Query(default=None, gt=0),
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[UrbanClimateRecord]:
    stmt = select(UrbanClimateRecord).order_by(UrbanClimateRecord.record_date.desc()).limit(limit)
    if city_id is not None:
        stmt = stmt.where(UrbanClimateRecord.city_id == city_id)
    if start_date is not None:
        stmt = stmt.where(UrbanClimateRecord.record_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(UrbanClimateRecord.record_date <= end_date)
    return list(db.scalars(stmt))


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> UrbanClimateRecord:
    if db.get(City, payload.city_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    record = UrbanClimateRecord(**payload.model_dump())
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A record for this city and date already exists",
        ) from exc
    db.refresh(record)
    return record


@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int, db: Annotated[Session, Depends(get_db)]) -> UrbanClimateRecord:
    record = db.get(UrbanClimateRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@router.put("/{record_id}", response_model=RecordRead)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> UrbanClimateRecord:
    record = db.get(UrbanClimateRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    record = db.get(UrbanClimateRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    db.delete(record)
    db.commit()

