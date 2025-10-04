# Moduł Administracyjny

FastAPI microservice for PostgreSQL database management.

## Installation

```bash
pip install -r requirements.txt
```

## Database Setup

1. Apply migration to your PostgreSQL database:
```bash
psql -U your_user -d your_database -f migrations/001_initial_schema.sql
```

2. Set DATABASE_URL environment variable:
```bash
export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/dbname"
```

## Running

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

## Endpoints

- `GET /` - Application status
- `GET /healthz` - Health check with database connection verification

## API Documentation

Available after startup at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

