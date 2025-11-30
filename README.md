# BookHub — Microservices Sample

This repository contains a full working scaffold for the BookHub capstone:
- FastAPI microservices: Auth (8001), Books (8002), Orders (8003), Reviews (8004)
- API Gateway (8000)
- PostgreSQL and Redis via docker-compose
- Pub/Sub stub with instructions to plug GCP Pub/Sub
- Dockerfile for each service and docker-compose to run everything locally

## Quick start (local)

1. Copy `.env.example` -> `.env` and fill values (at least POSTGRES_* and JWT_SECRET).
2. Create required DBs before services start (or use the provided helper):
   - authdb, booksdb, ordersdb, reviewsdb
   Example:
   ```bash
   docker compose up -d postgres
   docker compose exec postgres psql -U postgres -c "CREATE DATABASE authdb;"
   docker compose exec postgres psql -U postgres -c "CREATE DATABASE booksdb;"
   docker compose exec postgres psql -U postgres -c "CREATE DATABASE ordersdb;"
   docker compose exec postgres psql -U postgres -c "CREATE DATABASE reviewsdb;"
   ```
3. Verify databases exist
   ```bash
   docker compose exec postgres psql -U postgres -c "\l"
   ```
4. Start all services
   ```bash
   docker compose build --no-cache
   docker compose up --build
   ```
5. Check logs if a service fails:
   ```bash
   docker compose ps
   docker compose logs auth --tail 200
   docker compose logs books --tail 200
   ```
6. Open Swagger docs:
   - Gateway: http://localhost:8000/docs
   - Auth: http://localhost:8001/docs
   - Books: http://localhost:8002/docs
   - Orders: http://localhost:8003/docs
   - Reviews: http://localhost:8004/docs

## Code Format
1. Install ruff into your environment
   ```bash
   pip install -r requirements-dev.txt
   ```
2. Run ruff checks and/or autoformat:
   ```bash
   ruff check services
   ```
3. Fix formatting automatically:
   ```bash
   ruff format services
   ruff check services
   ```
## Notes
- The project uses a Pub/Sub **stub** by default for local development. Set `PUBSUB_MODE=gcp` and provide credentials to use real GCP Pub/Sub.
- Redis is used for caching and rate-limiting.
- Each service exposes endpoints under `/api/v1/<service>/*`.
- Internal service communication uses `X-Internal-Secret` header.

See each service `services/<name>/README.md` for more details.
