from fastapi import APIRouter, HTTPException, Depends
import pymysql
import bcrypt
from utils.database import get_db_connection, DatabaseConfig
from models import User, UserCreate, Vehicle, VehicleCreate, LoginRequest
import jwt
from datetime import datetime, timedelta
from dependencies import verify_token

router = APIRouter(
    prefix="/mobile",
    tags=["mobile"]
)

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

@router.post("/signup/", response_model=User)
def create_user(user: UserCreate):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE national_id = %s", (user.national_id,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="User already exists")
            
            hashed_password = hash_password(user.password)
            
            sql = """
                INSERT INTO users (national_id, name, phone_number, email, password, type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                user.national_id,
                user.name,
                user.phone_number,
                user.email,
                hashed_password,
                user.type
            ))
            connection.commit()
            
            return {
                "national_id": user.national_id,
                "name": user.name,
                "phone_number": user.phone_number,
                "email": user.email,
                "type": user.type
            }
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.post("/login/")
def login(login_request: LoginRequest):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT national_id, name, password, type 
                FROM users 
                WHERE national_id = %s
            """, (login_request.national_id,))
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            if not bcrypt.checkpw(login_request.password.encode('utf-8'), user['password'].encode('utf-8')):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            access_token = create_access_token(
                data={"sub": user['national_id'], "type": user['type']}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "national_id": user['national_id'],
                "name": user['name'],
                "type": user['type'],
                "message": "Login successful"
            }
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.get("/users/", response_model=list[User], dependencies=[Depends(verify_token)])
def read_users():
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT national_id, name, phone_number, email, type FROM users")
            users = cursor.fetchall()
            return list(users)
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.get("/users/{national_id}", response_model=User, dependencies=[Depends(verify_token)])
def read_user(national_id: str):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT national_id, name, phone_number, email, type 
                FROM users 
                WHERE national_id = %s
            """, (national_id,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.post("/vehicles/", response_model=Vehicle, dependencies=[Depends(verify_token)])
def create_vehicle(vehicle: VehicleCreate):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT password FROM users 
                WHERE national_id = %s
            """, (vehicle.national_id,))
            user = cursor.fetchone()
            if not user or not bcrypt.checkpw(vehicle.password.encode('utf-8'), user['password'].encode('utf-8')):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            sql = """
                INSERT INTO vehicles (national_id, vehicle, password, vehicle_type)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                vehicle.national_id,
                vehicle.vehicle,
                user['password'],  # Store the hashed password
                vehicle.vehicle_type
            ))
            connection.commit()
            return {
                "national_id": vehicle.national_id,
                "vehicle": vehicle.vehicle,
                "vehicle_type": vehicle.vehicle_type
            }
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.get("/vehicles/", response_model=list[Vehicle], dependencies=[Depends(verify_token)])
def read_vehicles():
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT national_id, vehicle, vehicle_type FROM vehicles")
            vehicles = cursor.fetchall()
            return [
                {
                    "national_id": vehicle["national_id"],
                    "vehicle": vehicle["vehicle"],
                    "vehicle_type": vehicle["vehicle_type"]
                }
                for vehicle in vehicles
            ]
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.get("/vehicles/{national_id}", response_model=list[Vehicle], dependencies=[Depends(verify_token)])
def read_user_vehicles(national_id: str):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT national_id, vehicle, vehicle_type 
                FROM vehicles 
                WHERE national_id = %s
            """, (national_id,))
            vehicles = cursor.fetchall()
            if not vehicles:
                raise HTTPException(status_code=404, detail="No vehicles found for this user")
            return [
                {
                    "national_id": vehicle["national_id"],
                    "vehicle": vehicle["vehicle"],
                    "vehicle_type": vehicle["vehicle_type"]
                }
                for vehicle in vehicles
            ]
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.get("/users/me-protected", dependencies=[Depends(verify_token)])
def read_current_user_protected():
    return {"message": "You are authenticated with a valid backend token."}