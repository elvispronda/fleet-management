from fastapi import FastAPI,Response, status, HTTPException, Depends, APIRouter
from typing import Optional,List, Dict 
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models ,schemas,oauth2,utils
from ..database import  get_db

router = APIRouter(prefix="/panne", tags=['Panne'])

############################################################################################################################
@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.PanneOut) 
def create_panne(panne : schemas.PanneCreate, db:Session = Depends(get_db)):

    new_panne = models.Panne(**panne.dict())
    db.add(new_panne)
    db.commit()
    db.refresh(new_panne)
    return new_panne

############################################################################################################################

@router.get("/", response_model = List[schemas.PanneOut])
def get_pannelog(db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user),
              limit : int = 5, skip : int = 0, search :Optional[str] = ""):
              
  
    ##filter all pannes log at the same time
    pannes = db.query(models.Panne).filter(models.Panne.vehicle_id.contains(search)).limit(limit).offset(skip).all()
    return pannes 
############################################################################################################################

@router.get("/{id}", response_model=schemas.PanneOut)
def get_panne(id : int, db :Session = Depends(get_db),  current_user : str = Depends(oauth2.get_current_user)):
    panne = db.query(models.Panne).filter(models.Panne.id == id).first()
    
    if not panne :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Panne log with this car id : {id} was not found")
    return panne

#############################################################################################################################

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_panne(id:int,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
   
   panne_query = db.query(models.Panne).filter(models.Panne.id == id)
   panne = panne_query.first()
   
   if panne == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Panne log with this car id : {id} does not exist")
  
         
   panne_query.delete(synchronize_session = False) 
   db.commit()  
   return Response(status_code=status.HTTP_204_NO_CONTENT)
############################################################################################################################

@router.put("/{id}", response_model=schemas.PanneCreate)
def update_panne(id:int,updated_panne:schemas.PanneCreate,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
  
    panne_query = db.query(models.Panne).filter(models.Panne.id == id)
    panne=panne_query.first()
    if panne == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} does not exist")
   
    panne_query.update(updated_panne.dict(),synchronize_session = False)
    db.commit()
    return panne_query.first()  
############################################################################################################################