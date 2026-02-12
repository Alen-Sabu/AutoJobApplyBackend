# AutoJobApply API

A FastAPI-based automated job application system.

## Features

- User authentication and authorization
- User profile management
- Job search and saving
- Job application tracking
- RESTful API with OpenAPI documentation

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── api/
│   ├── __init__.py
│   ├── dependencies.py     # Shared dependencies (auth, etc.)
│   └── v1/
│       ├── __init__.py
│       ├── api.py          # Main API router
│       └── endpoints/
│           ├── __init__.py
│           ├── auth.py     # Authentication endpoints
│           ├── profiles.py # Profile endpoints
│           ├── jobs.py     # Job endpoints
│           └── applications.py # Application endpoints
├── core/
│   ├── __init__.py
│   ├── config.py          # Application settings
│   └── database.py         # Database configuration
├── models/
│   ├── __init__.py
│   ├── user.py            # User model
│   ├── profile.py         # Profile model
│   ├── job.py             # Job model
│   └── application.py     # Application model
├── schemas/
│   ├── __init__.py
│   ├── auth.py           # Authentication schemas
│   ├── profile.py        # Profile schemas
│   ├── job.py            # Job schemas
│   └── application.py    # Application schemas
├── services/
│   ├── __init__.py
│   ├── auth_service.py      # Authentication service
│   ├── profile_service.py   # Profile service
│   ├── job_service.py       # Job service
│   └── application_service.py # Application service
└── utils/
    ├── __init__.py
    └── logger.py          # Logging configuration
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. **PostgreSQL**: The app uses PostgreSQL. Install [PostgreSQL](https://www.postgresql.org/download/) and create a database:
   ```bash
   # In psql or pgAdmin: create database and (optional) user
   CREATE DATABASE autojobapply;
   ```
   Copy `.env.example` to `.env` and set `DATABASE_URL`:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/autojobapply
   SECRET_KEY=your-secret-key-here
   ```

## Running the Application

1. Apply database migrations (from project root):
   ```bash
   cd app
   alembic upgrade head
   cd ..
   ```

2. Run the development server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   Or with the venv’s Python: `autoenv\Scripts\python.exe -m uvicorn app.main:app --reload`

3. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token

### Profiles
- `GET /api/v1/profiles/me` - Get current user's profile
- `POST /api/v1/profiles/` - Create a profile
- `PUT /api/v1/profiles/me` - Update current user's profile

### Jobs
- `GET /api/v1/jobs/search` - Search for jobs
- `GET /api/v1/jobs/` - Get saved jobs
- `POST /api/v1/jobs/` - Save a job
- `GET /api/v1/jobs/{job_id}` - Get a specific job
- `DELETE /api/v1/jobs/{job_id}` - Delete a saved job

### Applications
- `GET /api/v1/applications/` - Get user's applications
- `POST /api/v1/applications/` - Create an application
- `GET /api/v1/applications/{application_id}` - Get a specific application
- `PUT /api/v1/applications/{application_id}` - Update an application
- `POST /api/v1/applications/{application_id}/submit` - Submit an application
- `DELETE /api/v1/applications/{application_id}` - Delete an application

## Development

The application uses:
- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **Pydantic** for data validation
- **JWT** for authentication
- **SQLite** as the default database (can be changed to PostgreSQL, MySQL, etc.)

## License

MIT

