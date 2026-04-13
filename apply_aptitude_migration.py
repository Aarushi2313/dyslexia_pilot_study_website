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
        
        aptitude_task_columns = [
            ("listening_audio_url", "VARCHAR(255)"),
            ("listening_q1", "TEXT"),
            ("listening_q1_options", "JSON"),
            ("listening_q1_answer", "TEXT"),
            ("listening_q2", "TEXT"),
            ("listening_q2_options", "JSON"),
            ("listening_q2_answer", "TEXT"),
            ("listening_q3", "TEXT"),
            ("listening_q3_answer", "TEXT"),
            ("visual_image_url", "VARCHAR(255)"),
            ("visual_q1", "TEXT"),
            ("visual_q1_options", "JSON"),
            ("visual_q1_answer", "TEXT"),
            ("visual_q2", "TEXT"),
            ("visual_q2_options", "JSON"),
            ("visual_q2_answer", "TEXT"),
            ("visual_q3", "TEXT"),
            ("visual_q3_answer", "TEXT")
        ]

        aptitude_progress_columns = [
            ("listening_task_score", "INT DEFAULT 0"),
            ("visual_task_score", "INT DEFAULT 0")
        ]

        for col_name, col_def in aptitude_task_columns:
            try:
                cursor.execute(f"ALTER TABLE aptitude_tasks ADD COLUMN {col_name} {col_def}")
                print(f"Added column {col_name} to aptitude_tasks")
            except mysql.connector.Error as err:
                 # ignore if column exists
                if err.errno == 1060:
                    print(f"Column {col_name} already exists in aptitude_tasks.")
                else:
                    print(f"Error adding {col_name} to aptitude_tasks: {err}")

        for col_name, col_def in aptitude_progress_columns:
            try:
                cursor.execute(f"ALTER TABLE aptitude_progress ADD COLUMN {col_name} {col_def}")
                print(f"Added column {col_name} to aptitude_progress")
            except mysql.connector.Error as err:
                 # ignore if column exists
                if err.errno == 1060:
                    print(f"Column {col_name} already exists in aptitude_progress.")
                else:
                    print(f"Error adding {col_name} to aptitude_progress: {err}")

        # Update max_score to 10
        try:
            cursor.execute("ALTER TABLE aptitude_progress MODIFY COLUMN max_score INT DEFAULT 10")
            print("Updated max_score default in aptitude_progress to 10")
        except mysql.connector.Error as err:
            print(f"Error updating max_score in aptitude_progress: {err}")

        try:
            cursor.execute("UPDATE aptitude_progress SET max_score = 10")
            print("Set max_score = 10 for existing records in aptitude_progress")
        except mysql.connector.Error as err:
            print(f"Error updating existing max_score in aptitude_progress: {err}")

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
