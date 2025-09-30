# ✈️ Airport API (Django REST)

A production-ready REST API for managing airports, airplanes, routes, flights, and ticket orders — built with **Django**, **Django REST Framework**, **JWT (SimpleJWT)**, and **drf-spectacular**.  
Supports **PostgreSQL** (via Docker) and **SQLite** (for quick local development).  
Includes OpenAPI docs, demo seed data, and a seat-map endpoint to visualize taken seats.

---

## 🚀 Features

### Entities
- **Airports**, **Airplane Types**, **Airplanes** (with computed capacity), **Routes**, **Crew**.

### Flights
- Filter by **date**, **source**, **destination**, **airplane**.  
- `available_tickets` annotation.  
- `GET /api/flights/{id}/seat-map/` — returns a seat matrix (rows × seats) with **taken** flags.

### Orders & Tickets
- Create orders with **multiple tickets** in one request.
- Strong validation (seat bounds & seat availability).

### Auth & Docs
- **JWT** access & refresh tokens.
- OpenAPI schema & **Swagger UI** at **`/api/docs/`**.

### Batteries Included
- Docker/Compose, PostgreSQL, `wait_for_db` command, static/media volumes, demo seeder, and basic tests.

---

## 🧱 Tech Stack

- **Backend:** Python, Django, Django REST Framework  
- **Auth & Docs:** SimpleJWT, drf-spectacular  
- **Databases:** PostgreSQL (Docker), SQLite (local quick start)  
- **Runtime (Docker):** gunicorn

---

## 📦 Repository Structure (key parts)

config/ # Django project (settings, urls, wsgi)
core/ # App with models, serializers, views, urls
management/commands/
wait_for_db.py # Blocks until DB is ready (Docker)
seed_demo.py # Demo data (users, airports, flight, etc.)
tests/ # Basic API tests (flights, orders)
manage.py
requirements.txt
Dockerfile
docker-compose.yml
entrypoint.sh

markdown
Copy code

---

## 🛠️ Getting Started (Local, SQLite)

~~~bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
~~~

Open: **http://127.0.0.1:8000/api/docs/**

**Optional: seed demo data**
~~~bash
python manage.py seed_demo
~~~

**Optional: create superuser**
~~~bash
python manage.py createsuperuser
~~~

---

## 🐳 Run with Docker (PostgreSQL)

~~~bash
docker-compose up --build
~~~

App: **http://127.0.0.1:8000/api/docs/**

On container start it runs:

1. `wait_for_db`  
2. `migrate`  
3. `collectstatic`  
4. `gunicorn`

Named volumes are used for `/vol/web/static` and `/vol/web/media`.

---

## ⚙️ Environment Variables

| Variable            | Example            | Description                 |
|---------------------|--------------------|-----------------------------|
| `SECRET_KEY`        | `change-me`        | Django secret key           |
| `DEBUG`             | `1` / `0`          | Debug mode                  |
| `ALLOWED_HOSTS`     | `*`                | Comma-separated hosts       |
| `POSTGRES_DB`       | `airport`          | DB name                     |
| `POSTGRES_USER`     | `airport`          | DB user                     |
| `POSTGRES_PASSWORD` | `airport`          | DB password                 |
| `POSTGRES_HOST`     | `db`               | DB host (Docker service)    |
| `POSTGRES_PORT`     | `5432`             | DB port                     |
| `STATIC_ROOT`       | `/vol/web/static`  | Static files target         |
| `MEDIA_ROOT`        | `/vol/web/media`   | Uploaded media target       |

**Example `.env` (Docker):**
~~~env
SECRET_KEY=change-me
DEBUG=0
ALLOWED_HOSTS=*

POSTGRES_DB=airport
POSTGRES_USER=airport
POSTGRES_PASSWORD=airport
POSTGRES_HOST=db
POSTGRES_PORT=5432

STATIC_ROOT=/vol/web/static
MEDIA_ROOT=/vol/web/media
~~~

---

## 🔐 Authentication (JWT)

**Obtain token** — `POST /api/token/`
~~~json
{
  "username": "admin",
  "password": "adminpass"
}
~~~

**Response**
~~~json
{
  "access": "<JWT_ACCESS>",
  "refresh": "<JWT_REFRESH>"
}
~~~

Use the access token in requests:
Authorization: Bearer <JWT_ACCESS>

markdown
Copy code

**Refresh token** — `POST /api/token/refresh/`
~~~json
{
  "refresh": "<JWT_REFRESH>"
}
~~~

---

## 📚 API Overview

- **Airports** — `GET/POST /api/airports/`
- **Airplane Types** — `GET/POST /api/airplane-types/`
- **Airplanes** — `GET/POST /api/airplanes/`  
  _Capacity = `rows × seats_in_row`_
- **Routes** — `GET/POST /api/routes/`  
  _Unique by `source + destination`_
- **Crew** — `GET/POST /api/crew/`
- **Flights** — `GET/POST /api/flights/`
  - **Filters (query params):**
    - `date=YYYY-MM-DD`
    - `source=<airport_id>`
    - `destination=<airport_id>`
    - `airplane=<airplane_id>`
  - **Extra:** `GET /api/flights/{id}/seat-map/`
- **Orders** — `GET/POST /api/orders/`

**Create order** — `POST /api/orders/`
~~~json
{
  "tickets": [
    { "flight": 1, "row": 1, "seat": 2 },
    { "flight": 1, "row": 2, "seat": 3 }
  ]
}
~~~

_All endpoints are documented in Swagger UI: **`/api/docs/`**._

---

## 🧪 Tests & Lint

**Local**
~~~bash
python manage.py test
flake8
~~~

**Docker**
~~~bash
docker-compose run --rm app sh -c "python manage.py test"
docker-compose run --rm app sh -c "flake8"
~~~

---

## 🌱 Demo Data

**Local**
~~~bash
python manage.py seed_demo
~~~

**Docker**
~~~bash
docker-compose run --rm app sh -c "python manage.py seed_demo"
~~~

Creates:
- Users: `admin/adminpass`, `user/userpass`
- A few entities (airports, airplane, route, crew) and one **flight tomorrow**

---

## 🧩 Data Model (ERD)

- `Airport 1—n Route n—1 Airport`  
- `Route 1—n Flight n—1 Airplane n—1 AirplaneType`  
- `Flight n—n Crew (M2M)`  
- `Order 1—n Ticket n—1 Flight`

**Notes**
- **Airplane** has `rows` & `seats_in_row` → **capacity**.  
- `Flight.available_tickets = capacity - sold`.

_(Optional: add an ERD image to the repo and link it here.)_

---

## 🧰 Common Issues & Fixes

### `zsh: command not found: python`
Use `python3`, or install Python and add an alias:
~~~bash
brew install python
echo 'alias python="python3"' >> ~/.zshrc && source ~/.zshrc
~~~

### DB not ready in Docker
The app runs `wait_for_db` before migrations. If it still fails:
~~~bash
docker-compose logs db
docker-compose logs app
~~~

### Static/Media permissions in Docker
Volumes are `chown`’d at runtime in `entrypoint.sh`.  
If you change paths, update env vars & volumes accordingly.

---

## 🗺️ Roadmap

- User profile & role-based permissions  
- Search by city/country for airports  
- Flight pricing & payments  
- CSV import/export for schedules  
- Caching seat-maps & availability

---

## 📄 License

**MIT** (or your chosen license). Add a `LICENSE` file if needed.

---
