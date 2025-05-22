from sqlalchemy import Column, Integer, String,Float, ForeignKey, TIMESTAMP, text, Enum as DBEnum # Added DBEnum
from datetime import datetime # For default values or type hinting if needed
import enum # For Python enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False) # Added length for clarity
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False) # Hashed password
    
    # MODIFIED: Replaced is_active with status
    status = Column(String(50), nullable=False, default="pending_approval") # e.g., "active", "inactive", "pending_approval"
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # You might want to add roles or other fields later
    # role = Column(String(50), default="user") 
    # Add other fields as needed (e.g., is_superuser, roles, etc.)
##################################################################################################################

class Driver(Base):
    __tablename__ = "driver"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    cni = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    matricule = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
##################################################################################################################

class FuelType(Base):
    __tablename__ = "fuel_type"
    id = Column(Integer, primary_key=True, index=True)
    fuel_type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
##################################################################################################################

class Fuel(Base):
    __tablename__ = "fuel"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False)
    fuel_type_id = Column(Integer, ForeignKey("fuel_type.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
##################################################################################################################

class Trip(Base):
    __tablename__ = "trip"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id", ondelete="SET NULL"), nullable=True)
    driver_id = Column(Integer, ForeignKey("driver.id", ondelete="SET NULL"), nullable=True)
    departure_date = Column(TIMESTAMP(timezone=True), nullable=False)
    return_date = Column(TIMESTAMP(timezone=True), nullable=True) # Nullable
    leave_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    arrive_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))
    created_at=Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, default="planned") # Status as a string

##################################################################################################################

class VehicleType(Base):
    __tablename__ = "vehicle_type"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)
##################################################################################################################

class VehicleMake(Base):
    __tablename__ = "vehicle_make"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_make = Column(String, nullable=False)
##################################################################################################################

class VehicleModel(Base):
    __tablename__ = "vehicle_model"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_model = Column(String, nullable=False)
##################################################################################################################

class VehicleTransmission(Base):
    __tablename__ = "vehicle_transmission"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_transmission = Column(String, nullable=False)
##################################################################################################################
class Vehicle(Base):
    __tablename__ = "vehicle"
    id = Column(Integer, primary_key=True, index=True)
    make = Column(Integer, ForeignKey("vehicle_make.id"))
    model = Column(Integer, ForeignKey("vehicle_model.id"))
    year = Column(Integer)
    plate_number = Column(String, unique=True, nullable=False)
    mileage = Column(Float, default=0.0)
    engine_size = Column(Float, default=0.0)
    vehicle_type = Column(Integer, ForeignKey("vehicle_type.id"))
    vehicle_transmission = Column(Integer, ForeignKey("vehicle_transmission.id"))
    vehicle_fuel_type = Column(Integer, ForeignKey("fuel_type.id"))
    vin = Column(String, nullable=False)
    color = Column(String, nullable=False)
    purchase_price = Column(Float, default=0.0)
    purchase_date = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(String, default="available")
    registration_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')) 
##################################################################################################################

class CategoryDocument(Base):
    __tablename__ = "category_document"
    id = Column(Integer, primary_key=True, index=True)
    doc_name = Column(String, nullable=False)
    cost = Column(Float, default=0.0)
##################################################################################################################

class DocumentVehicule(Base):
    __tablename__ = "document_vehicule"
    id = Column(Integer, primary_key=True, index=True)
    doc_name_id = Column(Integer, ForeignKey("category_document.id"))
    vehicule_id = Column(Integer, ForeignKey("vehicle.id"))
    issued_date = Column(TIMESTAMP(timezone=True), nullable=False)
    expiration_date = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
##################################################################################################################

class Garage(Base):
    __tablename__ = "garage"
    id = Column(Integer, primary_key=True, index=True)
    nom_garage = Column(String, nullable=False)
##################################################################################################################

class CategoryMaintenance(Base):
    __tablename__ = "category_maintenance"
    id = Column(Integer, primary_key=True, index=True)
    cat_maintenance = Column(String, nullable=False)
##################################################################################################################

class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cat_maintenance_id = Column(Integer, ForeignKey("category_maintenance.id", ondelete="SET NULL"), nullable=True) # Consider ondelete behavior
    vehicle_id = Column(Integer, ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False) # Changed from vehicule_id. Consider ondelete.
    garage_id = Column(Integer, ForeignKey("garage.id", ondelete="SET NULL"), nullable=True) # Consider ondelete behavior

    maintenance_cost = Column(Float, default=0.0, nullable=False)
    receipt = Column(String, nullable=False)
    maintenance_date = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Optional: Define relationships for easier data access if needed
    # These allow you to access related objects like maintenance.vehicle, maintenance.category, etc.
    # Ensure the related models (Vehicle, CategoryMaintenance, Garage) also have a back_populates if you use these.

    # category = relationship("CategoryMaintenance", back_populates="maintenances") # Example
    # vehicle = relationship("Vehicle", back_populates="maintenances") # Example
    # garage = relationship("Garage", back_populates="maintenances") # Example

    # If you want to access maintenance records from the other side (e.g., vehicle.maintenances):
    # In your Vehicle model:
    # maintenances = relationship("Maintenance", back_populates="vehicle")
    # In your CategoryMaintenance model:
    # maintenances = relationship("Maintenance", back_populates="category")
    # In your Garage model:
    # maintenances = relationship("Maintenance", back_populates="garage")
##################################################################################################################

class CategoryPanne(Base):
    __tablename__ = "category_panne"
    id = Column(Integer, primary_key=True, index=True)
    nom_panne = Column(String, nullable=False)
##################################################################################################################

class Panne(Base):
    __tablename__ = "panne"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id"))
    nom_panne_id = Column(Integer, ForeignKey("category_panne.id"))
    description = Column(String, nullable=True)
    status = Column(String, default="active")
    panne_date = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
##################################################################################################################

class Reparation(Base):
    __tablename__ = "reparation"
    id = Column(Integer, primary_key=True, index=True)
    panne_id = Column(Integer, ForeignKey("panne.id"))
    cost = Column(Float, default=0.0)
    receipt = Column(String, nullable=False)
    garage_id = Column(Integer, ForeignKey("garage.id"))
    repair_date = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String, default="Inprogress")