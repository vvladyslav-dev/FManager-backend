# FManager Backend

REST API for a dynamic form management system with role-based access control and real-time Telegram notifications.

The application enables administrators to create custom forms with various field types (text, email, file uploads, etc.), manage user permissions, and track form submissions. Forms can be shared publicly via unique links, allowing anyone to submit responses without authentication. When a user submits a form, the system stores the data in PostgreSQL, uploads files to Azure Blob Storage, and sends instant notifications to designated Telegram channels, allowing teams to respond quickly to new entries.

## Technologies

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker & Docker Compose

## Quick Start

### Environment Setup

Create `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fmanager_db
SECRET_KEY=your-secret-key
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string

# Optional - Telegram Bot (leave empty to disable)
TELEGRAM_BOT_TOKEN=
FRONTEND_URL=http://localhost:3000
```

### Run Locally

```bash
# Start services
docker compose up

# Run migrations
docker compose exec backend alembic upgrade head
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## CI/CD Pipeline

The project uses **GitHub Actions** for automated deployment to Azure.

**Pipeline workflow** (`.github/workflows/deploy.yml`):
1. Build Docker image
2. Push to Azure Container Registry
3. Deploy to Azure Container Apps

**Triggers:** Push to `main` branch

### Database Migrations in Production

⚠️ Currently, production database migrations are applied **manually** 

Future improvement: Automate migrations via entrypoint script or init container.

## Development

### Project Structure

```
app/
├── api/              # API routes and schemas
├── application/      # Use cases and handlers
├── core/            # Configuration, DI container
├── domain/          # Domain models, events, repositories
└── infrastructure/  # Repository implementations, external services
```

### Useful Commands

```bash
# View logs
docker compose logs -f backend

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Run tests
docker compose exec backend pytest

# Connect to database
docker compose exec db psql -U postgres -d fmanager_db
```
