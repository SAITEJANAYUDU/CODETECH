# TASK MANAGEMENT API - SIMPLE VERSION
from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# File to store tasks
TASKS_FILE = 'tasks.json'

# Load tasks from file
def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

# Save tasks to file
def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

# Create file if doesn't exist
if not os.path.exists(TASKS_FILE):
    save_tasks([])

# ========== ROUTES ==========

@app.route('/')
def home():
    return jsonify({
        'message': '✅ TASK MANAGEMENT API',
        'version': '1.0.0',
        'description': 'Simple REST API for managing tasks',
        'endpoints': {
            'GET /tasks': 'Get all tasks',
            'POST /tasks': 'Create new task',
            'GET /tasks/<id>': 'Get single task',
            'PUT /tasks/<id>': 'Update task',
            'DELETE /tasks/<id>': 'Delete task'
        }
    })

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify({
        'success': True,
        'count': len(tasks),
        'tasks': tasks
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        tasks = load_tasks()
        
        # Find max ID
        max_id = max([task.get('id', 0) for task in tasks], default=0)
        
        new_task = {
            'id': max_id + 1,
            'title': data['title'],
            'description': data.get('description', ''),
            'completed': False
        }
        
        tasks.append(new_task)
        save_tasks(tasks)
        
        return jsonify({
            'success': True,
            'message': 'Task created successfully',
            'task': new_task
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 TASK MANAGEMENT API STARTING...")
    print("📍 URL: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)