# FManager Backend

Backend API for form management system.

## Technologies

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker & Docker Compose

## Installation and Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd FManager-backend
```

### 2. Environment variables setup

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fmanager_db
SECRET_KEY=your-secret-key
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string
```

### 3. Run with Docker

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f backend

# Stop services
docker compose down
```

API will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## Working with Alembic Migrations

### Apply migrations (upgrade)

```bash
# Apply all migrations to the latest version
docker compose exec backend alembic upgrade head

# Apply one migration forward
docker compose exec backend alembic upgrade +1

# Apply migration to a specific version
docker compose exec backend alembic upgrade <revision_id>
```

### Rollback migrations (downgrade)

```bash
# Rollback all migrations
docker compose exec backend alembic downgrade base

# Rollback one migration
docker compose exec backend alembic downgrade -1

# Rollback to a specific version
docker compose exec backend alembic downgrade <revision_id>
```

### Create a new migration

```bash
# Auto-generate migration based on model changes
docker compose exec backend alembic revision --autogenerate -m "migration_description"

# Create an empty migration
docker compose exec backend alembic revision -m "migration_description"
```

### View migration history

```bash
# Show current database version
docker compose exec backend alembic current

# Show migration history
docker compose exec backend alembic history

# Show details of a specific migration
docker compose exec backend alembic show <revision_id>
```

## Development

### Project structure

```
app/
├── api/              # API endpoints and schemas
├── application/      # Application layer (handlers)
├── core/            # Configuration and dependencies
├── domain/          # Domain models and repositories (interfaces)
└── infrastructure/  # Repository implementations
```

### Run tests

```bash
# Run all tests
docker compose exec backend pytest

# Run with coverage
docker compose exec backend pytest --cov=app

# Run a specific test
docker compose exec backend pytest tests/test_form_management.py
```

### Connect to database

```bash
# Connect to PostgreSQL via psql
docker compose exec db psql -U postgres -d fmanager_db
```

## Useful commands

```bash
# Rebuild containers
docker compose up --build

# View running containers
docker compose ps

# View logs of a specific service
docker compose logs -f backend
docker compose logs -f db

# Stop and remove all containers with volumes
docker compose down -v

# Execute a command inside a container
docker compose exec backend <command>
```

## Troubleshooting

### Migration issues

If migrations don't apply or conflicts occur:

```bash
# 1. Check current database version
docker compose exec backend alembic current

# 2. View migration history
docker compose exec backend alembic history

# 3. Rollback and reapply if necessary
docker compose exec backend alembic downgrade base
docker compose exec backend alembic upgrade head
```

### Database connection issues

```bash
# Check container status
docker compose ps

# Check database logs
docker compose logs db

# Restart services
docker compose restart
```
