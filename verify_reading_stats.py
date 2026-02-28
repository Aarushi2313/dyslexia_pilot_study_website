
import unittest
from app import app, connect_db
import json

class TestStartScores(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.user_id = 1 # Assuming user 1 exists, or we mock
        
    def test_get_scores(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
            
        response = self.client.get(f'/api/student-scores/{self.user_id}')
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        if data['stats']['reading_stats']:
            print("Reading Stats Found:", data['stats']['reading_stats'])
            self.assertIn('accuracy', data['stats']['reading_stats'])
            self.assertIn('skipped_words', data['stats']['reading_stats'])
        else:
            print("No reading stats found for this user (expected if no task done), but endpoint works.")

if __name__ == '__main__':
    unittest.main()
