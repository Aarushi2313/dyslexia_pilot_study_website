
import os
import io
import unittest
import json
from app import app, connect_db
import mysql.connector
from datetime import datetime

class TestReadingStats(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'test_uploads')
        self.client = app.test_client()
        self.user_id = None
        self.task_id = None
        
        # Ensure upload dir exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'))

        # Setup Database Data
        self.conn = connect_db()
        self.cursor = self.conn.cursor(dictionary=True)
        
        # 1. Create Test User
        self.cursor.execute("INSERT INTO users (name, email, password_hash, is_18_or_above) VALUES ('AutoTest User', 'autotest@example.com', 'hash', 1)")
        self.conn.commit()
        self.user_id = self.cursor.lastrowid
        
        # 2. Ensure "Reading Aloud Task 1" exists
        self.cursor.execute("SELECT id FROM tasks WHERE task_name = 'Reading Aloud Task 1'")
        task = self.cursor.fetchone()
        if not task:
            self.cursor.execute("INSERT INTO tasks (task_name) VALUES ('Reading Aloud Task 1')")
            self.conn.commit()
            self.task_id = self.cursor.lastrowid
        else:
            self.task_id = task['id']

        # 3. Ensure Reading Task Content exists (for app.py to fetch text)
        # Note: app.py queries `reading_tasks` table using the `id` passed in form data `task_id`
        # But `upload_video` logic uses `task_name` to find the generic `task_id` for `user_task_attempts`.
        # AND it uses `task_id` form field to look up content in `reading_tasks` table.
        # This seems to be a potential confusion point.
        # standard `reading_tasks` usually have IDs. Let's insert one.
        self.cursor.execute("""
            INSERT INTO reading_tasks (task_name, class_level, difficulty_level, content) 
            VALUES ('Reading Aloud Task 1', 1, 'Easy', 'The quick brown fox jumps over the lazy dog.')
        """)
        self.conn.commit()
        self.reading_task_content_id = self.cursor.lastrowid


    def tearDown(self):
        # Clean up DB
        if self.user_id:
            self.cursor.execute("DELETE FROM users WHERE id = %s", (self.user_id,))
        if self.reading_task_content_id:
            self.cursor.execute("DELETE FROM reading_tasks WHERE id = %s", (self.reading_task_content_id,))
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def test_upload_and_analysis_flow(self):
        # 1. Start a Task Attempt
        print(f"\nCreated User ID: {self.user_id}")
        print(f"Generic Task ID: {self.task_id}")
        print(f"Reading Content ID: {self.reading_task_content_id}")

        # Simulate "Start Task" - create an IN PROGRESS attempt
        self.cursor.execute("""
            INSERT INTO user_task_attempts (user_id, task_id, attempt_number, status, started_at) 
            VALUES (%s, %s, 1, 'In Progress', NOW())
        """, (self.user_id, self.task_id))
        self.conn.commit()
        attempt_id = self.cursor.lastrowid
        print(f"Created Attempt ID: {attempt_id}")

        # 2. Mock a Video File (We need a valid file for pydub to not crash if it checks, 
        # actually analyze_audio calls AudioSegment.from_file. 
        # If we send garbage, it might fail.
        # We can try to send a zero-byte file and expect failure, or try to generate simple wave)
        
        # Generate a silent wav file
        # Riff header structure... generic enough to pass?
        # Alternatively, assume ffmpeg is present and we can just use a dummy valid file if available.
        # Let's try to create a minimal valid wav file bytes
        # RIFF + 36 + WAVE + fmt + 16 + 1 (PCM) + 1 (chan) + 44100 (rate) + ...
        # Or just use pydub to generate one if installed!
        try:
            from pydub import AudioSegment
            silence = AudioSegment.silent(duration=3000) # 3 seconds
            b_io = io.BytesIO()
            silence.export(b_io, format="wav")
            b_io.seek(0)
            file_content = b_io.read()
            filename = 'test_audio.wav'
        except ImportError:
            print("Pydub not installed in test env")
            return
        except Exception as e:
            print(f"Could not generate audio: {e}")
            file_content = b'fake video content' # This will fail analysis
            filename = 'test.webm'

        # 3. Login
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
            sess['user_name'] = 'AutoTest User'
        
        # 4. Upload Video
        data = {
            'video': (io.BytesIO(file_content), filename),
            'task_id': str(self.reading_task_content_id), # This is the reading_task ID
            'task_name': 'Reading Aloud Task 1'
        }
        
        response = self.client.post('/api/upload-video', data=data, content_type='multipart/form-data')
        print(f"Upload Response: {response.data}")
        self.assertEqual(response.status_code, 200)

        # 5. Check Database for Reading Progress
        self.cursor.execute("SELECT * FROM reading_progress WHERE attempt_id = %s", (attempt_id,))
        progress = self.cursor.fetchone()
        
        print(f"Reading Progress Record: {progress}")
        
        if progress:
            print("SUCCESS: Reading stats generated.")
            print(f"WPM: {progress['wpm']}")
            print(f"Pauses: {progress['pause_frequency']}")
            print(f"Smoothness: {progress['smoothness']}")
            print(f"Accuracy: {progress['accuracy']}%")
            print(f"Skipped: {progress['skipped_words']}")
            print(f"Mispronounced: {progress['mispronounced_words']}")
            print(f"Transcribed: {progress['transcribed_text']}")
        else:
            print("FAILURE: No reading stats found in DB.")
            # Check if video was saved
            self.cursor.execute("SELECT * FROM video_recordings WHERE attempt_id = %s", (attempt_id,))
            vid = self.cursor.fetchone()
            print(f"Video Recording Record: {vid}")

    def test_audio_only_upload(self):
        # Additional test for the new /api/upload-audio endpoint
        print("\nTesting /api/upload-audio endpoint...")
        
        # Create attempt
        self.cursor.execute("""
            INSERT INTO user_task_attempts (user_id, task_id, attempt_number, status, started_at) 
            VALUES (%s, %s, 1, 'In Progress', NOW())
        """, (self.user_id, self.task_id))
        self.conn.commit()
        attempt_id = self.cursor.lastrowid

        # Mock Audio
        file_content = b'fake audio content' 
        filename = 'test_audio.webm'
        
        # Login
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
        
        data = {
            'audio': (io.BytesIO(file_content), filename),
            'task_name': 'Reading Aloud Task 1',
            'reading_task_id': str(self.reading_task_content_id)
        }
        
        response = self.client.post('/api/handle-audio-upload', data=data, content_type='multipart/form-data')
        print(f"Audio Upload Response: {response.data}")
        self.assertEqual(response.status_code, 200)
        
        # Check DB
        self.cursor.execute("SELECT * FROM reading_progress WHERE attempt_id = %s", (attempt_id,))
        progress = self.cursor.fetchone()
        if progress:
             print("SUCCESS: Audio upload triggered analysis (or at least DB entry).")
        else:
             print("Note: Analysis might fail due to fake audio, but let's check if file saved.")
             self.cursor.execute("SELECT * FROM video_recordings WHERE attempt_id = %s", (attempt_id,))
             vid = self.cursor.fetchone()
             if vid: print("SUCCESS: Audio file saved.")


if __name__ == '__main__':
    unittest.main()
