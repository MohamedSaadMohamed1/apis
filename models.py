from pydantic import BaseModel

# Traffic Lights Models
class TrafficSignalBase(BaseModel):
    lat: float
    lon: float
    tl_id_sumo: str
    tl_id_osm: str

class TrafficSignalCreate(TrafficSignalBase):
    pass

class TrafficSignal(TrafficSignalBase):
    class Config:
        orm_mode = True

# Mobile (Users/Vehicles) Models
class UserBase(BaseModel):
    national_id: str
    name: str
    phone_number: str
    email: str
    type: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    class Config:
        orm_mode = True

class VehicleBase(BaseModel):
    national_id: str
    vehicle: str
    vehicle_type: str

class VehicleCreate(VehicleBase):
    password: str

class Vehicle(VehicleBase):
    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    national_id: str
    password: str