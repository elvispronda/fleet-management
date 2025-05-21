from pydantic import BaseModel, EmailStr, Field # Field can be used for validation/examples
from typing import Optional, Union
from datetime import datetime

###################################################################################################################
# --- User Schemas ---
# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Possible user statuses - can be an Enum for more robustness if desired
# from enum import Enum
# class UserStatusEnum(str, Enum):
#     active = "active"
#     inactive = "inactive"
#     pending_approval = "pending_approval"
#     suspended = "suspended"

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
    # 'sub' (subject) is often used for the primary identifier (username or stringified user_id)
    # Let's assume 'sub' will be the username for this example.
    # If you use user_id as 'sub', make sure it's a string.
    sub: Optional[str] = Field(None, description="Subject of the token (e.g., username or user_id as string)")
    
    # You can add specific claims if needed beyond 'sub'
    user_id: Optional[int] = Field(None, description="User ID (integer)") 
    username: Optional[str] = Field(None, description="Username (can be same as sub)") 
    
    # This should reflect the string status
    status: Optional[str] = Field(None, description="User's status at the time of token creation")
    # exp: Optional[int] = None # Expiration time, usually handled by JWT library & verified during decode



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
    origin: str
    destination: str
    departure_date: datetime
    return_date: datetime
    vehicle_id: int
    driver_id: int

class TripCreate(TripBase):
    pass

class TripOut(TripBase):
    id: int

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

class MaintenanceBase(BaseModel):
    cat_maintenance_id: int
    vehicle_id: int
    garage_id: int
    maintenance_cost: float
    receipt: str
    maintenance_date: datetime

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceOut(MaintenanceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
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


