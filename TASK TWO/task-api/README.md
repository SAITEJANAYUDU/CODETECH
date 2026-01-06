server:
curl http://localhost:5001/


Tasks:
curl http://localhost:5001/tasks


Create task:
curl -X POST http://localhost:5001/tasks -H "Content-Type: application/json" -d "{\"title\":\"First Task\"}"

