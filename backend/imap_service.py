import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
from database import SessionLocal, EmailRecord

# Load credentials from .env
load_dotenv()
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = "imap.gmail.com"

def get_email_body(msg):
    """Helper function to extract plain text from the email body."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
    else:
        return msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    return ""

def fetch_unread_emails():
    """Connects to IMAP, fetches unread emails, and saves them to SQLite."""
    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        # Search for all unread emails
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        # NEW FIX: Only process the 5 most recent unread emails to prevent connection drops
        email_ids = email_ids[-5:]
        
        fetched_count = 0
        db = SessionLocal()

        for e_id in email_ids:
            # Fetch the raw email
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Decode the subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")

                    # Get sender and body
                    sender = msg.get("From")
                    body = get_email_body(msg)

                    # Save to database
                    new_email = EmailRecord(
                        sender=sender,
                        subject=subject,
                        content=body.strip(),
                        status="Pending"
                    )
                    db.add(new_email)
                    db.commit()
                    fetched_count += 1
        
        db.close()
        mail.logout()
        return {"status": "success", "fetched": fetched_count}

    except Exception as e:
        return {"status": "error", "message": str(e)}