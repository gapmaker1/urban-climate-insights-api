# Technical Report: Urban Climate Insights API

## Student Details

Student name: `Yuan Rui`

Student ID: `2022115981`

GitHub repository: `https://github.com/gapmaker1/urban-climate-insights-api`

API documentation (PDF): `https://github.com/gapmaker1/urban-climate-insights-api/blob/main/docs/api_documentation.pdf`

Presentation slides and visuals: `https://github.com/gapmaker1/urban-climate-insights-api/blob/main/presentation/Urban_Climate_Insights_API_Presentation.pptx`

Module: Web Services and Web Data

Submission date: `20 April 2026`

## Project Summary

Urban Climate Insights API is a RESTful API that stores and analyses city-level environmental data for the UK. The system supports CRUD operations for tracked cities and daily urban climate records, authenticates write access with JWT bearer tokens, and imports historical weather and air-quality observations from Open-Meteo.

The project was designed to go beyond the minimum coursework requirements. Instead of only storing manually entered records, it demonstrates external data integration, analytical processing, reproducible seeding, automated testing, and multiple deliverables suitable for the oral examination.

## Problem Choice and Rationale

I selected an urban climate domain because it works well as a web-data project for four reasons:

- It naturally combines CRUD with analytical queries, which fits the assignment brief well.
- It benefits from external open data, allowing the API to demonstrate integration rather than only local storage.
- It provides interesting numeric measures such as temperature, rainfall, PM2.5, PM10, ozone, and AQI, which support meaningful summaries and anomaly detection.
- It is easy to explain visually during a short oral presentation because the dataset relates to real cities and familiar environmental concerns.

## Requirements Coverage

The implementation satisfies the minimum technical requirements as follows:

- It includes database-backed CRUD for both `City` and `UrbanClimateRecord`.
- It exposes more than four endpoints over HTTP.
- It validates user input and returns JSON responses.
- It uses conventional HTTP status codes such as `201`, `204`, `401`, `404`, `409`, and `422`.
- It runs locally with FastAPI and can be containerised with the included Dockerfile.
- It includes API documentation, a technical report, and presentation slides.

## Technology Stack and Justification

### FastAPI

FastAPI was chosen because it is productive for API-first coursework. It provides:

- automatic OpenAPI generation
- built-in request validation through Pydantic
- strong support for JSON APIs
- interactive Swagger UI for live demonstration during the oral exam

This is a good fit for a project that must be both technically sound and easy to present.

### SQLAlchemy 2.0

SQLAlchemy 2.0 was selected for database access because it offers a mature ORM with explicit models, relationships, constraints, and composable queries. Compared with simpler database wrappers, it provides clearer control over schema design and query behaviour, which is useful when discussing design choices with examiners.

### SQLite

SQLite was used as the default database because the coursework must run locally with minimal setup. For a single-student project and oral demonstration, SQLite is appropriate because it is lightweight and easy to reproduce. The trade-off is that it is not ideal for concurrent production traffic, so PostgreSQL would be a better next step for deployment at scale.

### JWT Authentication

JWT bearer tokens were used to protect write operations. This design keeps public analytics endpoints easy to explore while ensuring that destructive actions require authentication. It also demonstrates an industry-standard authentication pattern rather than leaving the API completely open.

### Open-Meteo as Data Source

Open-Meteo was selected because it provides public geocoding, historical weather, and air-quality APIs that can be accessed without managing personal API keys for academic prototyping. This made it practical to build an import pipeline inside the coursework timescale.

Official documentation used:

- Historical Weather API: `https://open-meteo.com/en/docs/historical-weather-api`
- Air Quality API: `https://open-meteo.com/en/docs/air-quality-api`
- Geocoding API: `https://open-meteo.com/en/docs/geocoding-api`
- Licence page: `https://open-meteo.com/en/licence`

On the Open-Meteo licence page, the provider states that API data are offered under `CC BY 4.0`, which is suitable for academic attribution with proper citation.

## Architecture

The application follows a layered structure:

- `routers`: HTTP endpoints and request orchestration
- `schemas`: request and response validation
- `models`: SQLAlchemy entities and database schema
- `services`: analytics logic and external Open-Meteo integration
- `core`: configuration, database session management, and security helpers

