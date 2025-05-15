from fastapi import FastAPI,Response, status, HTTPException, Depends, APIRouter
from typing import Optional,List, Dict 
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models ,schemas,oauth2,utils
from ..database import  get_db

router = APIRouter(prefix="/trip", tags=['Trip'])

############################################################################################################################
@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.TripOut) 
def create_trip(trip: schemas.TripCreate, db:Session = Depends(get_db)):
   
    
    new_trip = models.User(**trip.dict())
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip

############################################################################################################################

@router.get("/", response_model = List[schemas.TripOut])
def get_trips(db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user),
              limit : int = 5, skip : int = 0, search :Optional[str] = ""):
              
  
    ##filter all trips  log at the same time
    trips = db.query(models.Trip).filter(models.Trip.vehicle_id.contains(search)).limit(limit).offset(skip).all()
    return trips
############################################################################################################################

@router.get("/{id}", response_model=schemas.TripOut)
def get_triplog(id : int, db :Session = Depends(get_db),  current_user : str = Depends(oauth2.get_current_user)):
    trip = db.query(models.Trip).filter(models.Trip.id == id).first()
    
    if not trip :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip with this car id : {id} was not found")
    return trip

#############################################################################################################################

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(id:int,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
   
   trip_query = db.query(models.Trip).filter(models.Trip.id == id)
   trip = trip_query.first()
   
   if trip == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Trip with this car id: {id} does not exist")
  
         
   trip_query.delete(synchronize_session = False) 
   db.commit()  
   return Response(status_code=status.HTTP_204_NO_CONTENT)
############################################################################################################################

@router.put("/{id}", response_model=schemas.TripCreate)
def update_trip(id:int,updated_trip:schemas.TripCreate,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
  
    trip_query = db.query(models.Trip).filter(models.Trip.id == id)
    trip =trip_query.first()
    if trip == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Trip with this car id: {id} does not exist")
   
    trip_query.update(updated_trip.dict(),synchronize_session = False)
    db.commit()
    return trip_query.first()  
############################################################################################################################

