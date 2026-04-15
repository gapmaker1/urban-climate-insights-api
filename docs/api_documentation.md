# Urban Climate Insights API Documentation

## Overview

This document describes the REST endpoints exposed by the Urban Climate Insights API. The project focuses on UK cities and combines manual CRUD with external climate imports from Open-Meteo.

Base URL for local execution:

`http://127.0.0.1:8000`

API prefix:

`/api/v1`

Interactive documentation is also available at `/docs`, and the exported OpenAPI schema is stored in `docs/openapi.json`.

## Authentication

The API uses JWT bearer authentication. Read-only analytics and list endpoints are public. All write operations require a bearer token.

Authentication flow:

- Register a user with `POST /api/v1/auth/register`.
- Exchange credentials for a JWT with `POST /api/v1/auth/token`.
- Include the token as `Authorization: Bearer <token>` in subsequent write requests.

Example registration request:

```json
POST /api/v1/auth/register
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "Password123!"
}
```

Example token request:

```text
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=alice&password=Password123!
```

Example token response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

## Core Data Models

### User

- `id`
- `username`
- `email`
- `hashed_password`
- `is_active`
- `created_at`

### City

- `id`
- `name`
- `country_code`
- `region`
- `latitude`
- `longitude`
- `timezone`
- `source`
- `created_at`
- `updated_at`

### UrbanClimateRecord

- `id`
- `city_id`
- `record_date`
- `temperature_max_c`
- `temperature_min_c`
- `precipitation_sum_mm`
- `wind_speed_max_kmh`
- `pm2_5`
- `pm10`
- `nitrogen_dioxide`
- `ozone`
- `european_aqi`
- `source`
- `created_at`
- `updated_at`

## Endpoint Reference

### `POST /api/v1/auth/register`

Creates a new user account.

- Authentication: not required
- Success status: `201 Created`
- Failure status: `409 Conflict` if username or email already exists

### `POST /api/v1/auth/token`

Returns a JWT bearer token.

- Authentication: not required
- Success status: `200 OK`
- Failure status: `401 Unauthorized` if credentials are invalid

### `GET /api/v1/auth/me`

Returns the current authenticated user.

- Authentication: required
- Success status: `200 OK`
- Failure status: `401 Unauthorized`

### `GET /api/v1/cities`

Lists stored cities.

Optional query parameters:

- `search`: partial city-name filter

Example:

```text
GET /api/v1/cities?search=Leeds
```

### `POST /api/v1/cities`

Creates a tracked city record.

- Authentication: required
- Success status: `201 Created`
- Failure status: `409 Conflict` if the city already exists

Example request:

```json
POST /api/v1/cities
{
  "name": "Leeds",
  "country_code": "GB",
  "region": "England",
  "latitude": 53.8,
  "longitude": -1.55,
  "timezone": "Europe/London",
  "source": "manual"
}
```

### `GET /api/v1/cities/{city_id}`

Fetches a single city.

- Success status: `200 OK`
- Failure status: `404 Not Found`

### `PUT /api/v1/cities/{city_id}`

Updates a city.

- Authentication: required
- Success status: `200 OK`
- Failure status: `404 Not Found`, `409 Conflict`

### `DELETE /api/v1/cities/{city_id}`

Deletes a city and its dependent climate records.

- Authentication: required
- Success status: `204 No Content`
- Failure status: `404 Not Found`

### `GET /api/v1/records`

Lists climate records.

Optional query parameters:

- `city_id`
- `start_date`
- `end_date`
- `limit`

Example:

```text
GET /api/v1/records?city_id=1&start_date=2026-04-01&end_date=2026-04-14&limit=20
```

### `POST /api/v1/records`

Creates a daily climate record.

- Authentication: required
- Success status: `201 Created`
- Failure status: `404 Not Found` if the city does not exist
- Failure status: `409 Conflict` if the `(city_id, record_date)` pair already exists

Example request:

```json
POST /api/v1/records
{
  "city_id": 1,
  "record_date": "2026-04-10",
  "temperature_max_c": 17.5,
  "temperature_min_c": 8.1,
  "precipitation_sum_mm": 1.2,
  "wind_speed_max_kmh": 24.5,
  "pm2_5": 7.0,
  "pm10": 11.4,
  "nitrogen_dioxide": 19.2,
  "ozone": 58.0,
  "european_aqi": 31.0,
  "source": "manual"
}
```

### `GET /api/v1/records/{record_id}`

Retrieves a single climate record.

- Success status: `200 OK`
- Failure status: `404 Not Found`