This separation improves readability and makes the code easier to defend in a viva setting. For example, it is clear that the Open-Meteo logic is not embedded inside the route handlers, and the anomaly detection logic is isolated from transport concerns.

## Database Design

The main entities are:

- `User`: stores login credentials and active status
- `City`: stores tracked city metadata including coordinates and timezone
- `UrbanClimateRecord`: stores one daily observation per city per date

Important design decisions:

- A uniqueness constraint on `(name, country_code)` prevents duplicate city entries.
- A uniqueness constraint on `(city_id, record_date)` prevents duplicate daily records for the same city.
- `City` has a one-to-many relationship with `UrbanClimateRecord`.
- Deleting a city cascades to its climate records, keeping referential integrity simple.

This schema is normalised enough for the coursework while remaining easy to explain.

## Data Import Workflow

The project includes a reproducible seed script: `scripts/seed_data.py`.

Its workflow is:

- read a small list of UK city names from `data/seed_cities.json`
- resolve each city through the Open-Meteo geocoding API
- fetch 30 days of historical weather data
- fetch hourly air-quality data and aggregate it into daily averages or maxima
- upsert the resulting data into SQLite
- create a demo user for presentation

After running the script on `15 April 2026`, the database contained:

- `6` UK cities
- `180` climate records
- `1` seeded demo user

This gives the project a realistic amount of data for presentation without becoming difficult to manage.

## Analytics Design

The analytical endpoints were chosen to show that the API does more than CRUD.

Implemented analytics:

- city summary statistics
- time-series trend output
- cross-city comparison
- z-score based anomaly detection

The anomaly endpoint is a useful demonstration feature because it lets me discuss a concrete statistical method rather than only basic aggregation.

## Validation, Error Handling, and API Behaviour

The API validates request payloads using Pydantic. Examples include:

- enforcing sensible latitude and longitude ranges
- ensuring `temperature_max_c` is not lower than `temperature_min_c`
- ensuring import date ranges are valid
- constraining numeric environmental fields to non-negative values where appropriate

Error handling follows conventional status codes:

- `401 Unauthorized` for invalid or missing tokens
- `404 Not Found` for missing cities or records
- `409 Conflict` for duplicate unique resources
- `422 Unprocessable Entity` for validation failures
- `502 Bad Gateway` when the external Open-Meteo service cannot be reached

During development I discovered that local proxy environment variables could interfere with `httpx` requests. I fixed this by configuring the Open-Meteo client with `trust_env=False`, which made the import scripts more robust and easier to run on different machines.

## Testing Approach

Testing was implemented with `pytest` and FastAPI's `TestClient`.

The automated tests cover:

- user registration, login, and authenticated profile access
- city CRUD operations
- climate record CRUD operations
- analytics endpoints for summary, comparison, and anomaly detection

This provides evidence that the API works across the main user journeys, not only at the individual function level.

## Version Control and Deliverables

The repository is structured so that all required deliverables live alongside the code:

- `README.md`
- `docs/api_documentation.md`
- `docs/api_documentation.pdf`
- `docs/technical_report.md`
- `docs/technical_report.pdf`
- `presentation/Urban_Climate_Insights_API_Presentation.pptx`

The project is also designed to support clear commit milestones such as:

- project scaffolding
- authentication and database models
- CRUD routes
- analytics and import integration
- tests and documentation

This makes it easy to maintain a visible GitHub history that examiners can review.

## Challenges and Lessons Learned

The main technical challenges were:

- designing an API that was richer than the minimum CRUD brief but still feasible within coursework scope
- combining daily weather data with hourly air-quality data in a consistent daily schema
- balancing local reproducibility with external data integration
- generating all supporting deliverables in a way that stays synchronised with the code

The main lessons learned were:

- service-layer separation makes debugging much easier
- analytical features become more convincing when grounded in reproducible seed data
- small operational details, such as environment-dependent HTTP configuration, matter a lot for live demos
- documentation and slides are easier to write when the code structure is clean from the start

## Limitations

The current version has some limitations:

