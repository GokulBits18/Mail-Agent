import imaplib
import email
from email.header import decode_header
import os
import re
import html
from dotenv import load_dotenv
from database import SessionLocal, EmailRecord

load_dotenv()
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = "imap.gmail.com"

def decode_field(field_value):
    if not field_value:
        return "Unknown"
    decoded_parts = decode_header(field_value) 
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding if encoding else "utf-8", errors="ignore")
        else:
            result += str(part)
    return result

def get_email_body(msg):
    body = ""
    is_html = False

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition"))
            
            if "attachment" in disposition:
                continue
                
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                break 
            elif content_type == "text/html" and not body:
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                is_html = True
    else:
        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        if msg.get_content_type() == "text/html":
            is_html = True
            
    if is_html or "<html" in body.lower() or "<style" in body.lower():
        body = re.sub(r'<style[^>]*>.*?</style>', ' ', body, flags=re.IGNORECASE | re.DOTALL)
        body = re.sub(r'<script[^>]*>.*?</script>', ' ', body, flags=re.IGNORECASE | re.DOTALL)
        body = re.sub(r'<[^>]+>', ' ', body)
        body = html.unescape(body)
            
    return re.sub(r'\s+', ' ', body).strip()

def fetch_unread_emails():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        
        if not messages[0]:
            return {"status": "success", "fetched": 0}
            
        email_ids = messages[0].split()
        email_ids = email_ids[-10:]
        
        fetched_count = 0
        db = SessionLocal()

        for e_id in email_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject = decode_field(msg["Subject"])
                    sender = decode_field(msg.get("From"))
                    body = get_email_body(msg)

                    existing_email = db.query(EmailRecord).filter_by(subject=subject, sender=sender).first()
                    
                    if not existing_email:
                        new_email = EmailRecord(
                            sender=sender,
                            subject=subject,
                            content=body,
                            priority="Unassigned", 
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