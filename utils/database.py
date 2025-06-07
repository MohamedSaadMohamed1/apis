import os
import pymysql
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    TRAFFIC_MANAGER = {
        "host": os.getenv("TRAFFIC_DB_HOST"),
        "port": int(os.getenv("TRAFFIC_DB_PORT")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": "trafficManagerFull"
    }

def get_db_connection(config):
    if not isinstance(config, dict):
        raise TypeError("Expected a dictionary for database configuration")
    try:
        return pymysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )
    except socket.gaierror as e:
        raise ConnectionError(f"Hostname resolution failed for {config['host']}: {e}")
    except pymysql.err.OperationalError as e:
        raise ConnectionError(f"Operational error while connecting to the database: {e}")