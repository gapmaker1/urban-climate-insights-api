from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import City, User
from app.schemas.city import CityCreate, CityRead, CityUpdate

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("", response_model=list[CityRead])
def list_cities(
    db: Annotated[Session, Depends(get_db)],
    search: str | None = Query(default=None, max_length=100),
) -> list[City]:
    stmt = select(City).order_by(City.name)
    if search:
        stmt = stmt.where(City.name.ilike(f"%{search}%"))
    return list(db.scalars(stmt))


@router.post("", response_model=CityRead, status_code=status.HTTP_201_CREATED)
def create_city(
    payload: CityCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> City:
    city = City(**payload.model_dump())
    db.add(city)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="City already exists") from exc
    db.refresh(city)
    return city


@router.get("/{city_id}", response_model=CityRead)
def get_city(city_id: int, db: Annotated[Session, Depends(get_db)]) -> City:
    city = db.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return city


@router.put("/{city_id}", response_model=CityRead)
def update_city(
    city_id: int,
    payload: CityUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> City:
    city = db.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(city, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Updated city would duplicate an existing record") from exc
    db.refresh(city)
    return city


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(
    city_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    city = db.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    db.delete(city)
    db.commit()
