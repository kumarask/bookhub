from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    description: Optional[str] = None
    price: float
    stock_quantity: Optional[int] = 0
    category: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[date] = None

class BookCreate(BookBase):
    created_at: Optional[date] = None

class BookUpdate(BaseModel):
    price: Optional[float]
    stock_quantity: Optional[int]
    description: Optional[str]

class BookOut(BaseModel):
    id: UUID
    title: str
    author: str
    isbn: str
    price: float
    stock_quantity: int
    category: Optional[str] = None

    class Config:
        from_attributes = True

class CategoryOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    book_count: Optional[int] = 0

    class Config:
        from_attributes = True


class BookListOut(BaseModel):
    items: list[BookOut]
    total: int
    page: int
    limit: int
    pages: int


class BookDetailOut(BaseModel):
    id: UUID
    title: str
    author: str
    isbn: str
    description: Optional[str]
    price: float
    stock_quantity: int
    category: Optional[str]
    publisher: Optional[str]
    published_date: Optional[date]
    average_rating: Optional[float] = 0.0
    review_count: Optional[int] = 0

    class Config:
        from_attributes = True


class BookStockUpdate(BaseModel):
    quantity_change: int

class BookStockOut(BaseModel):
    id: UUID
    stock_quantity: int
    updated_at: datetime

    class Config:
        from_attributes = True