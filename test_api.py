import json
from app import app
app.testing = True
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    res = client.get('/api/aptitude-tasks/1')
    data = res.json
    if data and 'tasks' in data:
        print("Task name:", data['tasks'][0]['task_name'])
        print("Logical:", data['tasks'][0].get('logical_question'))
    else:
        print("Error:", data)
