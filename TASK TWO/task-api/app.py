

from flask import Flask, jsonify, request
import json
import os


app = Flask(__name__)

TASKS_FILE = "tasks.json"


def load_tasks():
    """Load tasks from JSON file"""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as file:
                return json.load(file)
        except:
            return []
    return []

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file, indent=2)

def get_next_id(tasks):
    """Get next available ID"""
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

@app.route('/')
def home():
    """API documentation"""
    return jsonify({
        'api': 'Task Management System',
        'version': '1.0.0',
        'description': 'A simple REST API for managing tasks',
        'endpoints': {
            'GET /tasks': 'Get all tasks',
            'POST /tasks': 'Create a new task',
            'GET /tasks/<id>': 'Get a single task',
            'PUT /tasks/<id>': 'Update a task',
            'DELETE /tasks/<id>': 'Delete a task',
            'GET /health': 'Check API health'
        }
    })

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    """Retrieve all tasks"""
    tasks = load_tasks()
    return jsonify({
        'success': True,
        'count': len(tasks),
        'tasks': tasks
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        
        if not data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        
        tasks = load_tasks()
        
        
        new_task = {
            'id': get_next_id(tasks),
            'title': data['title'],
            'description': data.get('description', ''),
            'completed': False,
            'created_at': '2024-01-15'
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

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    tasks = load_tasks()
    
    
    for task in tasks:
        if task['id'] == task_id:
            return jsonify({
                'success': True,
                'task': task
            })
    
    return jsonify({
        'success': False,
        'error': f'Task with ID {task_id} not found'
    }), 404


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    
    try:
        data = request.get_json()
        tasks = load_tasks()
        
        
        for i, task in enumerate(tasks):
            if task['id'] == task_id:
                
                if 'title' in data:
                    tasks[i]['title'] = data['title']
                if 'description' in data:
                    tasks[i]['description'] = data.get('description', tasks[i]['description'])
                if 'completed' in data:
                    tasks[i]['completed'] = data['completed']
                
                
                save_tasks(tasks)
                
                return jsonify({
                    'success': True,
                    'message': 'Task updated successfully',
                    'task': tasks[i]
                })
        
        return jsonify({
            'success': False,
            'error': f'Task with ID {task_id} not found'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    
    tasks = load_tasks()
    
    
    original_count = len(tasks)
    
    
    tasks = [task for task in tasks if task['id'] != task_id]
    
    if len(tasks) < original_count:
        save_tasks(tasks)
        return jsonify({
            'success': True,
            'message': f'Task with ID {task_id} deleted successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Task with ID {task_id} not found'
        }), 404

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'task-management-api',
        'timestamp': '2024-01-15'
    })

if __name__ == '__main__':
    
    if not os.path.exists(TASKS_FILE):
        save_tasks([])
        print(f" Created {TASKS_FILE}")
    
    print("=" * 60)
    print(" TASK MANAGEMENT API")
    print("=" * 60)
    print(" URL: http://localhost:5001")
    print(" API Documentation available at: /")
    print("  Endpoints:")
    print("   • GET    /tasks         - Get all tasks")
    print("   • POST   /tasks         - Create task")
    print("   • GET    /tasks/<id>    - Get single task")
    print("   • PUT    /tasks/<id>    - Update task")
    print("   • DELETE /tasks/<id>    - Delete task")
    print("   • GET    /health        - Health check")
    print("=" * 60)
    
    app.run(debug=True, port=5001, use_reloader=False)