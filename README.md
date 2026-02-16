# Airport API ✈️ (Django REST Framework)

REST API service for managing airports, routes, flights, airplanes, crews and ticket booking via orders.

## Features
- Airports and routes management
- Airplanes and airplane types management
- Crew management
- Flights management (with filtering/search/ordering)
- Authentication:
  - user registration
  - JWT token obtain/refresh
- Orders & tickets:
  - create order and book seats for a flight
  - seat bounds validation (row/seat within airplane)
  - prevents booking taken seats
  - atomic transaction for order + tickets

---

## Tech stack
- Django + Django REST Framework
- JWT Auth: djangorestframework-simplejwt
- drf-spectacular (Swagger docs)
- PostgreSQL (Docker) / SQLite (local)
- django-filter

---

Run locally (SQLite)

Clone the repository

git clone <YOUR_REPO_URL>
cd <YOUR_PROJECT_DIR>


Create venv and install dependencies

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


Create .env

cp .env.example .env


Apply migrations and run server

python manage.py migrate
python manage.py runserver


Browsable API:

http://127.0.0.1:8000/api/

Swagger docs:

http://127.0.0.1:8000/api/docs/

Run with Docker (PostgreSQL)

Create .env

cp .env.example .env


Build and run containers

docker-compose build
docker-compose up


Open:

http://127.0.0.1:8000/api/

http://127.0.0.1:8000/api/docs/

Getting access (JWT)
1) Register user

POST /api/accounts/register/

Request:

{
  "username": "demo",
  "email": "demo@example.com",
  "password": "StrongPassword123!"
}

2) Obtain JWT tokens

POST /api/accounts/token/

Request:

{
  "username": "demo",
  "password": "StrongPassword123!"
}


Response:

{
  "refresh": "....",
  "access": "...."
}


Use the access token in requests:

Header:

Authorization: Bearer <access>

3) Refresh token

POST /api/accounts/token/refresh/

Request:

{
  "refresh": "...."
}

API endpoints
Reference data (Read for everyone, Write for staff only)

GET /api/airports/

GET /api/routes/

GET /api/airplane-types/

GET /api/airplanes/

GET /api/crew/

GET /api/flights/

Filtering examples:

/api/flights/?route__source=1

/api/flights/?route__destination=2

/api/flights/?airplane__airplane_type=3

Search example:

/api/flights/?search=Kyiv

Ordering example:

/api/flights/?ordering=departure_time

/api/flights/?ordering=-arrival_time

Orders (Authenticated users only)

GET /api/orders/ — list only your orders

POST /api/orders/ — create order and book seats

Create order example:
POST /api/orders/

{
  "flight_id": 1,
  "seats": [
    {"row": 1, "seat": 1},
    {"row": 1, "seat": 2}
  ]
}

Admin panel

Create superuser:

python manage.py createsuperuser


Admin:

http://127.0.0.1:8000/admin/

Screenshots for Pull Request (Browsable API)

Attach screenshots to your final PR (develop -> main):

/api/airports/ list page

/api/routes/ list page

/api/flights/ list page

/api/flights/<id>/ detail page

/api/orders/ list page (authenticated)

DB diagram (draw.io)

Create DB diagram (draw.io) based on models and attach the image to PR:

db_diagram.png or db_diagram.svg

Suggested approach:

open draw.io

create entities: Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket

add relations (FK/M2M)

export as PNG/SVG and attach to PR

Notes

This project is built as a portfolio project for demonstrating DRF skills and clean architecture:

ViewSets + serializers + router

business logic moved to services

constraints and validation at both app and database levels

## Project structure
```text
airport_api/
├── config/
├── airport/
├── accounts/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
