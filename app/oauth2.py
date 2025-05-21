# app/oauth2.py

from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional # <<< CORRECT IMPORT FOR OPTIONAL
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import schemas, database, models # Assuming these are your project's modules
from .config import settings # Assuming your settings (SECRET_KEY, ALGORITHM, etc.) are here

# Make sure these are correctly loaded from your settings
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# This URL should point to your actual login/token endpoint
# If your login endpoint is at /login/ (as in your auth.py router prefix), this is correct.
# If it's /auth/token or something else, adjust tokenUrl accordingly.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract claims that are expected to be in the token based on how it was created
        # and what schemas.TokenData expects.
        subject: Optional[str] = payload.get("sub")
        user_id_from_token: Optional[int] = payload.get("user_id")
        username_from_token: Optional[str] = payload.get("username") # If you also include username explicitly
        status_from_token: Optional[str] = payload.get("status")

        # Validate essential claims. 'sub' and 'user_id' are often critical.
        if subject is None or user_id_from_token is None:
            # Log this specific issue for easier debugging if it occurs
            print(f"JWTError: Missing critical claims. Subject: {subject}, UserID: {user_id_from_token}")
            raise credentials_exception
        
        # Construct and validate the token data using your Pydantic schema
        token_data = schemas.TokenData(
            sub=subject,
            user_id=user_id_from_token,
            username=username_from_token if username_from_token is not None else subject, # Fallback username if not explicit
            status=status_from_token
        )
    except JWTError as e:
        # Log the specific JWT error
        print(f"JWTError during token decoding or validation: {str(e)}")
        raise credentials_exception
    except Exception as e:
        # Catch any other unexpected errors during token processing
        print(f"Unexpected error during token verification: {str(e)}")
        raise credentials_exception
    
    return token_data

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(database.get_db)
) -> models.User: # Specify that this function returns a SQLAlchemy User model instance
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_access_token(token, credentials_exception)
    
    # token_data.user_id is now correctly accessed (it's already an int or None)
    if token_data.user_id is None:
        # This case should ideally be caught by checks within verify_access_token
        print("Error in get_current_user: token_data.user_id is None after verification.")
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()

    if user is None:
        print(f"Error in get_current_user: User with ID {token_data.user_id} not found in DB.")
        raise credentials_exception 
    
    # Optional: Real-time status check after fetching user from DB.
    # The status in the token is from when the token was created.
    # if user.status != "active":
    #     print(f"Access denied for user {user.username} (ID: {user.id}). Current status: {user.status}")
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail=f"User account is currently '{user.status}'. Access restricted."
    #     )
        
    return user

# Example for an optional current user (if you need to check if a user is logged in
# without throwing an error if they are not, for public pages that have extra features for logged-in users)
# def get_current_active_user_optional(
#     token: Optional[str] = Depends(oauth2_scheme_optional), # Define oauth2_scheme_optional if needed
#     db: Session = Depends(database.get_db)
# ) -> Optional[models.User]:
#     if not token:
#         return None
#     try:
#         token_data = verify_access_token(token, HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid optional token")) # Dummy exception
#         if token_data.user_id is None:
#             return None
#         user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
#         if user and user.status == "active": # Only return if active
#             return user
#         return None # User not found or not active
#     except HTTPException: # Includes JWTError from verify_access_token
#         return None