# Client Onboarding Portal

An internal portal that lets staff onboard and manage client organisations and their contacts
in one centralised system, replacing spreadsheets and email threads.

## Features
- **Staff login** (JWT) with roles: `admin` (full access, can delete organisations and create users)
  and `staff` (create, view and edit)
- **Organisation CRUD** with business details, registration number, contact details and a
  structured UK postal address
- **Search and filter** by name, email, registration number, city or postcode, and by status
- **Multiple contacts per organisation** with name, job title, email, phone, contact type
  (general, billing, technical, legal, other) and a primary contact; full contact CRUD via the UI
  and dedicated API endpoints
- **UK address lookup:** type an address or postcode, choose a suggestion, and the structured
  address (line 1, city, county, postcode, country) is saved against the organisation
- Input validation (frontend and backend) and clear error messages

## Tech stack
React (Vite) · Python FastAPI · PostgreSQL · SQLAlchemy · Alembic · PyJWT · bcrypt · httpx

## Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 14+

## Setup

### 1. Database
Create an empty PostgreSQL database named `client_onboarding_db` (for example in pgAdmin).

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
python -m pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env
```
Edit `backend/.env`:

| Variable | Description |
|---|---|
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | PostgreSQL connection settings |
| `SECRET_KEY` | JWT signing key. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 480) |
| `ALLOWED_ORIGINS` | Allowed frontend origins (default `http://localhost:5173`) |
| `GEOAPIFY_API_KEY` | Optional, see "Address lookup" below |

Then:
```bash
python -m alembic upgrade head   # create the tables
python create_admin.py           # create the first admin user (prompts for name, email, password)
python seed.py                   # optional sample data
python -m uvicorn app.main:app --reload
```
The API runs at http://127.0.0.1:8000 and interactive docs are at http://127.0.0.1:8000/docs.

### 3. Frontend
```bash
cd frontend
npm install
copy .env.example .env           # macOS/Linux: cp .env.example .env
npm run dev
```
Open http://localhost:5173 and sign in with the admin account you created.

## Address lookup
The frontend calls the backend endpoint `GET /addresses/search?q=...`, and the backend calls the
external service, so no API key is ever exposed to the browser and the endpoint requires login.

- **Default (no setup):** [Photon](https://photon.komoot.io), a free OpenStreetMap-based geocoder.
  Results are restricted to the UK.
- **With an API key (recommended for production):** set `GEOAPIFY_API_KEY` in `backend/.env`
  (free key from https://myprojects.geoapify.com) and the backend automatically switches to the
  Geoapify Autocomplete API.
- If the service is unavailable, the form shows a message and the address can still be entered manually.

Note: OpenStreetMap data is not as complete as the Royal Mail address file, so some house numbers
may be missing from suggestions; all fields remain editable after selecting a suggestion.

## Roles
| Action | staff | admin |
|---|---|---|
| View / search organisations | yes | yes |
| Create / edit organisations and contacts | yes | yes |
| Delete organisations | no | yes |
| Create users | no | yes |

New users are created by an admin via `POST /auth/users` (Swagger docs).

## API overview
| Area | Endpoints |
|---|---|
| Auth | `POST /auth/login`, `GET /auth/me`, `GET/POST /auth/users` (admin) |
| Organisations | `GET/POST /organisations`, `GET/PUT/DELETE /organisations/{id}` |
| Contacts | `GET/POST /organisations/{id}/contacts`, `GET/PUT/DELETE /contacts/{id}` |
| Address lookup | `GET /addresses/search?q=...` |

## Design decisions
- Alembic manages schema migrations rather than manual SQL.
- Role checks are enforced on the backend, not just hidden in the UI.
- Pydantic schemas validate all input (email format, lengths, enums, UK postcode pattern, a single
  primary contact, unique registration number).
- Secrets live in git-ignored `.env` files; `.env.example` files document the settings.

## Possible improvements
Pagination, audit log, user management screens, automated tests, and deployment.