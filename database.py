import pymysql
from pymysql.cursors import DictCursor
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    TRAFFIC_MANAGER = {
        "host": os.getenv("TRAFFIC_DB_HOST"),
        "port": int(os.getenv("TRAFFIC_DB_PORT")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "db": "trafficManagerFull",
        "charset": "utf8mb4",
        "cursorclass": DictCursor
    }
    

@lru_cache()
def get_db_connection(config: dict):
    return pymysql.connect(**config)