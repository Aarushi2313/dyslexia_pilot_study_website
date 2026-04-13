import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv('MYSQLHOST', 'localhost'),
    user=os.getenv('MYSQLUSER', 'root'),
    password=os.getenv('MYSQLPASSWORD', ''),
    database=os.getenv('MYSQLDATABASE', 'aviendbnew'),
    port=int(os.getenv('MYSQLPORT', '3306'))
)

cursor = db.cursor()

# Set all aptitude tasks to point to your new media files and provide placeholder questions
update_query = """
    UPDATE aptitude_tasks 
    SET listening_audio_url = 'listening_task_1.mp3',
        listening_q1 = 'What was the main topic of the audio recording?',
        listening_q1_options = '["A conversation", "A lecture", "A news report", "A story"]',
        listening_q2 = 'Which word was NOT mentioned in the audio?',
        listening_q2_options = '["Apple", "Banana", "Orange", "Grape"]',
        listening_q3 = 'Summarize what you heard in 2-3 sentences.',
        visual_image_url = 'visual_task_1.jpg',
        visual_q1 = 'What is the main color of the object in the image?',
        visual_q1_options = '["Red", "Blue", "Green", "Yellow"]',
        visual_q2 = 'How many distinct shapes can you see?',
        visual_q2_options = '["One", "Two", "Three", "Four"]',
        visual_q3 = 'Describe the image in detail.'
    WHERE listening_audio_url IS NULL OR visual_image_url IS NULL
"""

cursor.execute(update_query)
db.commit()

print(f"Successfully updated {cursor.rowcount} aptitude tasks with placeholder questions and media links!")
cursor.close()
db.close()
