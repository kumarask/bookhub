"""
API Gateway for all microservices.

This gateway serves as the central entry point for all client requests
and provides the following features:

1. Request Routing:
   - Routes requests to the appropriate microservice (auth, books, orders, reviews)
   - Preserves HTTP method, headers, query parameters, and request body

2. Authentication:
   - Validates JWT tokens using the `get_current_user` dependency
   - Attaches user information to requests for downstream services

3. Rate Limiting:
   - Enforces Redis-based rate limits based on user type (unauthenticated, authenticated, admin)

4. Request/Response Logging:
   - Can be extended to log all incoming requests and proxied responses

5. CORS Handling:
   - Configured to allow requests from any origin with all standard HTTP methods and headers

6. Health Check:
   - `/health` endpoint checks the status of all microservices
   - Returns overall gateway status and individual service health

Routes:
- `/api/v1/{service}/{path:path}`: Proxies all requests to the corresponding microservice
  - Supported services: `auth`, `books`, `orders`, `reviews`
  - Supports GET, POST, PUT, DELETE methods
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime
from app.deps import get_current_user
from app.rate_limiter import rate_limit
from app.config import (
    AUTH_SERVICE_URL,
    BOOKS_SERVICE_URL,
    ORDERS_SERVICE_URL,
    REVIEWS_SERVICE_URL,
)

app = FastAPI(title="API Gateway", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def proxy_request(service_url: str, request: Request):
    """
    Proxy an incoming request to the target microservice.

    Args:
        service_url (str): Base URL of the target microservice.
        request (Request): FastAPI Request object representing the incoming client request.

    Returns:
        httpx.Response: Response received from the proxied microservice.
    """
    async with httpx.AsyncClient() as client:
        url = f"{service_url}{request.url.path.replace('/api/v1', '')}"
        headers = dict(request.headers)

        # Forward form data correctly
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            response = await client.request(
                request.method,
                url,
                headers=headers,
                data=form,
                params=request.query_params,
            )
        else:
            body = await request.body()
            response = await client.request(
                request.method,
                url,
                headers=headers,
                content=body,
                params=request.query_params,
            )

        return response


@app.get("/health")
async def health_check():
    """
    Perform a health check for the API Gateway and all registered microservices.

    Returns:
        dict: Health status containing:
            - "status": Overall gateway status
            - "services": Dictionary mapping each microservice name to "healthy" or "unhealthy"
            - "timestamp": Current UTC timestamp in ISO 8601 format
    """
    services = {}
    for name, url in [
        ("auth", AUTH_SERVICE_URL),
        ("books", BOOKS_SERVICE_URL),
        ("orders", ORDERS_SERVICE_URL),
        ("reviews", REVIEWS_SERVICE_URL),
    ]:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{url}/health")
                services[name] = "healthy" if r.status_code == 200 else "unhealthy"
        except:  # noqa: E722
            services[name] = "unhealthy"
    return {
        "status": "healthy",
        "services": services,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.api_route(
    "/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def gateway_route(
    service: str, path: str, request: Request, user=Depends(get_current_user)
):
    """
    Generic route to proxy requests to appropriate microservices.

    Performs rate limiting and authentication before forwarding requests.

    Args:
        service (str): Target microservice name (auth, books, orders, reviews)
        path (str): Path of the request to forward to the microservice
        request (Request): FastAPI Request object
        user (dict, optional): Authenticated user info provided by dependency injection

    Returns:
        tuple: JSON response from microservice and the HTTP status code

    Raises:
        HTTPException: If rate limit is exceeded or service name is unknown
    """
    await rate_limit(request, user)

    if service == "auth":
        url = AUTH_SERVICE_URL
    elif service == "books":
        url = BOOKS_SERVICE_URL
    elif service == "orders":
        url = ORDERS_SERVICE_URL
    elif service == "reviews":
        url = REVIEWS_SERVICE_URL
    else:
        return {"error": "Unknown service"}

    response = await proxy_request(url, request)
    return response.json(), response.status_code
