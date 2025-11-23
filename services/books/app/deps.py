from fastapi import Header, HTTPException

INTERNAL_SECRET = "supersecretinternalkey"

def verify_internal_secret(x_internal_secret: str = Header(...)):
    if x_internal_secret != INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Invalid internal service secret")
    return True
