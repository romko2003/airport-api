✈️ Airport API (Django REST)

A production-ready REST API for managing airports, airplanes, routes, flights, and ticket orders — built with Django, DRF, JWT (SimpleJWT), and drf-spectacular.
Supports PostgreSQL (Docker) and SQLite (local dev). Ships with OpenAPI docs, demo seed data, and a handy seat-map endpoint to visualize taken seats.

🚀 Features

Entities: Airports, Airplane Types, Airplanes (with computed capacity), Routes, Crew

Flights

Filter by date, source, destination, airplane

available_tickets annotation

GET /api/flights/{id}/seat-map/ — matrix of rows/seats with taken flags

Orders & Tickets

Create orders with multiple tickets in one request

Strong validation (seat bounds & availability)

Auth: JWT access & refresh tokens

Docs: OpenAPI schema & Swagger UI at /api/docs/

Batteries included: Docker/Compose, Postgres, wait_for_db command, static/media volumes, demo seeder, basic tests

🧱 Tech Stack

Python, Django, Django REST Framework

SimpleJWT (Auth), drf-spectacular (OpenAPI)

PostgreSQL (Docker), SQLite (local quick start)

gunicorn (WSGI, Docker runtime)

📦 Repository Structure (key parts)
config/                 # Django project (settings, urls, wsgi)
core/                   # App with models, serializers, views, urls
  management/commands/
    wait_for_db.py      # Blocks until DB is ready (Docker)
    seed_demo.py        # Demo data (users, airports, flight, etc.)
tests/                  # Basic API tests (flights, orders)
manage.py
requirements.txt
Dockerfile
docker-compose.yml
entrypoint.sh

🛠️ Quick Start (Local, SQLite)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver


Open: http://127.0.0.1:8000/api/docs/

Optional: seed demo data

python manage.py seed_demo


Optional: create superuser

python manage.py createsuperuser

🐳 Run with Docker (PostgreSQL)
docker-compose up --build
# App: http://127.0.0.1:8000/api/docs/


The app executes:
wait_for_db → migrate → collectstatic → gunicorn

Named volumes are used for /vol/web/static and /vol/web/media.

Environment Variables
Variable	Example	Description
SECRET_KEY	change-me	Django secret key
DEBUG	1 / 0	Debug mode
ALLOWED_HOSTS	*	Comma-separated hosts
POSTGRES_DB	airport	DB name
POSTGRES_USER	airport	DB user
POSTGRES_PASSWORD	airport	DB password
POSTGRES_HOST	db	DB host (service name)
POSTGRES_PORT	5432	DB port
STATIC_ROOT	/vol/web/static	Static files target
MEDIA_ROOT	/vol/web/media	Uploaded media target
🔐 Authentication (JWT)

Obtain token — POST /api/token/

{ "username": "admin", "password": "adminpass" }


Response

{ "access": "<JWT_ACCESS>", "refresh": "<JWT_REFRESH>" }


Use the access token in requests:

Authorization: Bearer <JWT_ACCESS>


Refresh token — POST /api/token/refresh/

{ "refresh": "<JWT_REFRESH>" }

📚 API Overview

Airports — /api/airports/

Airplane Types — /api/airplane-types/

Airplanes — /api/airplanes/ (capacity = rows × seats_in_row)

Routes — /api/routes/ (unique by source+destination)

Crew — /api/crew/

Flights — /api/flights/

Filters (query params):

date=YYYY-MM-DD

source=<airport_id>

destination=<airport_id>

airplane=<airplane_id>

Extra: GET /api/flights/{id}/seat-map/

Orders — /api/orders/

POST body

{
  "tickets": [
    {"flight": 1, "row": 1, "seat": 2},
    {"flight": 1, "row": 2, "seat": 3}
  ]
}


All endpoints are documented in Swagger UI: /api/docs/.

🧪 Tests & Lint

Local

python manage.py test
flake8


Docker

docker-compose run --rm app sh -c "python manage.py test"
docker-compose run --rm app sh -c "flake8"

🌱 Demo Data

Local

python manage.py seed_demo


Docker

docker-compose run --rm app sh -c "python manage.py seed_demo"


Creates:

users: admin/adminpass, user/userpass

a few entities (airports, airplane, route, crew) and one flight tomorrow

🧩 Data Model (ERD)
Airport 1—n Route n—1 Airport
Route  1—n Flight n—1 Airplane  n—1 AirplaneType
Flight n—n Crew (M2M)
Order  1—n Ticket n—1 Flight

Airplane has rows & seats_in_row → capacity
Flight.available_tickets = capacity - sold


(Optional: add a diagram image to the repo and link it here.)

🧰 Common Issues & Fixes

zsh: command not found: python
Use python3, or install Python and add alias:

brew install python
echo 'alias python="python3"' >> ~/.zshrc && source ~/.zshrc


DB not ready in Docker
The app runs wait_for_db before migrations. If it still fails:

docker-compose logs db
docker-compose logs app


Static/Media permissions in Docker
Volumes are chowned at runtime in entrypoint.sh. If you change paths, update env vars & volumes accordingly.

🗺️ Roadmap (ideas)

User profile & role-based permissions

Search by city/country for airports

Flight pricing & payments

CSV import/export for schedules

Caching seat-maps & availability

📄 License

MIT (or your chosen license). Add a LICENSE file if needed.

❤️ Portfolio Tips

Add screenshots of /api/docs/ and a few endpoints

Include an ERD image

Describe any optional features you implemented

Link a running demo if you deploy it
