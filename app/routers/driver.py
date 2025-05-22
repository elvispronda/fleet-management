from fastapi import FastAPI,Response, status, HTTPException, Depends, APIRouter
from typing import Optional,List, Dict 
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models ,schemas,oauth2,utils
from ..database import  get_db

router = APIRouter(prefix="/driver", tags=['Driver'])
############################################################################################################################
@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.DriverOut) 
def create_driver(driver : schemas.DriverCreate, db:Session = Depends(get_db)):
  
    new_driver = models.Driver(**driver.dict())
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver

############################################################################################################################

@router.get("/", response_model = List[schemas.DriverOut])
def get_drivers(db:Session = Depends(get_db),limit : int = 5, skip : int = 0, search :Optional[str] = ""):
              
  
    ##filter all drivers at the same time
    drivers= db.query(models.Driver).filter(models.Driver.matricule.contains(search)).limit(limit).offset(skip).all()
    return drivers
############################################################################################################################

@router.get("/{id}", response_model=schemas.DriverOut)
def get_driver(id : int, db :Session = Depends(get_db),  current_user : str = Depends(oauth2.get_current_user)):
    driver = db.query(models.Driver).filter(models.Driver.id == id).first()
    
    if not driver :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"driver with id : {id} was not found")
    return driver

#############################################################################################################################

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(id:int,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
   
   driver_query = db.query(models.Driver).filter(models.Driver.id == id)
   driver = driver_query.first()
   
   if driver == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"driver with id: {id} does not exist")
  
         
   driver_query.delete(synchronize_session = False) 
   db.commit()  
   return Response(status_code=status.HTTP_204_NO_CONTENT)
############################################################################################################################
""" 
@router.put("/{id}", response_model=schemas.DriverCreate)
def update_driver(id:int,updated_driver:schemas.DriverCreate,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
  
    driver_query = db.query(models.User).filter(models.User.id == id)
    driver =driver_query.first()
    if driver == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"driver with id: {id} does not exist")
   
    driver_query.update(updated_driver.dict(),synchronize_session = False)
    db.commit()
    return driver_query.first()   """

# In your driver.py router
@router.put("/{id}", response_model=schemas.DriverOut) # Changed response_model
def update_driver(
    id: int, 
    updated_driver_data: schemas.DriverCreate, # Ideally schemas.DriverUpdate with Optional fields
    db: Session = Depends(get_db), 
    current_user: str = Depends(oauth2.get_current_user) # Assuming this is a placeholder for a user object
):
    driver_query = db.query(models.Driver).filter(models.Driver.id == id) # Corrected to models.Driver
    db_driver = driver_query.first()

    if db_driver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Driver with id: {id} does not exist")
   
    # If using DriverCreate, all fields are expected.
    # If you create DriverUpdate with Optional fields, use .dict(exclude_unset=True)
    update_data = updated_driver_data.dict() 
    
    driver_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(db_driver) # Refresh the instance fetched earlier
    return db_driver
############################################################################################################################