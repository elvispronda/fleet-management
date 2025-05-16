# app/oauth2.py
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import schemas, database, models
from .config import settings

# OAuth2 scheme configuration - tokenUrl should point to your login endpoint's path
# If auth.router is prefixed, ensure this matches: e.g., "auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/") # Assuming /login is at the root or auth router is not prefixed

# JWT Configuration from settings
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e: # More specific exception handling could be added for JWT encoding issues
        # Log the error for debugging purposes
        print(f"Error encoding JWT: {e}") # Replace with proper logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token."
        )


def verify_access_token(token: str, credentials_exception: HTTPException) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str = payload.get("user_id")
        username: str = payload.get("sub")
        is_active_from_token: bool = payload.get("is_active", False) # Default to False if not present

        if user_id is None or username is None:
            raise credentials_exception
            
        # Ensure user_id can be converted to int for DB lookup
        try:
            int(user_id)
        except ValueError:
            raise credentials_exception
            
        return schemas.TokenData(id=user_id, username=username, is_active=is_active_from_token)
    except JWTError as e: # Catches specific JWT errors like ExpiredSignatureError, InvalidTokenError
        # Log the specific JWT error
        print(f"JWTError during token verification: {e}") # Replace with proper logging
        # Provide a slightly more informative message if it's an expiration issue
        if "Expired" in str(e):
             expired_credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\", error_description=\"The token has expired\""},
            )
             raise expired_credentials_exception from e
        raise credentials_exception from e
    except Exception as e: # Catch-all for other unexpected errors
        print(f"Unexpected error during token verification: {e}") # Replace with proper logging
        raise credentials_exception # Re-raise the generic credentials_exception


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_access_token(token, credentials_exception)
    
    try:
        user_id_int = int(token_data.id)
    except ValueError:
        # This should have been caught in verify_access_token, but defensive check
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id_int).first()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active: # <-- Professional user status check from DB
        inactive_user_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_request\", error_description=\"User account is inactive\""},
        )
        raise inactive_user_exception
            
    return user

# Optional: Dependency to get current *active* user, can be used directly
async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    # The get_current_user already checks for is_active.
    # This function is more for semantic clarity if needed, or if you add more checks (e.g., roles).
    # if not current_user.is_active: # This check is redundant if get_current_user does it
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user