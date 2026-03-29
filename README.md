# Broker Backend

This repository contains the backend/API for the broker buyer portal.

- Frontend repository: https://github.com/adhikaribibek231/broker-frontend
- Backend repository: https://github.com/adhikaribibek231/broker-backend
- Live frontend deployment: https://broker-frontend.vercel.app

This backend is responsible for:

- user registration and login
- JWT-based authentication
- storing users and favourites in the application database
- returning the logged-in user profile
- listing properties and letting a user add/remove only their own favourites

The frontend UI lives in the separate repository linked above.

## Current Deployment

- Frontend: https://broker-frontend.vercel.app
- Database in use for deployment: NeonDB (managed PostgreSQL)

The deployed backend uses a private NeonDB connection that is not shared in this repository. NeonDB is used in deployment because a managed PostgreSQL database is a better fit for hosted infrastructure: it provides persistent remote storage, survives redeploys, and handles production-style access more reliably than a local SQLite file. For anyone cloning this project, the documented setup still uses SQLite and works without NeonDB credentials.

## Tech Stack

- FastAPI
- SQLAlchemy
- NeonDB (PostgreSQL) in the private deployed environment
- SQLite for shared local development setup
- `uv` for Python/dependency management
- JWT access tokens + DB-backed refresh tokens

## What You Need Before Starting

- Git
- Internet access to install `uv` and project dependencies the first time
- A terminal

You do **not** need to install Python manually first. `uv` can install the required Python version for you.

## Step-By-Step Setup For A New User

### 1. Clone the repository

```bash
git clone https://github.com/adhikaribibek231/broker-backend.git
cd broker-backend
```

### 2. Install `uv`

Official installation guide: https://docs.astral.sh/uv/getting-started/installation/

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, close and reopen your terminal, then confirm it works:

```bash
uv --version
```

### 3. Install Python 3.13 through `uv`

This project is pinned for Python `3.13`.

```bash
uv python install 3.13
```

### 4. Create your `.env` file

Copy the example file:

macOS / Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then open `.env` and set the values you want.

Example `.env`:

```env
APP_DISPLAY_NAME=Broker Buyer Portal API
APP_ENV=dev
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./app.db
DATABASE_CONNECT_TIMEOUT=5
AUTO_CREATE_SCHEMA=true
JWT_SECRET_KEY=replace-this-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

The example above intentionally keeps `DATABASE_URL` on SQLite. The deployed environment uses a private NeonDB connection string, but that value is not shared and is not required to run the project locally.

### 5. What each `.env` value means

- `APP_DISPLAY_NAME`: The API name shown in logs and docs.
- `APP_ENV`: Use `dev` for local development.
- `LOG_LEVEL`: `INFO` is a good default.
- `DATABASE_URL`: Keep `sqlite:///./app.db` for the documented setup and simplest local run. In the private deployed environment, this is set to a NeonDB PostgreSQL connection string instead.
- `DATABASE_CONNECT_TIMEOUT`: Database connection timeout in seconds.
- `AUTO_CREATE_SCHEMA`: `true` lets the app create tables automatically on startup.
- `JWT_SECRET_KEY`: A long random secret used to sign JWTs. Do not reuse a weak value.
- `JWT_ALGORITHM`: Keep `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: How long the access token lasts.
- `REFRESH_TOKEN_EXPIRE_DAYS`: How long the refresh token lasts.

You can use any long random string. If you already have a working `python` command, you can generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it into `JWT_SECRET_KEY`.

### 6. Install dependencies

```bash
uv sync
```

This creates the virtual environment and installs all required packages.

### 7. Seed sample properties

The buyer dashboard needs properties in the database so a user can favourite them.

```bash
uv run python scripts/seed_properties.py
```

If you run this more than once, it will safely skip duplicate seeding.

### 8. Start the backend server

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once it starts, open:

- API base URL: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

## How To Run The Full Feature With The Frontend

1. Start this backend.
2. Start the frontend from `https://github.com/adhikaribibek231/broker-frontend`.
3. Open the frontend in the browser.
4. Register a new user.
5. Log in with that user.
6. Open the dashboard.
7. Add a property to favourites.
8. Remove it again to confirm the full flow works.

## Example Flow

1. Register with `name`, `username`, `email`, and `password`.
2. Log in with `email` and `password`.
3. Open `My Favourites` in the dashboard.
4. Save one of the seeded properties.
5. Refresh the page and confirm the favourite is still there.
6. Remove the favourite and confirm it disappears.

## Main API Routes

- `POST /api/v1/public/auth/register`
- `POST /api/v1/public/auth/login`
- `POST /api/v1/public/auth/refresh`
- `POST /api/v1/public/auth/logout`
- `GET /api/v1/public/auth/me`
- `GET /api/v1/public/properties`
- `GET /api/v1/public/properties/{property_id}`
- `GET /api/v1/public/favorites/`
- `POST /api/v1/public/favorites/`
- `DELETE /api/v1/public/favorites/{property_id}`

## Run Tests

```bash
uv run python -m unittest discover -s tests
```

## Notes

- `.env` is ignored by git and should not be committed.
- This repository covers the backend/API layer of the broker portal.
- For the UI, use the frontend repository linked at the top of this README.
