
import os
import mysql.connector
from dotenv import load_dotenv

if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),
    "database": os.getenv("MYSQLDATABASE", "aviendbnew"),
    "port": int(os.getenv("MYSQLPORT", 3306))
}

def apply_migration():
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        columns = [
            ("spelling_error_rate", "FLOAT DEFAULT 0"),
            ("sentence_length_variance", "FLOAT DEFAULT 0"),
            ("edit_density", "FLOAT DEFAULT 0"),
            ("insertions", "INT DEFAULT 0"),
            ("deletions", "INT DEFAULT 0")
        ]

        for col_name, col_def in columns:
            try:
                cursor.execute(f"ALTER TABLE typing_progress ADD COLUMN {col_name} {col_def}")
                print(f"Added column {col_name}")
            except mysql.connector.Error as err:
                 # ignore if column exists
                if err.errno == 1060:
                    print(f"Column {col_name} already exists.")
                else:
                    print(f"Error adding {col_name}: {err}")

        conn.commit()
        print("Schema update completed successfully")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    apply_migration()
