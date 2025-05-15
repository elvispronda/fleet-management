from fastapi import FastAPI,Response, status, HTTPException, Depends, APIRouter
from typing import Optional,List, Dict 
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models ,schemas,oauth2,utils
from ..database import  get_db

router = APIRouter(prefix="/maintenance", tags=['Maintenance'])

############################################################################################################################
@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.MaintenanceOut) 
def create_maintenance(maintenance : schemas.MaintenanceCreate, db:Session = Depends(get_db)):
    
    new_maintenance = models.Maintenance(**maintenance.dict())
    db.add(new_maintenance)
    db.commit()
    db.refresh(new_maintenance)
    return new_maintenance

############################################################################################################################

@router.get("/", response_model = List[schemas.MaintenanceOut])
def get_maintenanceLog(db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user),
              limit : int = 5, skip : int = 0, search :Optional[str] = ""):
              
  
    ##filter all maintenance  logsat the same time
    maintenances = db.query(models.Maintenance).filter(models.Maintenance.vehicule_id.contains(search)).limit(limit).offset(skip).all()
    return maintenances 
############################################################################################################################

@router.get("/{id}", response_model=schemas.UserOut)
def get_maintenancelog(id : int, db :Session = Depends(get_db),  current_user : str = Depends(oauth2.get_current_user)):
    maintenance = db.query(models.Maintenance).filter(models.Maintenance.id == id).first()
    
    if not maintenance :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Maintenance log with this Car id : {id} was not found")
    return maintenance

#############################################################################################################################

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance(id:int,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
   
   maintenance_query = db.query(models.Maintenance).filter(models.Maintenance.id == id)
   maintenance = maintenance_query.first()
   
   if maintenance == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Maintenance log with this Car id: {id} does not exist")
  
         
   maintenance_query.delete(synchronize_session = False) 
   db.commit()  
   return Response(status_code=status.HTTP_204_NO_CONTENT)
############################################################################################################################

@router.put("/{id}", response_model=schemas.MaintenanceCreate)
def update_maintenance(id:int,updated_maintenance:schemas.MaintenanceCreate,db:Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
  
    maintenance_query = db.query(models.Maintenance).filter(models.Maintenance.id == id)
    maintenance =maintenance_query.first()
    if maintenance == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Maintenance  with  car id: {id} does not exist")
   
    maintenance_query.update(updated_maintenance.dict(),synchronize_session = False)
    db.commit()
    return maintenance_query.first()  
############################################################################################################################
