# API Gateway Service

## Overview
The API Gateway is the central entry point for all microservices in the system. It handles routing, authentication, rate limiting, logging, and CORS. All client requests go through this service, which forwards them to the appropriate microservice.

**Port:** `8000`  
**Tech Stack:** FastAPI, Redis, HTTPX

---

## Features

1. **Request Routing**  
   Routes requests to the appropriate microservice:
   - `auth` → Auth Service (`8001`)
   - `books` → Books Service (`8002`)
   - `orders` → Orders Service (`8003`)
   - `reviews` → Reviews Service (`8004`)

2. **Authentication**  
   Validates JWT tokens before forwarding requests.  
   Unauthorized requests return `401`.

3. **Rate Limiting** (Redis-based)  
   Limits requests to prevent abuse:
   - Unauthenticated requests: 20 requests/min/IP  
   - Authenticated users: 100 requests/min/user  
   - Admin users: 500 requests/min/user

4. **Logging**  
   Logs all incoming requests and outgoing responses.

5. **CORS Handling**  
   Allows cross-origin requests for frontend applications.

6. **Health Check**  
   Endpoint: `GET /health`  
   Returns status of all microservices:
   ```json
   {
     "status": "healthy",
     "services": {
       "auth": "healthy",
       "books": "healthy",
       "orders": "healthy",
       "reviews": "healthy"
     },
     "timestamp": "2025-10-22T15:00:00Z"
   }

**Environment Variables**
---

-------------------------------------------------------------------------------------------------
|  Variable	         |   Description	                                |   Default             |
-------------------------------------------------------------------------------------------------
| AUTH_SERVICE_URL	 |  URL of the Auth Service	                        |   http://auth:8001    |
| BOOKS_SERVICE_URL	 |  URL of the Books Service	                    |   http://books:8002   |
| ORDERS_SERVICE_URL |	URL of the Orders Service	                    |   http://orders:8003  |
| REVIEWS_SERVICE_URL|	URL of the Reviews Service	                    |   http://reviews:8004 |
| REDIS_URL	         |  Redis connection URL for caching & rate limiting|   redis://redis:6379/0|
| JWT_SECRET_KEY	 |  Secret key for JWT validation	                |   supersecret         |
-------------------------------------------------------------------------------------------------

**API Endpoints**
All microservice endpoints are accessible via the gateway under /api/v1/{service}/...

*Examples*:

`GET /api/v1/auth/login` → Auth Service
`GET /api/v1/books/` → Books Service
`POST /api/v1/orders/` → Orders Service
`GET /api/v1/reviews/book/{book_id}` → Reviews Service

**Health Check**:
GET /health

**Rate Limiting**
Uses Redis to store request counters.
Unauthenticated: 20 requests/min/IP
Authenticated: 100 requests/min/user
Admin: 500 requests/min/user
Returns `429 Too Many Requests` if exceeded.

**Running Locally**
Clone the repository:

```bash
git clone <repo-url>
cd <repo-folder>
```

**Create a virtual environment and install dependencies**:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Set environment variables (optional, defaults will be used if not set)**:

```bash
export AUTH_SERVICE_URL=http://localhost:8001
export BOOKS_SERVICE_URL=http://localhost:8002
export ORDERS_SERVICE_URL=http://localhost:8003
export REVIEWS_SERVICE_URL=http://localhost:8004
export REDIS_URL=redis://localhost:6379/0
export JWT_SECRET_KEY=supersecret
```

**Run the gateway**:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Docker**
---

**Dockerfile included for containerized deployment**:

```dockerfile
FROM python:3.12-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Build and run**:

```bash
docker build -t api-gateway .
docker run -p 8000:8000 --env-file .env api-gateway
```

**Dependencies**

FastAPI
HTTPX (async HTTP requests)
Redis (asyncio)
python-jose (JWT)
Uvicorn

**Notes**
Make sure all microservices are running before starting the gateway.
Redis is required for caching and rate limiting.
JWT secret key must match the one used in Auth Service.