from fastapi import FastAPI
from app.api.v1 import books, categories

app = FastAPI(title="Books Service", version="1.0")

app.include_router(books.router)
app.include_router(categories.router)
