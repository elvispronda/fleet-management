from pydantic import BaseModel, EmailStr,Field, validator # 
from typing import Optional,List
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
    access_token: str
    token_type: str
    user_id: int
    username: str
    status: str

class TokenData(BaseModel):
    sub: str        
    user_id: int
    status: str
    username: str   


# --- Schema for Password Change ---
class PasswordChange(BaseModel):
    current_password: str = Field(..., description="User's current password")
    new_password: str = Field(..., min_length=8, description="New desired password")
###################################################################################################################

class DriverBase(BaseModel):
    last_name: str
    first_name: str
    cni_number: str
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
# --- Trip Schemas ---

class TripBase(BaseModel):
    vehicle_id: int
    driver_id: int
    start_location: str
    end_location: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "planned"
    # --- NEW OPTIONAL FIELDS ---
    purpose: Optional[str] = None
    notes: Optional[str] = None
    # --- END NEW OPTIONAL FIELDS ---

class TripCreate(TripBase):
    pass # Inherits all from TripBase, including new fields

class TripUpdate(BaseModel): # For PUT, allow partial updates
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    # --- NEW OPTIONAL FIELDS ---
    purpose: Optional[str] = None
    notes: Optional[str] = None
    # --- END NEW OPTIONAL FIELDS ---

# To include related vehicle and driver info when returning a trip
# You might already have something similar
class VehicleNestedInTrip(BaseModel): # Simplified Vehicle for nesting
    id: int
    plate_number: str
    # Add other vehicle fields you want to show directly with the trip
    make: Optional[str] = None # Assuming you resolve this from vehicle.make (id) to vehicle_make.vehicle_make (name)
    model: Optional[str] = None# Assuming you resolve this from vehicle.model (id) to vehicle_model.vehicle_model (name)

    class Config:
        from_attributes = True

class DriverNestedInTrip(BaseModel): # Simplified Driver for nesting
    id: int
    first_name: str
    last_name: str
    # Add other driver fields

    class Config:
        from_attributes = True


class TripResponse(TripBase): # Schema for returning a trip to the client
    id: int
    created_at: Optional[datetime] = None # Or datetime if always present
    updated_at: Optional[datetime] = None # Or datetime if always present

    # Optional: Include nested vehicle and driver details if your API returns them
    # vehicle: Optional[VehicleNestedInTrip] = None
    # driver: Optional[DriverNestedInTrip] = None
    # If you resolve make/model names from IDs at the API level, you can add them here:
    # vehicle_plate_number: Optional[str] = None
    # driver_full_name: Optional[str] = None


    class Config:
        from_attributes = True # For SQLAlchemy model to Pydantic conversion

# Schema for a list of trips (if you use it)
class TripListResponse(BaseModel):
    trips: List[TripResponse]
    total_count: Optional[int] = None # For pagination
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


