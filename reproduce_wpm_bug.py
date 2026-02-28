import os
import sys
from pydub import AudioSegment
from pydub.generators import Sine

# Add current directory to path
sys.path.append(os.getcwd())

# Import from app.py
from app import connect_db, analyze_audio

def create_short_audio():
    # Create 5 seconds of audio representing 10 words spoken
    # Use Sine wave generator
    return Sine(440).to_audio_segment(duration=5000)

def reproduction_test():
    print("--- Reproducing WPM Calculation Issue ---")
    
    # Connect DB to get a reading task text
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        # Get a task with ~40-60 words (Task 7 has 58 words, Task 5 has ~53?)
        cursor.execute("SELECT content FROM reading_tasks WHERE LENGTH(content) > 200 LIMIT 1")
        task = cursor.fetchone()
        conn.close()
        
        if not task:
            print("No suitable reading task found for test.")
            return

        content = task['content']
        words_in_db = len(content.split())
        print(f"Using DB Content ({words_in_db} words): {content[:50]}...")
        
        # Create a 5-second audio file (simulating reading ~10 words)
        audio = create_short_audio()
        temp_audio_path = "temp_reproduce.wav"
        audio.export(temp_audio_path, format="wav")
        
        # Call the function
        print(f"  Audio Duration: 5.0 seconds (simulating 10 words read)")
        print(f"  Task Content Length: {words_in_db} words (User supposedly stopped early)")
        
        # Call the function
        stats = analyze_audio(temp_audio_path, content)
        
        if stats:
            print("\n--- Results ---")
            print(f"Calculated WPM: {stats['wpm']}")
            print(f"Total Words Used: {stats['total_words']}")
            
            # 5 seconds = 0.0833 minutes.
            # If logic uses full text (e.g. 50 words): WPM = 50 / 0.0833 = 600 WPM
            expected_if_bug = words_in_db / (5/60)
            
            # If logic used actual words read (10 words): WPM = 10 / 0.0833 = 120 WPM
            expected_if_correct = 10 / (5/60)
            
            print(f"Expected WPM (Buggy Logic): ~{expected_if_bug:.0f}")
            print(f"Expected WPM (Correct Logic): ~{expected_if_correct:.0f}")
            
            if stats['wpm'] > 200:
                print("\n[CONCLUSION] BUG CONFIRMED: The system assumes the user read the ENTIRE text.")
            else:
                print("\n[CONCLUSION] BUG NOT REPRODUCED??")
        else:
            print("Analysis failed.")
            
        # Cleanup
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reproduction_test()
