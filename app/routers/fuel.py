from fastapi import FastAPI,Response, status, HTTPException, Depends, APIRouter
from typing import Optional,List, Dict 
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models ,schemas,oauth2,utils
from ..database import  get_db

router = APIRouter(prefix="/fuel", tags=['Fuel'])

############################################################################################################################
@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.FuelOut) 
def create_fuel(fuel : schemas.FuelCreate, db:Session = Depends(get_db)):
 
    new_fuel = models.Fuel(**fuel.dict())
    db.add(new_fuel)
    db.commit()
    db.refresh(new_fuel)
    return new_fuel

############################################################################################################################

@router.get("/", response_model = List[schemas.FuelOut])
def get_fuelLog(db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user),
              limit : int = 5, skip : int = 0, search :Optional[str] = ""):
              
  
    ##filter all the fuel history(log) at the same time
    fuel = db.query(models.Fuel).filter(models.Fuel.vehicle_id.contains(search)).limit(limit).offset(skip).all()
    return fuel
############################################################################################################################

@router.get("/{id}", response_model=schemas.FuelOut)
def get_fuelog(id : int, db :Session = Depends(get_db),  current_user : str = Depends(oauth2.get_current_user)):
    fuel = db.query(models.Fuel).filter(models.Fuel.id == id).first()
    
    if not fuel :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fuel Log  with id : {id} was not found")
    return fuel

#############################################################################################################################

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_fuelog(id:int,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
   
   fuel_query = db.query(models.Fuel).filter(models.Fuel.id == id)
   fuel = fuel_query.first()
   
   if fuel == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"fuel log with id: {id} does not exist")
  
         
   fuel_query.delete(synchronize_session = False) 
   db.commit()  
   return Response(status_code=status.HTTP_204_NO_CONTENT)
############################################################################################################################

@router.put("/{id}", response_model=schemas.FuelCreate)
def update_fuelog(id:int,updated_fuel:schemas.FuelCreate,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
  
    fuel_query = db.query(models.User).filter(models.Fuel.id == id)
    fuel =fuel_query.first()
    if fuel == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"fuelv log  with id: {id} does not exist")
   
    fuel_query.update(updated_fuel.dict(),synchronize_session = False)
    db.commit()
    return fuel_query.first()  
############################################################################################################################
