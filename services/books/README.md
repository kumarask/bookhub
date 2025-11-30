# Books Service

This service manages books and categories, providing CRUD operations
and caching for efficient access. It is built using **FastAPI**,
**SQLAlchemy**, **PostgreSQL**, and **Redis**.

## Service Details

- **Service Name:** Books Service
- **API Version:** 1.0
- **Port:** 8002
- **Dependencies:** PostgreSQL, Redis

## Running the Service

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Configure environment variables (example .env)**:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/booksdb
REDIS_URL=redis://localhost:6379
INTERNAL_SECRET=your-internal-secret
```

3. **Start the service**:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

4. **The service will now be accessible at**:
```bash
http://localhost:8002
```

5. **API Endpoints**
/api/v1/books/ – CRUD operations for books
/api/v1/categories/ – CRUD operations for categories


**Notes**
Internal service calls require the `X-Internal-Secret` header.
Cached book data is stored in Redis for faster retrieval.
