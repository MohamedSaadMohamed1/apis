from fastapi import APIRouter, HTTPException
import pymysql
from utils.database import get_db_connection, DatabaseConfig

router = APIRouter(
    prefix="/rl-online",
    tags=["rl_online"]
)

@router.get("/")
def read_rl_data():
    connection = get_db_connection(DatabaseConfig.TRAFFIC_MANAGER)  # <-- Change to your RL DB config
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            return {"tables": tables}
    except pymysql.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()