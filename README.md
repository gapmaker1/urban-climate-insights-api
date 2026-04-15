# Urban Climate Insights API

Urban Climate Insights API is a coursework-ready REST API for the Web Services and Web Data module. It combines authenticated CRUD operations with real weather and air-quality imports from Open-Meteo, then exposes analytics endpoints for summary statistics, anomaly detection, and cross-city comparison.

## Deliverables

- API documentation PDF: `docs/api_documentation.pdf`
- Technical report PDF: `docs/technical_report.pdf`
- Presentation slides: `presentation/Urban_Climate_Insights_API_Presentation.pptx`
- Exported OpenAPI schema: `docs/openapi.json`

## Key Features

- JWT authentication with register, login, and current-user endpoints.
- Full CRUD for `City` and `UrbanClimateRecord` models backed by SQLite.
- External data import from Open-Meteo historical weather, air-quality, and geocoding services.
- Analytics endpoints for city summaries, trend series, anomaly detection, and city-to-city comparison.
- Automated test suite covering authentication, CRUD, and analytics workflows.
- Delivery material generation scripts for OpenAPI export, PDF documents, and PowerPoint slides.

## Technology Stack

- Python 3.11
- FastAPI for REST API development and automatic OpenAPI generation
- SQLAlchemy 2.0 for ORM and database access
- SQLite for local coursework demonstration
- JWT bearer tokens for authentication
- Open-Meteo APIs for geocoding, historical weather, and air-quality data
- Pytest for automated testing
- ReportLab and python-pptx for coursework deliverables

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies.
3. Seed the database with sample cities, 30 days of observations, and a demo user.
4. Start the API server.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\seed_data.py
uvicorn app.main:app --reload
```

The API will then be available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Demo Credentials

- Username: `demo`
- Password: `Password123!`

These credentials are created by `scripts/seed_data.py`.

## Running Tests

```powershell
.\.venv\Scripts\python -m pytest
```

## Exporting Supporting Materials

```powershell
.\.venv\Scripts\python scripts\export_openapi.py
.\.venv\Scripts\python scripts\render_markdown_pdf.py docs\api_documentation.md docs\api_documentation.pdf
.\.venv\Scripts\python scripts\render_markdown_pdf.py docs\technical_report.md docs\technical_report.pdf
.\.venv\Scripts\python scripts\build_slides.py
```

## API Overview

- `POST /api/v1/auth/register`: create a user account.
- `POST /api/v1/auth/token`: exchange username and password for a JWT token.
- `GET /api/v1/auth/me`: inspect the authenticated user profile.
- `GET|POST|PUT|DELETE /api/v1/cities`: manage tracked UK cities.
- `GET|POST|PUT|DELETE /api/v1/records`: manage daily urban climate records.
- `POST /api/v1/imports/cities/{city_id}/historical`: import historical weather and air-quality data from Open-Meteo.
- `GET /api/v1/analytics/cities/{city_id}/summary`: aggregated statistics for one city.
- `GET /api/v1/analytics/cities/{city_id}/trend`: date-series trend output for plotting.
- `GET /api/v1/analytics/cities/{city_id}/anomalies`: z-score based anomaly detection.
- `GET /api/v1/analytics/compare`: compare multiple cities over the same date range.

## Project Structure

```text
app/
  core/         configuration, database, security
  models/       SQLAlchemy entities
  routers/      FastAPI route handlers
  schemas/      Pydantic request and response models
  services/     analytics and Open-Meteo integration
data/           seed city list
docs/           markdown and PDF supporting materials
presentation/   generated PowerPoint deck
scripts/        seed, export, and document generation scripts
tests/          pytest coverage
```

## Assessment Coverage

- Minimum requirements are met through authenticated CRUD on database-backed `City` and `UrbanClimateRecord` models.
- More than four HTTP endpoints are implemented, all returning JSON and appropriate status codes.
- API documentation is provided through Swagger UI, exported OpenAPI, and a dedicated PDF document.
- A concise technical report with stack justification, challenges, testing, limitations, and GenAI declaration is included.
- Slides are included for the oral examination and explicitly cover deliverables, version control, documentation, and technical choices.

## Submission Notes

- Replace the placeholder student name, student ID, and GitHub URL in the slide deck before submission.
- Push this repository to a public GitHub repository with visible commit history.
- Regenerate the PDF files after any major content change to keep the deliverables aligned with the code.