- SQLite is suitable for local demonstration, but PostgreSQL would be better for concurrent deployment.
- External imports run synchronously in the request path, so a production version should move them to a background worker or scheduled job.
- Authentication is intentionally simple and does not yet include roles, refresh tokens, or audit logging.
- The project focuses on API behaviour rather than a frontend dashboard.

## Future Improvements

Possible extensions include:

- deploying with PostgreSQL and persistent cloud hosting
- adding scheduled nightly imports
- caching frequent analytics queries
- adding role-based access control for administrative imports
- exposing chart-ready aggregation windows such as weekly and monthly summaries
- building a lightweight frontend or dashboard on top of the API

## Generative AI Declaration

Generative AI was used in a deliberate and methodologically controlled way during this project.

AI-assisted activities:

- brainstorming project directions that would exceed the minimum pass requirements
- drafting implementation scaffolding for FastAPI, SQLAlchemy, and testing
- suggesting ways to structure supporting documentation and slides
- helping diagnose development issues such as environment-related HTTP connectivity problems

AI was not used as an unquestioned code generator. All generated content was reviewed, edited, tested, and integrated manually. In particular:

- the architecture was selected intentionally to fit the module brief
- validation and analytics behaviour were checked with automated tests
- the final report and documentation were rewritten to reflect the actual implementation
- external data source suitability and licensing were checked against official documentation

Reflecting on this process, AI was most valuable for accelerating prototyping and exploring alternatives, not for replacing design judgement. The most important human contribution remained the selection of trade-offs, debugging of real execution issues, and alignment of the deliverables with the marking criteria.

## Conclusion

Urban Climate Insights API meets the coursework requirements and extends them with external data integration, analytical endpoints, testing, and presentation-ready deliverables. The final system is not only a working CRUD API, but also a small analytical platform that can be explained clearly in an oral exam and expanded further in future work.

## Appendix A: Selected Generative AI Conversation Logs

This appendix records representative GenAI-assisted interactions used during development. The full working conversation was longer, so the entries below focus on the prompts that materially affected design, debugging, submission preparation, and presentation planning.

### Log 1: Project Direction and Scope

- User prompt: "Help me complete a Web Services and Web Data coursework project."
- AI support: suggested a project direction that would exceed the minimum CRUD brief by combining database-backed API design, external open data, analytics, testing, and coursework deliverables.
- Outcome used in the project: the final system became the Urban Climate Insights API rather than a minimal single-model CRUD exercise.

### Log 2: Clarifying the Nature of the Project

- User prompt: "I don't really understand what this project is in essence."
- AI support: reframed the project as a backend data service rather than a traditional website, explaining that the API is the layer that stores, imports, serves, and analyses environmental data.
- Outcome used in the project: this explanation informed the oral presentation narrative and technical report wording.

### Log 3: Debugging a Package Import Error

- User prompt: "Explain this error with examples" after receiving `ModuleNotFoundError: No module named 'app'`.
- AI support: explained Python package resolution, why `python app/main.py` failed in that context, and why `uvicorn app.main:app --reload` or module-based execution is the correct startup approach.
- Outcome used in the project: the project startup guidance was clarified and the runtime path issue was resolved for local demonstration.

### Log 4: Repository and Commit History Preparation

- User prompt: "I don't want to upload only one big commit; tell me in detail how I should upload it."
- AI support: proposed a logical commit structure, checked Git status, and helped organise the repository into meaningful milestones rather than a single monolithic upload.
- Outcome used in the project: the public GitHub repository now shows staged development-oriented commits and cleaner submission history.

### Log 5: Oral Presentation and Q&A Preparation

- User prompt: "Write a defence script of around 10 minutes and a list of likely Q&A questions."
- AI support: drafted English and Chinese speaking notes, highlighted likely examiner questions, and aligned the oral explanation with the implemented stack, analytics, and trade-offs.
- Outcome used in the project: the presentation deck and viva preparation materials were structured around these talking points.

### Log 6: Final Submission Cleanup

- User prompt: "Help me clean the project and remove unused files, such as image-generation scripts."
- AI support: identified non-essential generation scripts and temporary image assets, then simplified the repository to keep only runnable code and final submission materials.
- Outcome used in the project: the final repository is cleaner, easier to review, and more closely aligned with the actual submission requirements.
