from pydantic import BaseModel, EmailStr,Field, validator # 
from typing import Optional
from datetime import datetime, time
import enum # For Python enum

###################################################################################################################

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="pronda")
    email: EmailStr = Field(..., example="root@gmail.com")
    
    # MODIFIED: Replaced is_active with status
    status: str = Field(..., example="active", description="User account status (e.g., active, inactive)")
    # If using Enum: status: UserStatusEnum = Field(..., example=UserStatusEnum.active)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User password (will be hashed)")


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user. All fields are optional.
    Password updates should ideally have a dedicated endpoint or stricter controls.
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50, example="pronda_new")
    email: Optional[EmailStr] = Field(None, example="new_root@gmail.com")
    
    # MODIFIED: Replaced is_active with status
    status: Optional[str] = Field(None, example="inactive", description="New user account status")
    # If using Enum: status: Optional[UserStatusEnum] = Field(None, example=UserStatusEnum.inactive)

    # Optional: If you want to allow password updates via this endpoint
    # password: Optional[str] = Field(None, min_length=8, description="New password (will be hashed)")


class UserOut(UserBase): # UserBase already includes the modified 'status'
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example=datetime.utcnow())
    # username, email, status are inherited from UserBase

    class Config:
        from_attributes = True # Pydantic V2+ (replaces orm_mode)
        # orm_mode = True # For Pydantic V1

# --- Authentication Schemas ---

