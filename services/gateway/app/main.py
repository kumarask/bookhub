"""API Gateway service.

This module implements a lightweight HTTP gateway that forwards requests
to internal services (auth, books, orders, reviews) based on path
prefixes defined in ``SERVICE_MAP``. It also implements a simple
rate-limiting middleware backed by Redis via :class:`RateLimiter`.

Design notes:
- The gateway preserves request headers (except ``Host``) and forwards
    request bodies and query parameters to the target service.
- Health checks call each service's health endpoint and aggregate
    results to provide an overall view used by orchestration tooling.
- The proxy is intentionally simple and does not perform request
    transformation, authentication, or advanced routing. Extend with
    authentication, tracing, or circuit-breaker behavior as needed.
"""

import os
import time

import httpx
from fastapi import FastAPI, HTTPException, Request, Response

from .rate_limiter import RateLimiter

app = FastAPI(title="API Gateway")

SERVICE_MAP = {
    "/api/v1/auth": "http://auth:8001/api/v1/auth",
    "/api/v1/books": "http://books:8002/api/v1/books",
    "/api/v1/orders": "http://orders:8003/api/v1/orders",
    "/api/v1/reviews": "http://reviews:8004/api/v1/reviews",
}

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
rate_limiter = RateLimiter(redis_url=redis_url)


@app.get("/health")
def health():
    """Health check for the gateway and downstream services.

    Calls the health endpoint of each mapped service and returns an
    aggregate view including per-service health statuses and a timestamp.

    Returns:
        dict: overall status, per-service statuses and a timestamp string
            in UTC.
    """
    services = {}
    for name, url in SERVICE_MAP.items():
        try:
            r = httpx.get(url.replace("/api/v1", "") + "/health", timeout=2.0)
            services[name.split("/")[-1]] = (
                "healthy" if r.status_code == 200 else "unhealthy"
            )
        except Exception:
            services[name.split("/")[-1]] = "unhealthy"
    return {
        "status": "healthy",
        "services": services,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


@app.middleware("http")
async def throttle(request: Request, call_next):
    """Rate-limiting middleware.

    Determines an identity for the request (prefer an authorization header
    value, otherwise the client IP) and asks :class:`RateLimiter` whether
    the request should be allowed. If not allowed a 429 is raised.

    This middleware should be lightweight and non-blocking so it runs for
    every incoming HTTP request.
    """
    identity = request.headers.get("authorization") or request.client.host
    allowed = await rate_limiter.allow_request(identity)
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests")
    return await call_next(request)


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(full_path: str, request: Request):
    """Catch-all proxy that forwards requests to internal services.

    The route receives any path and method and forwards it to the
    appropriate backend service based on prefix matching against
    ``SERVICE_MAP``. Request headers (except Host), body and query
    parameters are forwarded. The backend response content, status code
    and headers are returned verbatim.

    Args:
        full_path (str): the full path captured by the catch-all route.
        request (Request): the incoming FastAPI request object.

    Returns:
        Response: a FastAPI Response constructed from the upstream service
            response.

    Raises:
        HTTPException: 404 when no backend matches the requested path.
    """
    path = "/" + full_path
    for prefix, target in SERVICE_MAP.items():
        if path.startswith(prefix):
            suffix = path[len(prefix) :]
            url = target + suffix
            async with httpx.AsyncClient() as client:
                headers = {
                    k: v for k, v in request.headers.items() if k.lower() != "host"
                }
                body = await request.body()
                resp = await client.request(
                    request.method,
                    url,
                    headers=headers,
                    content=body,
                    params=request.query_params,
                )
            return Response(
                content=resp.content, status_code=resp.status_code, headers=resp.headers
            )
    raise HTTPException(status_code=404, detail="Not found")
