import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS port for Gmail

def send_email(to_address: str, subject: str, body: str):
    """Sends an email using Gmail SMTP."""
    try:
        # 1. Set up the email format
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ACCOUNT
        msg['To'] = to_address
        msg['Subject'] = subject
        
        # Attach the body text
        msg.attach(MIMEText(body, 'plain'))

        # 2. Connect to the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        
        # 3. Login and send
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ACCOUNT, to_address, text)
        
        # 4. Close the connection
        server.quit()
        return {"status": "success", "message": f"Email sent to {to_address}"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}