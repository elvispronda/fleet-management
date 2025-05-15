from fastapi import FastAPI,Response, status, HTTPException, Depends, APIRouter
from typing import Optional,List, Dict 
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models ,schemas,oauth2,utils
from ..database import  get_db

router = APIRouter(prefix="/reparation", tags=['Reparation'])

############################################################################################################################
@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.ReparationOut) 
def create_reparationlog(reparation : schemas.ReparationCreate, db:Session = Depends(get_db)):
    

    new_reparation = models.Reparation(**reparation.dict())
    db.add(new_reparation)
    db.commit()
    db.refresh(new_reparation)
    return new_reparation

############################################################################################################################

@router.get("/", response_model = List[schemas.ReparationOut])
def get_reparations(db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user),
              limit : int = 5, skip : int = 0, search :Optional[str] = ""):
              
  
    ##filter all reparations log at the same time
    reparations = db.query(models.Reparation).filter(models.Reparation.panne_id.contains(search)).limit(limit).offset(skip).all()
    return reparations
############################################################################################################################

@router.get("/{id}", response_model=schemas.ReparationOut)
def get_reparationlog(id : int, db :Session = Depends(get_db),  current_user : str = Depends(oauth2.get_current_user)):
    reparation = db.query(models.Reparation).filter(models.Reparation.id == id).first()
    
    if not reparation :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"reparation log with panne id : {id} was not found")
    return reparation

#############################################################################################################################

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_reparationlog(id:int,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
   
   reparation_query = db.query(models.Reparation).filter(models.Reparation.id == id)
   reparation = reparation_query.first()
   
   if reparation == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"reparation log with panne id : {id} does not exist")
  
         
   reparation_query.delete(synchronize_session = False) 
   db.commit()  
   return Response(status_code=status.HTTP_204_NO_CONTENT)
############################################################################################################################

@router.put("/{id}", response_model=schemas.ReparationCreate)
def update_reparation(id:int,updated_reparation:schemas.ReparationCreate,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
  
    reparation_query = db.query(models.Reparation).filter(models.Reparation.id == id)
    reparation =reparation_query.first()
    if reparation == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} does not exist")
   
    reparation_query.update(updated_reparation.dict(),synchronize_session = False)
    db.commit()
    return reparation_query.first()  
############################################################################################################################