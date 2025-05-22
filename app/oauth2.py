# app/oauth2.py

from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import schemas, database, models
from .config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes # Will now be a clean int

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/") # Matches your auth.py

def create_access_token(data: dict):
    to_encode = data.copy()
    # Ensure ACCESS_TOKEN_EXPIRE_MINUTES is treated as an integer
    expire_minutes = int(ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Claims from your auth.py: "sub": username, "user_id": int, "status": str
        subject: Optional[str] = payload.get("sub") 
        user_id_from_token: Optional[int] = payload.get("user_id")
        status_from_token: Optional[str] = payload.get("status")

        if subject is None or user_id_from_token is None or status_from_token is None:
            print(f"JWTError: Missing critical claims. Subject: {subject}, UserID: {user_id_from_token}, Status: {status_from_token}")
            raise credentials_exception
        
        # Assuming schemas.TokenData expects 'sub', 'user_id', 'status'
        # and possibly 'username' if you explicitly add it as a separate claim from 'sub'.
        # In your current auth.py, 'sub' IS the username.
        token_data = schemas.TokenData(
            sub=subject,       # This is the username
            user_id=user_id_from_token,
            status=status_from_token,
            username=subject   # Explicitly setting username to match 'sub' for TokenData
        )
    except JWTError as e:
        print(f"JWTError during token decoding or validation: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"Unexpected error during token verification: {str(e)}")
        raise credentials_exception
    
    return token_data

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(database.get_db)
) -> models.User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_access_token(token, credentials_exception)
    
    if token_data.user_id is None: # Should be caught earlier, but good safeguard
        print("Error in get_current_user: token_data.user_id is None after verification.")
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()

    if user is None:
        print(f"Error in get_current_user: User with ID {token_data.user_id} not found in DB.")
        raise credentials_exception
    
    # Security Improvement: Re-check user status on every authenticated request
    if user.status != "active":
        print(f"Access denied for user ID {user.id}: Account status is '{user.status}'.")
        # You might want a more specific message or just the generic credentials_exception
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account access restricted. Status: {user.status}",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

