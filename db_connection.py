import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",   # XAMPP e default password khali thake
    "database": "hospital_management",
    "port": 3306
}


def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection failed: {e}")
        return None


if __name__ == "__main__":
    conn = get_connection()
    if conn and conn.is_connected():
        print("Connected to hospital_db successfully!")
        conn.close()
    else:
        print("Connection failed. Check DB_CONFIG values.")