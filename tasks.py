import os
import smtplib
import logging
from celery import Celery
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Celery
celery = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND')
)

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))

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

@celery.task(bind=True)
def send_email(self, email):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = email
        msg['Subject'] = "Subject: Test"
        body = "This is the stage 3 task given by HNG internship."
        msg.attach(MIMEText(body, 'plain'))

        server.sendmail(EMAIL, email, msg.as_string())
        server.quit()
        
        logging.info(f'Email sent to {email}')
        print(f"Email sent to {email}")
        return {'status': 'SUCCESS', 'email': email}  # Return the email address as the result
    except Exception as e:
        logging.error(f'Failed to send email to {email}: {e}')
        print(f"Failed to send email to {email}: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
        return {'status': 'FAILURE', 'error': str(e)}
