import os 
from dotenv import load_dotenv
from pathlib import Path
import mysql.connector
from mysql.connector import pooling

# .env
env_path = Path(__file__).resolve().parent.parent
ENV_path = env_path / ".env"

load_dotenv(dotenv_path=ENV_path)

# load_dotenv() # 載入 .env

dbconfig={
    # "host":"localhost",
    # "user":"root",
    # "password":"12345678",
    # "database": "taipei_day_trip"
    "host": os.getenv("DB_HOST"),  # 127.0.0.1
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "use_pure": True
}

if not all(dbconfig.values()):
    raise RuntimeError("Database env are not correctly")

connection_pool= pooling.MySQLConnectionPool(
    pool_name="taipei",
    pool_size=5,
    **dbconfig
)

def get_connection():
    return connection_pool.get_connection()

# conn = get_connection()
# print("DB connection id:", conn.connection_id)
# conn.close()