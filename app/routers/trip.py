# app/routers/trip.py
from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, String 
from datetime import datetime, time, timezone # Import timezone

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/trip", tags=['Trip'])

############################################################################################################################
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TripOut)
def create_trip(
    trip_data: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Pydantic validator 'check_return_date_chronology' already handles this
    # if trip_data.return_date and trip_data.departure_day >= trip_data.return_date:
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail="Return date must be after departure_day."
    #     )

    # Pydantic validator 'check_arrive_at_if_return_date' handles this
    # if trip_data.return_date and not trip_data.arrive_at:
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail="If return_date is provided, arrive_at must also be provided."
    #     )

    # Combine date and time for DB's TIMESTAMP fields
    # The model's 'departure_date' field will store the full departure datetime
    # The model's 'leave_at' field will store departure_day's date + leave_at's time
    
    db_leave_at = datetime.combine(trip_data.departure_day.date(), trip_data.leave_at)
    # Ensure timezone awareness if your DB TIMESTAMPs are timezone-aware
    if trip_data.departure_day.tzinfo is None:
        db_leave_at = db_leave_at.replace(tzinfo=timezone.utc) # Or user's local timezone if known
        departure_day_for_db = trip_data.departure_day.replace(tzinfo=timezone.utc)
    else:
        departure_day_for_db = trip_data.departure_day
        db_leave_at = db_leave_at.replace(tzinfo=trip_data.departure_day.tzinfo)


    db_arrive_at = None
    return_date_for_db = None
    if trip_data.return_date and trip_data.arrive_at:
        db_arrive_at = datetime.combine(trip_data.return_date.date(), trip_data.arrive_at)
        if trip_data.return_date.tzinfo is None:
            db_arrive_at = db_arrive_at.replace(tzinfo=timezone.utc)
            return_date_for_db = trip_data.return_date.replace(tzinfo=timezone.utc)
        else:
            return_date_for_db = trip_data.return_date
            db_arrive_at = db_arrive_at.replace(tzinfo=trip_data.return_date.tzinfo)


    trip_dict = trip_data.model_dump(exclude={'departure_day', 'return_date', 'leave_at', 'arrive_at'})
    
    new_trip = models.Trip(
        **trip_dict,
        departure_date=departure_day_for_db, # This is the full departure datetime from schema
        return_date=return_date_for_db,     # This is the full return datetime from schema
        leave_at=db_leave_at,               # Combined date from departure_day + time from leave_at
        arrive_at=db_arrive_at,             # Combined date from return_date + time from arrive_at
        created_at=datetime.now(timezone.utc) # Set created_at since model doesn't have default
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip

############################################################################################################################

@router.get("/", response_model=List[schemas.TripOut])
def get_trips(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
    status_filter: Optional[str] = None # Changed from Enum for flexibility if Enum isn't defined
):
    query = db.query(models.Trip)

    if search:
        search_term = f"%{search.lower()}%"
        # Ensure joins are outer joins if vehicle or driver might be null
        query = query.outerjoin(models.Vehicle, models.Trip.vehicle_id == models.Vehicle.id) \
                     .outerjoin(models.Driver, models.Trip.driver_id == models.Driver.id)

        query = query.filter(
            or_(
                models.Trip.origin.ilike(search_term),
                models.Trip.destination.ilike(search_term),
                models.Vehicle.plate_number.ilike(search_term),
                # Assuming Driver model has 'nom' and 'prenom'
                (func.lower(models.Driver.nom) + " " + func.lower(models.Driver.prenom)).contains(search.lower()),
                func.cast(models.Trip.id, String).ilike(search_term),
                models.Trip.status.ilike(search_term) # Search in status as well
            )
        )

    if status_filter:
        query = query.filter(models.Trip.status == status_filter)

    trips = query.order_by(models.Trip.departure_date.desc()).limit(limit).offset(skip).all()
    return trips

############################################################################################################################

@router.get("/{id}", response_model=schemas.TripOut)
def get_trip_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    trip = db.query(models.Trip).filter(models.Trip.id == id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id: {id} was not found"
        )
    return trip

#############################################################################################################################

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    trip_query = db.query(models.Trip).filter(models.Trip.id == id)
    trip_to_delete = trip_query.first()

    if trip_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id: {id} does not exist"
        )

    trip_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

############################################################################################################################

@router.put("/{id}", response_model=schemas.TripOut)
def update_trip(
    id: int,
    trip_update_payload: schemas.TripUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    existing_trip = db.query(models.Trip).filter(models.Trip.id == id).first()

    if existing_trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id: {id} does not exist"
        )

    update_data = trip_update_payload.model_dump(exclude_unset=True)

    # Handle date and time fields carefully
    # The Pydantic schema sends 'departure_day', 'leave_at', 'return_date', 'arrive_at'
    # The DB model has 'departure_date', 'leave_at' (TIMESTAMP), 'return_date', 'arrive_at' (TIMESTAMP)

    # Determine effective dates and times for validation and DB update
    # Start with existing values and override if provided in payload
    effective_departure_day = update_data.get('departure_day', existing_trip.departure_date)
    effective_leave_at_time = update_data.get('leave_at', existing_trip.leave_at.time() if existing_trip.leave_at else None) # Get time part
    
    effective_return_date = update_data.get('return_date') # If None in payload, means clear it
    if 'return_date' not in update_data: # Not in payload, use existing
        effective_return_date = existing_trip.return_date
    
    effective_arrive_at_time = update_data.get('arrive_at') # If None in payload, means clear it
    if 'arrive_at' not in update_data and existing_trip.arrive_at: # Not in payload, use existing
        effective_arrive_at_time = existing_trip.arrive_at.time()


    # Validation: Chronology
    if effective_return_date and effective_departure_day >= effective_return_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Return date must be after departure_day."
        )
    
    # Validation: arrive_at presence if return_date is set
    if effective_return_date and not effective_arrive_at_time:
         raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="If return_date is provided, arrive_at must also be provided."
        )
    if not effective_return_date and effective_arrive_at_time: # If clearing return_date, arrive_at should also be cleared or not set
        if 'arrive_at' in update_data and update_data['arrive_at'] is not None:
             raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="If arrive_at is provided, return_date must also be provided."
            )
        effective_arrive_at_time = None # Clear arrive_at if return_date is cleared


    # Apply updates to the model
    for key, value in update_data.items():
        if key == "departure_day":
            existing_trip.departure_date = value # DB model field is departure_date
            if value and value.tzinfo is None: # Ensure timezone
                 existing_trip.departure_date = value.replace(tzinfo=timezone.utc)
        elif key == "return_date":
            existing_trip.return_date = value # Can be None to clear
            if value and value.tzinfo is None: # Ensure timezone
                 existing_trip.return_date = value.replace(tzinfo=timezone.utc)
        elif key in ["leave_at", "arrive_at"]:
            pass # Handled separately after simple fields
        else:
            setattr(existing_trip, key, value)

    # Reconstruct leave_at (TIMESTAMP) if departure_day or leave_at (time) changed
    if 'departure_day' in update_data or 'leave_at' in update_data:
        if effective_departure_day and effective_leave_at_time:
            new_leave_at_ts = datetime.combine(effective_departure_day.date(), effective_leave_at_time)
            if effective_departure_day.tzinfo is None: # Ensure timezone
                new_leave_at_ts = new_leave_at_ts.replace(tzinfo=timezone.utc)
            else:
                new_leave_at_ts = new_leave_at_ts.replace(tzinfo=effective_departure_day.tzinfo)
            existing_trip.leave_at = new_leave_at_ts
        elif 'leave_at' in update_data and update_data['leave_at'] is None: # Explicitly clearing
             existing_trip.leave_at = None # This might be an issue if DB 'leave_at' is NOT NULLABLE
                                           # Your model has nullable=False for leave_at, so this case shouldn't happen
                                           # or Pydantic validation for leave_at should make it non-optional in TripUpdate

    # Reconstruct arrive_at (TIMESTAMP) if return_date or arrive_at (time) changed
    if 'return_date' in update_data or 'arrive_at' in update_data:
        if effective_return_date and effective_arrive_at_time:
            new_arrive_at_ts = datetime.combine(effective_return_date.date(), effective_arrive_at_time)
            if effective_return_date.tzinfo is None: # Ensure timezone
                new_arrive_at_ts = new_arrive_at_ts.replace(tzinfo=timezone.utc)
            else:
                new_arrive_at_ts = new_arrive_at_ts.replace(tzinfo=effective_return_date.tzinfo)
            existing_trip.arrive_at = new_arrive_at_ts
        else: # Clearing return_date or arrive_at
            existing_trip.arrive_at = None


    db.add(existing_trip)
    db.commit()
    db.refresh(existing_trip)
    return existing_trip