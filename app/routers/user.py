from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Request
from typing import Optional, List
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2, utils
from ..database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/user", tags=['User'])

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

############################################################################################################################
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

############################################################################################################################
@router.get("/", response_model=List[schemas.UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user),  # This enforces auth
    limit: int = 5,
    skip: int = 0,
    search: Optional[str] = ""
):
    """Get list of users (API endpoint)"""
    users = db.query(models.User).filter(
        models.User.email.contains(search)
    ).limit(limit).offset(skip).all()
    return users


 

############################################################################################################################
@router.get("/users-page", response_class=HTMLResponse)
async def get_users_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user)
):
    """User management HTML page"""
    return templates.TemplateResponse("users.html", {
        "request": request,
        "current_user": current_user.username if current_user else None
    })

############################################################################################################################
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user)
):
    """Get a specific user by ID"""
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} was not found"
        )
    return user

############################################################################################################################
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user)
):
    """Delete a user"""
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
   
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
  
    user_query.delete(synchronize_session=False) 
    db.commit()  
    return Response(status_code=status.HTTP_204_NO_CONTENT)

############################################################################################################################
@router.put("/{id}", response_model=schemas.UserOut)
def update_user(
    id: int,
    updated_user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user)
):
    """Update a user"""
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
   
    # Hash the password if it's being updated
    if updated_user.password:
        updated_user.password = utils.hash(updated_user.password)
    
    user_query.update(updated_user.dict(), synchronize_session=False)
    db.commit()
    return user_query.first()