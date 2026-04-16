# Discards

## 2026-04-16
- **CSV for inventory**: Too many entries (\u003e10k). Not scalable.
- **Flat file JSON**: Would require manual parsing and not efficient for queries.
- **External DB (PostgreSQL/MySQL)**: Adds deployment complexity; SQLite suffices.
- **ORM-less raw SQL**: Harder to maintain; SQLAlchemy provides abstraction.
- **Monolithic API**: Would mix business logic with persistence; split into modules.
- **Docker Compose**: Overkill for local dev; use virtualenv.

## 2026-04-17
- **GraphQL**: Adds unnecessary complexity for simple CRUD.
- **Celery for async tasks**: Not needed for current workload.
- **WebSocket API**: Not required.

## 2026-04-18
- **React frontend**: Project is backend focused; UI not in scope.
- **TypeScript**: Python is primary language.
- **CI/CD pipeline**: Will be added later.
