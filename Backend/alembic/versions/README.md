# Database Migrations

This directory contains Alembic migration files for the Campaign Performance Optimization Platform.

## Usage

Generate a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Downgrade migrations:
```bash
alembic downgrade -1
``` 