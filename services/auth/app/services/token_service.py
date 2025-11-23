from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken


def create_refresh_token(user_id: str, db: Session, expires_in: int = 3600*24*7) -> str:
    """
    Create a new refresh token for a user and store it in DB.
    """
    import secrets

    token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    r = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r.token

def verify_refresh_token(token: str, db: Session) -> bool:
    """
    Verify if a refresh token exists and is not expired.
    """
    r = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not r:
        return False
    if r.expires_at < datetime.utcnow():
        return False
    return True

def blacklist_token(token: str, db: Session):
    """
    Invalidate a refresh token by deleting it from the DB.
    You can also store it in Redis for quick blacklist checks.
    """
    r = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if r:
        db.delete(r)
        db.commit()