class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    Can use 'username' or 'email' for login.
    """
    identifier: str = Field(..., description="Username or email address", example="johndoe") # Or 'username_or_email'
    password: str = Field(..., min_length=8, description="User password")



class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", example="bearer")
    user_id: int = Field(..., example=1, description="ID of the logged-in user") # Made non-optional
    username: str = Field(..., example="johndoe", description="Username of the logged-in user") # Made non-optional
    
    # ADDED: User status at the time of login
    status: str = Field(..., example="active", description="User's status at the time of login") 


class TokenData(BaseModel):
    sub: str # Subject, typically the username
    user_id: int
    status: str
    username: str # Explicitly add if needed, or rely on 'sub'


# --- Schema for Password Change ---
class PasswordChange(BaseModel):
    current_password: str = Field(..., description="User's current password")
    new_password: str = Field(..., min_length=8, description="New desired password")
###################################################################################################################

class DriverBase(BaseModel):
    nom: str
    prenom: str
    cni: str
    email: str
    matricule: str

class DriverCreate(DriverBase):
    pass

class DriverOut(DriverBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
##################################################################################################################

class CategoryFuelBase(BaseModel):
    fuel_name: str

class CategoryFuelCreate(CategoryFuelBase):
    pass

class CategoryFuelOut(CategoryFuelBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
##################################################################################################################

class FuelBase(BaseModel):
    vehicle_id: int
    fuel_type_id: int
    quantity: float
    cost: float

class FuelCreate(FuelBase):
    pass

class FuelOut(FuelBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
##################################################################################################################

class TripBase(BaseModel):
    origin: str = Field(..., examples=["New York City"])
    destination: str = Field(..., examples=["Los Angeles"])
    vehicle_id: Optional[int] = Field(default=None, examples=[101])
    driver_id: Optional[int] = Field(default=None, examples=[202])
    
    departure_day: datetime = Field(..., examples=["2023-10-27T00:00:00"]) # Frontend provides full datetime
    return_date: Optional[datetime] = Field(default=None, examples=["2023-10-28T00:00:00"]) # Frontend provides full datetime
    
    leave_at: time = Field(..., examples=["09:30:00"])         # Time part for departure
    arrive_at: Optional[time] = Field(default=None, examples=["17:45:00"]) # Time part for arrival
    
    status: str = Field(..., examples=["PLANNED"]) # e.g., "PLANNED", "ONGOING". Could be an Enum.

    @validator('return_date', always=True)
    def check_return_date_chronology(cls, v_return_date, values):
        departure_day = values.get('departure_day')
        if v_return_date and departure_day:
            if v_return_date <= departure_day:
                raise ValueError('return_date must be strictly after departure_day')
        return v_return_date

    @validator('arrive_at', always=True)
    def check_arrive_at_if_return_date_present(cls, v_arrive_at, values):
        return_date = values.get('return_date')
        # If return_date is provided (not None), then arrive_at must also be provided.
        if return_date and v_arrive_at is None:
            raise ValueError('arrive_at must be provided if return_date is set')
        # If return_date is None, arrive_at should also be None or not provided.
        if not return_date and v_arrive_at is not None:
            raise ValueError('arrive_at should not be set if return_date is not set')
        return v_arrive_at

  
class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    origin: Optional[str] = Field(default=None, examples=["New York City"])
    destination: Optional[str] = Field(default=None, examples=["Los Angeles"])
    vehicle_id: Optional[int] = Field(default=None, examples=[101])
    driver_id: Optional[int] = Field(default=None, examples=[202])
    
    departure_day: Optional[datetime] = Field(default=None, examples=["2023-10-27T00:00:00"])
    return_date: Optional[datetime] = Field(default=None, examples=["2023-10-28T00:00:00"]) 
    
    leave_at: Optional[time] = Field(default=None, examples=["09:30:00"])
    arrive_at: Optional[time] = Field(default=None, examples=["17:45:00"]) 
    
    status: Optional[str] = Field(default=None, examples=["ONGOING"]) 


class TripOut(BaseModel):    
    id: int
    origin: str
    destination: str
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    
    departure_date: datetime         
    return_date: Optional[datetime] = None 
    
    leave_at: datetime               
    arrive_at: Optional[datetime] = None  
    
    created_at: datetime
    status: str

    class Config:
        from_attributes = True 


##################################################################################################################

class VehicleTransmissionBase(BaseModel):
    vehicle_transmission: str

class VehicleTransmissionCreate(VehicleTransmissionBase):
    pass

class VehicleTransmissionOut(VehicleTransmissionBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

class FuelTypeBase(BaseModel):
    fuel_type: str

class FuelTypeCreate(FuelTypeBase):
    pass

class FuelTypeOut(FuelTypeBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

class VehicleTypeBase(BaseModel):
    vehicle_type: str

class VehicleTypeCreate(VehicleTypeBase):
    pass

class VehicleTypeOut(VehicleTypeBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

class VehicleMakeBase(BaseModel):
    vehicle_make: str

class VehicleMakeCreate(VehicleMakeBase):
    pass

class VehicleMakeOut(VehicleMakeBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

class VehicleModelBase(BaseModel):
    vehicle_model: str

class VehicleModelCreate(VehicleModelBase):
    pass

class VehicleModelOut(VehicleModelBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

class VehicleBase(BaseModel):
    make: int
    model: int
    year: int
    plate_number: str
    mileage: float = 0.0
    engine_size: float
    vehicle_type: int
    vehicle_transmission: int
    vehicle_fuel_type: int
    vin: str
    color: str
    purchase_price: float
    purchase_date: datetime
    status: str = "available" 

class VehicleCreate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: int
    registration_date: datetime

    class Config:
        from_attributes = True
##################################################################################################################

class CategoryDocumentBase(BaseModel):
    doc_name: str
    cost: float

class CategoryDocumentCreate(CategoryDocumentBase):
    pass

class CategoryDocumentOut(CategoryDocumentBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

class DocumentVehiculeBase(BaseModel):
    doc_name_id: int
    vehicle_id: int
    issued_date: datetime
    expiration_date: datetime

class DocumentVehiculeCreate(DocumentVehiculeBase):
    pass

class DocumentVehiculeOut(DocumentVehiculeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
##################################################################################################################

class GarageBase(BaseModel):
    nom_garage: str

class GarageCreate(GarageBase):
    pass

class GarageOut(GarageBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

class CategoryMaintenanceBase(BaseModel):
    cat_maintenance: str

class CategoryMaintenanceCreate(CategoryMaintenanceBase):
    pass

class CategoryMaintenanceOut(CategoryMaintenanceBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

# --- Maintenance Schemas ---
class MaintenanceBase(BaseModel):
    cat_maintenance_id: Optional[int] = None # Made optional to align with nullable=True in DB if that's the case
    vehicle_id: int
    garage_id: Optional[int] = None # Made optional to align with nullable=True in DB if that's the case
    maintenance_cost: float
    receipt: str
    maintenance_date: datetime

class MaintenanceCreate(MaintenanceBase):
    pass # No changes needed here, it inherits the corrected fields

class MaintenanceOut(MaintenanceBase):
    id: int
    created_at: datetime

    # Optional: Add fields from related models if you want to include them in the output
    # This requires using relationship loading in your API endpoint and defining nested Pydantic models.
    # Example:
    # vehicle_plate_number: Optional[str] = None
    # category_name: Optional[str] = None
    # garage_name: Optional[str] = None

    class Config:
        from_attributes = True # Was orm_mode = True in Pydantic V1
##################################################################################################################

class CategoryPanneBase(BaseModel):
    nom_panne: str

class CategoryPanneCreate(CategoryPanneBase):
    pass

class CategoryPanneOut(CategoryPanneBase):
    id: int

    class Config:
        from_attributes = True
##################################################################################################################

class PanneBase(BaseModel):
    vehicle_id: int
    nom_panne_id: int
    description: Optional[str] = None
    status: str
    panne_date: datetime

class PanneCreate(PanneBase):
    pass

class PanneOut(PanneBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
##################################################################################################################

class ReparationBase(BaseModel):
    panne_id: int
    cost: float
    receipt: str
    garage_id: int
    repair_date: datetime
    status: str

class ReparationCreate(ReparationBase):
    pass

class ReparationOut(ReparationBase):
    id: int

    class Config:
        from_attributes = True


