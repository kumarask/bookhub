from sqlalchemy.orm import Session
from app.models import books, categories
from app import schemas

def create_book(db: Session, book: schemas.BookCreate):
    # Check ISBN
    if db.query(books.Book).filter(books.Book.isbn == book.isbn).first():
        raise ValueError("ISBN already exists")
    
    # Validate category exists
    category_obj = None
    if book.category:
        category_obj = db.query(categories.Category).filter(categories.Category.name == book.category).first()
        if not category_obj:
            raise ValueError("Category does not exist")
    
    db_book = books.Book(
        **book.dict(exclude={"category"}),
        category_id=category_obj.id if category_obj else None
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_book(db: Session, book_id: str):
    return db.query(books.Book).filter(books.Book.id == book_id).first()

def list_books(db: Session, skip: int = 0, limit: int = 20):
    return db.query(books.Book).offset(skip).limit(limit).all()

def update_book(db: Session, db_book: books.Book, updates: schemas.BookUpdate):
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, db_book: books.Book):
    db.delete(db_book)
    db.commit()
