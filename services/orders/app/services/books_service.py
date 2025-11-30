"""
app.services.books_service

BooksService module.

Provides a service class for interacting with the external Books service.
Handles operations such as retrieving book details and updating stock
via HTTP requests to the Books service API.

Classes:
- BooksService: Async client for communicating with the Books service.
"""

import httpx
from uuid import UUID
from app.config import BOOKS_SERVICE_URL


class BooksService:
    """
    Service client for interacting with the Books service API.

    Methods
    -------
    get_book(book_id: UUID)
        Fetch detailed information of a book by its ID.
    update_stock(book_id: UUID, quantity_change: int)
        Update the stock quantity of a specific book.
    """

    async def get_book(self, book_id: UUID):
        """
        Retrieve book details from the Books service.

        Args:
            book_id (UUID): Unique identifier of the book.

        Returns:
            dict | None: Returns book details as a dictionary if found,
                         otherwise None.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BOOKS_SERVICE_URL}/api/v1/books/{book_id}")
            if resp.status_code == 200:
                return resp.json()
            return None

    async def update_stock(self, book_id: UUID, quantity_change: int):
        """
        Update the stock quantity of a book.

        Sends a PATCH request to the Books service to adjust stock.

        Args:
            book_id (UUID): Unique identifier of the book.
            quantity_change (int): Positive or negative quantity to adjust stock.

        Returns:
            bool: True if the update was successful (status code 200), False otherwise.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                f"{BOOKS_SERVICE_URL}/api/v1/books/{book_id}/stock",
                json={"quantity_change": quantity_change},
            )
            return resp.status_code == 200
