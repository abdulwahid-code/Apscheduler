from flask import Flask, jsonify, request
from scheduler import Scheduler
import time
from datetime import datetime, timedelta
from dateutil import parser

app = Flask(__name__)
scheduler = Scheduler()

# API endpoint for scheduling a task
@app.route('/schedule', methods=['POST'])
def schedule_task():
    data = scheduler.create_student_table()

    name = request.json['name']
    age = request.json['age']
    scheduled_time = request.json['scheduled_time']
    repeat_scheduled_time = request.json['repeat_scheduled_time']
      
    repeat_interval = request.json['repeat_interval']
    # repeat_time = request.json['repeat_time']
    repeat_type = request.json['repeat_type']
    
    # Schedule a task to check for pending tasks every 10 minutes
    scheduler.insert_data(name, age, scheduled_time,repeat_interval, repeat_type,repeat_scheduled_time)
    scheduler.check_pending()
    
    scheduler.schedule_task(name, age, scheduled_time)

    scheduler.schedule_repeat_task(name, age, repeat_interval, repeat_scheduled_time, repeat_type, scheduled_time)
    return jsonify({'message': 'Repeat task scheduled successfully'})

@app.route('/update', methods=['POST'])
def update_task():
    name = request.json['name']
    scheduled_time = request.json['scheduled_time']
    scheduled_time = parser.parse(scheduled_time)

    # Get the existing data for the task
    rows = scheduler.get_data()
    task_data = None
    for row in rows:
        if row[0] == name:
            task_data = row
            break

    # Prompt the user to confirm the changes
    if task_data is not None:
        print("Current data:")
        print(f"Name: {task_data[0]}")
        print(f"Age: {task_data[1]}")
        print(f"Scheduled Time: {task_data[2]}")

        # print("Updated data:")
        # print(f"Name: {name}")
        age = request.json('age', task_data[1])
        # print(f"Age: {age}")
        # print(f"Scheduled Time: {scheduled_time}")

        confirm = input("Are you sure you want to update this task? (y/n) ")
        if confirm.lower() == "y":
            scheduler.update_status(name, age, scheduled_time)
            return jsonify({'message': 'Task updated successfully'})
        else:
            return jsonify({'message': 'Task update cancelled'})
    else:
        return jsonify({'message': 'Task not found'})

# API endpoint for deleting a task
@app.route('/delete', methods=['DELETE'])
def delete_task():
    # id = request.json['id']
    success = scheduler.delete_task()
    if success:
        return jsonify({'message': 'Task deleted successfully.'})
    else:
        return jsonify({'message': 'Task not found.'})

if __name__ == '__main__':
    app.run(debug=True)

