from fastapi import APIRouter, HTTPException, Depends
import pymysql
from utils.database import get_db_connection, DatabaseConfig
from models import TrafficSignal, TrafficSignalCreate
from dependencies import verify_token

router = APIRouter(
    prefix="/traffic-lights",
    tags=["traffic_lights"]
)

@router.post("/", response_model=TrafficSignal, dependencies=[Depends(verify_token)])
def create_traffic_signal(signal: TrafficSignalCreate):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO traffic_signals (lat, lon, tl_id_sumo, tl_id_osm)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (signal.lat, signal.lon, signal.tl_id_sumo, signal.tl_id_osm))
            connection.commit()
            return signal
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()


@router.get("/", response_model=list[TrafficSignal], dependencies=[Depends(verify_token)])
def read_traffic_signals():
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT lat, lon, tl_id_sumo, tl_id_osm FROM traffic_signals")
            results = cursor.fetchall()
            return [
                {"lat": row["lat"], "lon": row["lon"], 
                 "tl_id_sumo": row["tl_id_sumo"], "tl_id_osm": row["tl_id_osm"]} 
                for row in results
            ]
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.get("/{lat}/{lon}", response_model=TrafficSignal, dependencies=[Depends(verify_token)])
def read_traffic_signal(lat: float, lon: float):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT lat, lon, tl_id_sumo, tl_id_osm FROM traffic_signals WHERE lat = %s AND lon = %s", (lat, lon))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Traffic signal not found")
            return {
                "lat": result["lat"], 
                "lon": result["lon"],
                "tl_id_sumo": result["tl_id_sumo"], 
                "tl_id_osm": result["tl_id_osm"]
            }
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.put("/{lat}/{lon}", response_model=TrafficSignal, dependencies=[Depends(verify_token)])
def update_traffic_signal(lat: float, lon: float, signal: TrafficSignalCreate):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor() as cursor:
            # First check if the record exists
            cursor.execute("SELECT * FROM traffic_signals WHERE lat = %s AND lon = %s", (lat, lon))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Traffic signal not found")
            
            # Update all fields
            sql = """
                UPDATE traffic_signals 
                SET lat = %s, lon = %s, tl_id_sumo = %s, tl_id_osm = %s
                WHERE lat = %s AND lon = %s
            """
            cursor.execute(sql, (signal.lat, signal.lon, signal.tl_id_sumo, signal.tl_id_osm, lat, lon))
            connection.commit()
            return signal.dict()
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@router.delete("/{lat}/{lon}", dependencies=[Depends(verify_token)])
def delete_traffic_signal(lat: float, lon: float):
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM traffic_signals WHERE lat = %s AND lon = %s", (lat, lon))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Traffic signal not found")
            connection.commit()
            return {"message": "Traffic signal deleted successfully"}
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()