from __future__ import annotations

from collections import defaultdict
from datetime import date

import httpx
from fastapi import HTTPException, status


class OpenMeteoService:
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    weather_url = "https://archive-api.open-meteo.com/v1/archive"
    air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    async def search_city(self, name: str, country_code: str = "GB") -> dict:
        params = {
            "name": name,
            "count": 1,
            "language": "en",
            "format": "json",
            "countryCode": country_code,
        }
        try:
            async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                response = await client.get(self.geocoding_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to reach Open-Meteo geocoding service",
            ) from exc

        results = payload.get("results") or []
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No geocoding result found for city '{name}'",
            )
        return results[0]

    async def fetch_weather_history(self, latitude: float, longitude: float, start_date: date, end_date: date) -> dict[str, dict]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timezone": "auto",
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                ]
            ),
        }
        try:
            async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                response = await client.get(self.weather_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to reach Open-Meteo weather history service",
            ) from exc

        daily = payload.get("daily")
        if not daily:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Weather history payload did not contain daily data",
            )

        weather_by_date: dict[str, dict] = {}
        for idx, day in enumerate(daily["time"]):
            weather_by_date[day] = {
                "temperature_max_c": daily["temperature_2m_max"][idx],
                "temperature_min_c": daily["temperature_2m_min"][idx],
                "precipitation_sum_mm": daily["precipitation_sum"][idx],
                "wind_speed_max_kmh": daily["wind_speed_10m_max"][idx],
            }
        return weather_by_date

    async def fetch_air_quality_history(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> dict[str, dict]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timezone": "auto",
            "domains": "cams_europe",
            "hourly": ",".join(
                [
                    "pm2_5",
                    "pm10",
                    "nitrogen_dioxide",
                    "ozone",
                    "european_aqi",
                ]
            ),
        }

        try:
            async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                response = await client.get(self.air_quality_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to reach Open-Meteo air-quality service",
            ) from exc

        hourly = payload.get("hourly")
        if not hourly:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Air-quality payload did not contain hourly data",
            )

        buckets: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: {
                "pm2_5": [],
                "pm10": [],
                "nitrogen_dioxide": [],
                "ozone": [],
                "european_aqi": [],
            }
        )

        for idx, timestamp in enumerate(hourly["time"]):
            day = timestamp.split("T", maxsplit=1)[0]
            for key in buckets[day]:
                value = hourly[key][idx]
                if value is not None:
                    buckets[day][key].append(float(value))

        aggregated: dict[str, dict] = {}
        for day, values in buckets.items():
            aggregated[day] = {
                "pm2_5": round(sum(values["pm2_5"]) / len(values["pm2_5"]), 2) if values["pm2_5"] else None,
                "pm10": round(sum(values["pm10"]) / len(values["pm10"]), 2) if values["pm10"] else None,
                "nitrogen_dioxide": round(sum(values["nitrogen_dioxide"]) / len(values["nitrogen_dioxide"]), 2)
                if values["nitrogen_dioxide"]
                else None,
                "ozone": round(sum(values["ozone"]) / len(values["ozone"]), 2) if values["ozone"] else None,
                "european_aqi": round(max(values["european_aqi"]), 2) if values["european_aqi"] else None,
            }
        return aggregated

    async def fetch_combined_history(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> dict[str, dict]:
        weather = await self.fetch_weather_history(latitude, longitude, start_date, end_date)
        air_quality = await self.fetch_air_quality_history(latitude, longitude, start_date, end_date)

        combined = {}
        for day, weather_values in weather.items():
            combined[day] = {
                **weather_values,
                **air_quality.get(
                    day,
                    {
                        "pm2_5": None,
                        "pm10": None,
                        "nitrogen_dioxide": None,
                        "ozone": None,
                        "european_aqi": None,
                    },
                ),
            }
        return combined
