
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),
    "database": os.getenv("MYSQLDATABASE", "dyslexia_study"),
    "port": int(os.getenv("MYSQLPORT", 3306))
}

def apply_migration():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connected to database...")

        columns_to_add = [
            ("accuracy", "FLOAT DEFAULT 0"),
            ("skipped_words", "INT DEFAULT 0"),
            ("mispronounced_words", "INT DEFAULT 0"),
            ("extra_words", "INT DEFAULT 0"),
            ("transcribed_text", "TEXT")
        ]

        for col_name, col_def in columns_to_add:
            try:
                print(f"Adding column {col_name}...")
                cursor.execute(f"ALTER TABLE reading_progress ADD COLUMN {col_name} {col_def}")
                print(f"Column {col_name} added successfully.")
            except mysql.connector.Error as err:
                if err.errno == 1060: # Duplicate column name
                    print(f"Column {col_name} already exists. Skipping.")
                else:
                    print(f"Error adding {col_name}: {err}")

        conn.commit()
        cursor.close()
        conn.close()
        print("Migration complete.")
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    apply_migration()
