from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
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
    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_date = Column(TIMESTAMP(timezone=True), nullable=False)
    return_date = Column(TIMESTAMP(timezone=True), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id"))
    driver_id = Column(Integer, ForeignKey("user.id"))

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
    purchase_date = Column(Float, default=0.0)
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
    id = Column(Integer, primary_key=True, index=True)
    cat_maintenance_id = Column(Integer, ForeignKey("category_maintenance.id"))
    vehicule_id = Column(Integer, ForeignKey("vehicle.id"))
    garage_id = Column(Integer, ForeignKey("garage.id"))
    maintenance_cost = Column(Float, default=0.0)
    receipt = Column(String, nullable=False)
    maintenance_date = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
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