### `PUT /api/v1/records/{record_id}`

Updates an existing climate record.

- Authentication: required
- Success status: `200 OK`

### `DELETE /api/v1/records/{record_id}`

Deletes a climate record.

- Authentication: required
- Success status: `204 No Content`

### `POST /api/v1/imports/cities/{city_id}/historical`

Imports historical weather and air-quality data from Open-Meteo for an existing city.

- Authentication: required
- Success status: `201 Created`
- Failure status: `404 Not Found` if the city is unknown
- Failure status: `502 Bad Gateway` if the upstream data provider cannot be reached

Example request:

```json
POST /api/v1/imports/cities/1/historical
{
  "start_date": "2026-03-16",
  "end_date": "2026-04-14",
  "overwrite_existing": true
}
```

Example response:

```json
{
  "city_id": 1,
  "city_name": "Leeds",
  "start_date": "2026-03-16",
  "end_date": "2026-04-14",
  "imported": 30,
  "skipped": 0
}
```

### `GET /api/v1/analytics/cities/{city_id}/summary`

Returns aggregated statistics over the selected period.

Optional query parameters:

- `start_date`
- `end_date`

Example response for seeded Leeds data:

```json
{
  "city_id": 1,
  "city_name": "Leeds",
  "start_date": "2026-03-16",
  "end_date": "2026-04-14",
  "record_count": 30,
  "avg_temp_max_c": 12.03,
  "avg_temp_min_c": 4.36,
  "total_precipitation_mm": 38.1,
  "avg_pm2_5": 10.15,
  "avg_pm10": 15.4,
  "avg_nitrogen_dioxide": 13.68,
  "avg_ozone": 67.34,
  "max_european_aqi": 74.0,
  "hottest_day": {
    "record_date": "2026-04-08",
    "temperature_max_c": 20.3
  }
}
```

### `GET /api/v1/analytics/cities/{city_id}/trend`

Returns a time series suitable for charting.

- Each point includes `record_date`, `temperature_max_c`, `pm2_5`, and `european_aqi`.

### `GET /api/v1/analytics/cities/{city_id}/anomalies`

Runs z-score based anomaly detection.

Query parameters:

- `metric`: one of `temperature_max_c`, `precipitation_sum_mm`, `pm2_5`, `european_aqi`
- `threshold`: z-score threshold, default `1.5`
- `start_date`
- `end_date`

Example response:

```json
{
  "city_id": 1,
  "city_name": "Leeds",
  "metric": "temperature_max_c",
  "threshold": 1.5,
  "mean": 12.03,
  "standard_deviation": 2.89,
  "anomalies": [
    {
      "record_date": "2026-04-08",
      "value": 20.3,
      "deviation": 8.27,
      "z_score": 2.86
    }
  ]
}
```

### `GET /api/v1/analytics/compare`

Compares multiple cities over the same range.

Query parameters:

- `city_ids`: repeat this parameter for each city
- `start_date`
- `end_date`

Example:

```text
GET /api/v1/analytics/compare?city_ids=1&city_ids=2
```

Example response excerpt:

```json
[
  {
    "city_id": 1,
    "city_name": "Leeds",
    "avg_temp_max_c": 12.03,
    "avg_pm2_5": 10.15,
    "total_precipitation_mm": 38.1,
    "max_european_aqi": 74.0
  },
  {
    "city_id": 2,
    "city_name": "London",
    "avg_temp_max_c": 14.05,
    "avg_pm2_5": 10.96,
    "total_precipitation_mm": 11.9,
    "max_european_aqi": 67.0
  }
]
```

## Error Handling

The API uses standard HTTP status codes and JSON error bodies.

- `200 OK`: successful read or update
- `201 Created`: resource created successfully
- `204 No Content`: delete succeeded
- `400 Bad Request`: invalid query parameter or unsupported analytics metric
- `401 Unauthorized`: missing or invalid bearer token
- `404 Not Found`: requested city or record does not exist
- `409 Conflict`: duplicate unique resource
- `422 Unprocessable Entity`: validation failed
- `502 Bad Gateway`: upstream Open-Meteo service failure

## Source References

- Open-Meteo Historical Weather API: `https://open-meteo.com/en/docs/historical-weather-api`
- Open-Meteo Air Quality API: `https://open-meteo.com/en/docs/air-quality-api`
- Open-Meteo Geocoding API: `https://open-meteo.com/en/docs/geocoding-api`
- OpenAPI export in this repository: `docs/openapi.json`
