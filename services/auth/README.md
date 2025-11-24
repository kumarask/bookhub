# Auth Service

A lightweight authentication service built with **FastAPI**, **SQLAlchemy**, and **Redis**.  
Provides user registration, login, JWT-based authentication, refresh tokens, and role-based access control. Includes a stub Pub/Sub helper for domain events.

**Author:** Kumara S K

---

## Features

- User registration, login, and profile management
- JWT access and refresh tokens
- Secure password hashing (bcrypt)
- Role-based access control (admin / user)
- SQLAlchemy ORM for PostgreSQL
- Redis integration for caching or token management
- Lightweight Pub/Sub system (stub mode for development)
- Health check endpoint
- Fully typed with Pydantic schemas
- FastAPI dependency injection for DB, Redis, and current user

---

## Project Structure
```
auth-service/
├── app/
│ ├── api/
│ │ └── v1/
│ │ ├── auth.py # Auth API endpoints
│ │ └── user.py # User API endpoints
│ ├── config.py # Environment variables and service settings
│ ├── database.py # SQLAlchemy engine and session setup
│ ├── dependencies.py # FastAPI dependency helpers
│ ├── main.py # FastAPI application entrypoint
│ ├── models/
│ │ ├── user.py # User SQLAlchemy model
│ │ └── refresh_token.py # RefreshToken model
│ ├── schemas/
│ │ ├── auth.py # Auth request/response schemas
│ │ └── user.py # User request/response schemas
│ ├── security/
│ │ ├── hashing.py # Password hashing utilities
│ │ └── jwt.py # JWT token utilities
│ ├── services/
│ │ ├── auth_service.py # Business logic for login, registration
│ │ ├── token_service.py # Refresh token handling
│ │ └── user_service.py # User-related business logic
│ └── pubsub.py # Lightweight Pub/Sub helper
└── README.md
```
---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/auth-service.git
cd auth-service
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables (optional, defaults are provided):

```bash
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="your_jwt_secret"
export ACCESS_TOKEN_EXPIRE_MINUTES=60
export REFRESH_TOKEN_EXPIRE_DAYS=7
export PUBSUB_MODE="stub"
```

## Running the Service

1. Start the FastAPI server:

``` bash
uvicorn app.main:app --reload
```

2. Access API documentation at:

```bash
http://localhost:8000/docs
```

3. Health check endpoint:

```bash
GET /health
Response: {"status": "healthy"}
```
## Usage

1. Authentication Endpoints
**Register:** POST /api/v1/auth/register
**Login:** POST /api/v1/auth/login
**Refresh Token:** POST /api/v1/auth/refresh
**Logout:** POST /api/v1/auth/logout

2. User Endpoints
**Get Current User:** GET /api/v1/user/me
**Update Profile:** PUT /api/v1/user/me

## Security
* Passwords are hashed using bcrypt.
* JWT tokens are used for authentication:
* Access tokens expire quickly (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)
* Refresh tokens allow long-lived sessions (configurable via REFRESH_TOKEN_EXPIRE_DAYS)
* Role-based access control is supported (admin vs regular users).

## Pub/Sub
* app/pubsub.py provides a stub interface for publishing events.
* Currently supports stub mode for development.
* Can be extended to use GCP Pub/Sub, Kafka, or other systems.

## Example usage:

```python
from app.pubsub import publish
import asyncio

asyncio.run(publish("user.registered", {"user_id": "1234"}))
```

## Contributing
* Fork the repository.
* Create a new branch: git checkout -b feature/my-feature
* Commit your changes: git commit -am 'Add new feature'
* Push to the branch: git push origin feature/my-feature
* Open a Pull Request.

## License
This project is licensed under the MIT License.

**Author:** Kumara S K
