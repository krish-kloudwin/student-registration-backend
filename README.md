# Student Registration System — Backend

FastAPI + PostgreSQL backend for the Student Registration System. Exposes a
REST API used by the separate `student-registration-frontend` Next.js app.

## 1. Overview

This service accepts student registrations, validates them (both with
Pydantic and with custom business rules), stores them in PostgreSQL, and
lets them be listed back out. It never trusts the frontend's validation —
every rule is re-checked here.

## 2. Architecture

```
Next.js Frontend (separate repo)
        │  HTTP REST (JSON)
        ▼
FastAPI  (app/main.py)          ← routes, CORS, error handling
        │
        ▼
Pydantic  (app/schemas.py)      ← request/response validation
        │
        ▼
Business validation (app/main.py) ← duplicate email/mobile checks
        │
        ▼
SQLAlchemy (app/models.py, app/crud.py, app/database.py)
        │
        ▼
PostgreSQL (database/schema.sql)
```

## 3. Project structure

```
student-registration-backend/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI app, routes, CORS, error handlers
│   ├── config.py       # Reads environment variables (.env)
│   ├── database.py     # SQLAlchemy engine/session setup
│   ├── models.py       # SQLAlchemy ORM model (students table)
│   ├── schemas.py       # Pydantic request/response models + validation rules
│   └── crud.py          # Database access functions
├── database/
│   └── schema.sql        # Raw SQL to create the students table
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 4. Prerequisites

- Python 3.11+ (3.10+ also works)
- PostgreSQL 14+ installed and running locally
- pip

## 5. Step 1 — Install PostgreSQL & create the database

If PostgreSQL isn't installed yet, install it for your OS (postgresql.org has
installers for Windows/macOS; on Linux use your package manager, e.g.
`sudo apt install postgresql`).

Then create the database:

```bash
# Log into psql as the postgres superuser
psql -U postgres

# Inside the psql prompt:
CREATE DATABASE student_registration;
\q
```

Create the table (optional — the app also creates it automatically on
startup — but running this manually is good for demonstrating the schema):

```bash
psql -U postgres -d student_registration -f database/schema.sql
```

## 6. Step 2 — Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your real PostgreSQL username/password:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/student_registration
CORS_ORIGINS=http://localhost:3000
```

**Never commit `.env`** — it's already listed in `.gitignore`. Only
`.env.example` (no real secrets) is committed.

## 7. Step 3 — Create a virtual environment & install dependencies

```bash
cd student-registration-backend
python -m venv venv
```

Activate it:

- **Linux / macOS:** `source venv/bin/activate`
- **Windows (cmd):** `venv\Scripts\activate.bat`
- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`

Install dependencies:

```bash
pip install -r requirements.txt
```

## 8. Step 4 — Start the API

```bash
uvicorn app.main:app --reload
```

Expected output includes a line like:
```
Uvicorn running on http://127.0.0.1:8000
```

## 9. Step 5 — Open Swagger UI

Visit: **http://localhost:8000/docs**

You should see two endpoints under "Students": `POST /api/students` and
`GET /api/students`.

## 10. API Endpoints

### `POST /api/students` — Register a student

**Request body:**
```json
{
  "first_name": "Rahul",
  "last_name": "Kumar",
  "email": "rahul@gmail.com",
  "mobile": "9876543210",
  "date_of_birth": "2002-05-15",
  "gender": "Male",
  "course": "BCA",
  "address": "123 MG Road",
  "city": "Bengaluru",
  "state": "Karnataka",
  "pincode": "560001"
}
```

**Success response — `201 Created`:**
```json
{
  "success": true,
  "message": "Student registered successfully",
  "student_id": 101
}
```

**Validation error — `422 Unprocessable Entity`** (e.g. invalid email, short
name, bad pincode, invalid course/gender, age under 5, etc.):
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    { "field": "email", "message": "value is not a valid email address" }
  ]
}
```

**Duplicate email or mobile — `409 Conflict`:**
```json
{ "detail": "A student with this email is already registered" }
```

### `GET /api/students` — List all students

**Success response — `200 OK`:**
```json
[
  {
    "id": 101,
    "first_name": "Rahul",
    "last_name": "Kumar",
    "email": "rahul@gmail.com",
    "mobile": "9876543210",
    "date_of_birth": "2002-05-15",
    "gender": "Male",
    "course": "BCA",
    "address": "123 MG Road",
    "city": "Bengaluru",
    "state": "Karnataka",
    "pincode": "560001",
    "created_at": "2026-09-18T10:15:00Z",
    "updated_at": "2026-09-18T10:15:00Z"
  }
]
```

## 11. How validation works

Every field is validated by **Pydantic** (`app/schemas.py`) before the
route function even runs:

| Field | Rule |
|---|---|
| first_name / last_name | required, min 2 characters |
| email | required, valid email format |
| mobile | required, exactly 10 digits, must start with 6/7/8/9 (Indian mobile) |
| date_of_birth | required, valid date, student must be ≥ 5 years old |
| gender | must be one of `Male`, `Female`, `Other` |
| course | must be one of `BCA`, `BSc`, `BCom`, `MCA`, `MBA` |
| address | required, min 10 characters |
| city / state | required, min 2 characters |
| pincode | required, exactly 6 digits |

Any failure returns `422` automatically, before touching the database.

After Pydantic passes, `app/main.py` performs **business validation**:
duplicate email and duplicate mobile checks against the database, each
returning `409 Conflict` with a clean message (never a raw SQL error).

## 12. How duplicate handling works

1. Before inserting, the API queries for an existing row with the same
   email, and separately for the same mobile number.
2. If either exists, it returns `409 Conflict` immediately.
3. As a safety net for race conditions (two identical requests at the same
   instant), the database `UNIQUE` constraints on `email` and `mobile`
   also protect the data — if that constraint is violated, the resulting
   `IntegrityError` is caught and converted into the same clean `409`
   response, never a raw database error message.

## 13. Troubleshooting

| Problem | Possible cause | How to check | How to fix |
|---|---|---|---|
| `connection refused` | PostgreSQL isn't running | `pg_isready` or check services | Start the PostgreSQL service |
| `database "student_registration" does not exist` | DB not created | `psql -U postgres -l` | Run `CREATE DATABASE student_registration;` |
| `password authentication failed` | Wrong password in `.env` | Check `DATABASE_URL` | Fix the password in `.env` |
| `port 5432 already in use` | Another Postgres instance running | `lsof -i :5432` (macOS/Linux) | Stop the other instance, or change the port in `DATABASE_URL` |
| `ModuleNotFoundError` | Dependencies not installed / venv not active | Check prompt shows `(venv)` | `pip install -r requirements.txt` |
| Swagger doesn't open | Server not running / wrong port | Check terminal output | Restart `uvicorn app.main:app --reload` |
| CORS error in browser console | Frontend origin not in `CORS_ORIGINS` | Check `.env` | Add `http://localhost:3000` to `CORS_ORIGINS`, restart server |
| Frontend can't reach backend | Backend not running, or wrong URL | Open `http://localhost:8000/docs` directly | Start backend; check frontend's `NEXT_PUBLIC_API_URL` |
| `422 Unprocessable Entity` | Request body fails validation | Read the `errors` array in the response | Fix the offending field(s) |
| `409 Conflict` | Duplicate email/mobile | N/A — this is expected behavior | Use a different email/mobile to test |

## 14. Bonus / optional (not required for the core assignment)

Not implemented in this version. Could be added later: `PUT /api/students/{id}`,
`DELETE /api/students/{id}`, `GET /api/students?search=...`, pagination, Docker Compose.
