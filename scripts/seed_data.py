import asyncio
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal, create_db_and_tables
from app.core.security import hash_password
from app.models.entities import City, UrbanClimateRecord, User
from app.services.open_meteo import OpenMeteoService

SEED_CITIES_PATH = ROOT / "data" / "seed_cities.json"


async def seed_demo_data() -> None:
    create_db_and_tables()
    db = SessionLocal()
    service = OpenMeteoService()
    city_payloads = json.loads(SEED_CITIES_PATH.read_text(encoding="utf-8"))
    start_date = date.today() - timedelta(days=30)
    end_date = date.today() - timedelta(days=1)

    try:
        demo_user = db.scalar(select(User).where(User.username == "demo"))
        if demo_user is None:
            demo_user = User(
                username="demo",
                email="demo@example.com",
                hashed_password=hash_password("Password123!"),
            )
            db.add(demo_user)
            db.commit()

        for item in city_payloads:
            result = await service.search_city(item["name"], item.get("country_code", "GB"))
            city = db.scalar(
                select(City).where(
                    City.name == result["name"],
                    City.country_code == item.get("country_code", "GB"),
                )
            )
            if city is None:
                city = City(
                    name=result["name"],
                    country_code=item.get("country_code", "GB"),
                    region=result.get("admin1"),
                    latitude=result["latitude"],
                    longitude=result["longitude"],
                    timezone=result.get("timezone"),
                    source="open-meteo-geocoding",
                )
                db.add(city)
                db.commit()
                db.refresh(city)

            combined_history = await service.fetch_combined_history(
                latitude=city.latitude,
                longitude=city.longitude,
                start_date=start_date,
                end_date=end_date,
            )

            for day, metrics in combined_history.items():
                record_date = date.fromisoformat(day)
                record = db.scalar(
                    select(UrbanClimateRecord).where(
                        UrbanClimateRecord.city_id == city.id,
                        UrbanClimateRecord.record_date == record_date,
                    )
                )
                if record is None:
                    record = UrbanClimateRecord(city_id=city.id, record_date=record_date)
                    db.add(record)
                for field, value in metrics.items():
                    setattr(record, field, value)
                record.source = "open-meteo"

            db.commit()
            print(f"Seeded {city.name} from {start_date} to {end_date}.")

        print("Demo user created: username=demo password=Password123!")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
