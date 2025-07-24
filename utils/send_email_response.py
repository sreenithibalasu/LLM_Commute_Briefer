import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()
# -- Config --
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL =  os.getenv("RECIPIENT_EMAIL")
JSON_FILE_PATH = os.getenv("PROMPT_OUTPUT_FILENAME")

def send_email():
	with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
		data = json.load(f)

	decoded_text = data["claude_output"]

	# -- Compose --
	msg = MIMEMultipart("alternative")
	dt = datetime.now() + timedelta(days=1)
	formatted_date = dt.strftime("%B %d, %Y")
	msg["Subject"] = "{} - Commute Briefing".format(formatted_date)
	msg["From"] = SENDER_EMAIL
	msg["To"] = RECIPIENT_EMAIL

	# Add plain text version
	msg.attach(MIMEText(decoded_text, "plain"))

	# -- Send --
	try:
		with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
			server.login(SENDER_EMAIL, SENDER_PASSWORD)
			server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
		print("Email sent successfully!")
	except Exception as e:
		print(f"Failed to send email: {e}")

