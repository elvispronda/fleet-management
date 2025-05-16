# app/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas, models, utils, oauth2
from ..database import get_db

router = APIRouter(prefix="/login",tags=['Authentication'])

@router.post("/", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        (models.User.email == user_credentials.username) |
        (models.User.username == user_credentials.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # More specific than 403 for login
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active: # <-- Professional user status check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # 403 Forbidden if account exists but is inactive
            detail="Account is inactive. Please contact support."
        )
    
    access_token_data = {
        "user_id": str(user.id), # Ensure user_id is a string for JWT consistency
        "sub": user.username,
        "is_active": user.is_active # Optionally include other non-sensitive claims
        # "roles": ["admin"] # Example if you have roles
    }
    access_token = oauth2.create_access_token(data=access_token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,         # For client-side convenience
        "username": user.username,  # For client-side convenience
        "is_active": user.is_active
    }




    