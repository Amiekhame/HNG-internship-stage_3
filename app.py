import os
import logging
from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
from celery import Celery
from tasks import send_email
from celery.result import AsyncResult

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(_name_)

########################## CELERY #########################################
# Configure Celery
celery = Celery(
    _name_,
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND')
)

# Configure logging
log_path = '/var/log/messaging_system.log'
print(f"Log file path: {log_path}")

logging.basicConfig(
    filename=home/vagrant/messaging_system.log,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Set to DEBUG to capture all log levels
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set to DEBUG to capture all log levels
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

print("Logging is configured")

@app.route('/')
def index():
    logging.info('Accessed index route.')
    print('Accessed index route.')
    sendmail = request.args.get('sendmail')
    talktime = request.args.get('talktime')

    if sendmail and talktime:
        task = send_email.delay(sendmail)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f'Email task queued with task id: {task.id}')
        print(f'Email task queued with task id: {task.id}')
        return jsonify({
            'message': 'Email task has been queued.',
            'task_id': task.id
        }), 200
    logging.warning('Both sendmail and talktime parameters are required.')
    print('Both sendmail and talktime parameters are required.')
    return 'Both sendmail and talktime parameters are required.', 400

@app.route('/task_status/<task_id>')
def get_task_status(task_id):
    result = AsyncResult(task_id, app=celery)
    logging.info(f'Checking status for task id: {task_id}')
    print(f'Checking status for task id: {task_id}')
    status = result.state
    logging.info(f'Task status for {task_id}: {status}')
    print(f'Task status for {task_id}: {status}')

    if status == 'SUCCESS':
        result_data = result.result
        logging.info(f'Email sent successfully to {result_data["email"]}')
        print(f'Email sent successfully to {result_data["email"]}')
        return jsonify({
            'status': 'SUCCESS',
            'message': f'Email sent successfully to {result_data["email"]}'
        }), 200
    elif status == 'FAILURE':
        result_data = result.result
        logging.error(f'Failed to send email: {result_data["error"]}')
        print(f'Failed to send email: {result_data["error"]}')
        return jsonify({
            'status': 'FAILURE',
            'message': f'Failed to send email: {result_data["error"]}'
        }), 400
    elif status in ['PENDING', 'RECEIVED', 'STARTED']:
        logging.info('Email sending in progress')
        print('Email sending in progress')
        return jsonify({
            'status': 'PENDING',
            'message': 'Email sending in progress'
        }), 202
    else:
        logging.warning('Task status unknown')
        print('Task status unknown')
        return jsonify({
            'status': 'UNKNOWN',
            'message': 'Task status unknown'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)