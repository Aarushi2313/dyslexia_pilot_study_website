
import os
import mysql.connector
import json
import sys
from dotenv import load_dotenv

# Add current directory to path to import app
sys.path.append(os.getcwd())

# Load env
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),
    "database": os.getenv("MYSQLDATABASE", "aviendbnew"),
    "port": int(os.getenv("MYSQLPORT", 3306))
}

def check_schema():
    print("--- Checking Schema ---")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DESCRIBE typing_progress")
        columns = [row[0] for row in cursor.fetchall()]
        
        required_columns = [
            'spelling_error_rate', 
            'sentence_length_variance', 
            'edit_density', 
            'insertions', 
            'deletions'
        ]
        
        missing = [col for col in required_columns if col not in columns]
        
        if missing:
            print(f"FAILED: Missing columns: {missing}")
        else:
            print("SUCCESS: All required columns present.")
            
        conn.close()
    except Exception as e:
        print(f"Error checking schema: {e}")

def test_logic():
    print("\n--- Testing Logic ---")
    try:
        from app import calculate_typing_metrics
        
        # Test Case 1: Simple text with error against ground truth
        reference_text = "The quick brown fox jumps over the lazy dog."
        text = "The quick brown fox jumps over the lazy dogg."
        keystrokes = [
            {'key': 'T'}, {'key': 'h'}, {'key': 'e'}, {'key': ' '},
            {'key': 'q'}, {'key': 'Backspace'}, {'key': 'q'} 
        ]
        
        metrics = calculate_typing_metrics(text, keystrokes, reference_text)
        print(f"Metrics for '{text}':")
        print(json.dumps(metrics, indent=2))
        
        # assertions
        if metrics['spelling_error_rate'] > 0:
            print("SUCCESS: Spelling error detected (dogg).")
        else:
            print("FAILED: No spelling error detected.")
            
        if metrics['deletions'] == 1:
            print("SUCCESS: Deletions counted correctly.")
        else:
            print(f"FAILED: Deletions count {metrics['deletions']} != 1")

    except ImportError:
        print("FAILED: Could not import app.py. Make sure you are in the right directory.")
    except Exception as e:
        print(f"Error testing logic: {e}")

if __name__ == "__main__":
    check_schema()
    test_logic()
