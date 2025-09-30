
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

