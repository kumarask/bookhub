import os


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
REDIS_URL = "redis://localhost:6379"
DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/booksdb"
INTERNAL_SECRET = "supersecretinternalkey"
