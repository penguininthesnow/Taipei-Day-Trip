import mysql.connector
from mysql.connector import pooling

dbconfig={
    "host":"localhost",
    "user":"root",
    "password":"12345678",
    "database": "taipei_day_trip"
}

connection_pool=pooling.MySQLConnectionPool(
    pool_name="taipei",
    pool_size=5,
    **dbconfig
)

def get_connection():
    return connection_pool.get_connection()