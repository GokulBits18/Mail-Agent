from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, EmailRecord
from imap_service import fetch_unread_emails
from smtp_service import send_email
from ai_service import process_email_with_ai

app = FastAPI(title="Email Triage API")

# Add CORS so the React frontend can communicate with this API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/emails")
def get_emails(db: Session = Depends(get_db)):
    emails = db.query(EmailRecord).order_by(EmailRecord.id.desc()).all()
    return {"status": "success", "data": emails}

#  THE MASTER PIPELINE 

@app.get("/api/process-emails")
def process_inbox(db: Session = Depends(get_db)):
    # 1. Fetch unread emails
    fetch_result = fetch_unread_emails()
    if fetch_result.get("status") == "error":
        return fetch_result
        
    #  Query all emails that haven't been analyzed by AI yet
    
    unprocessed_emails = db.query(EmailRecord).filter(
        (EmailRecord.priority == "Unassigned") | (EmailRecord.priority.is_(None))
    ).all()
    
    processed_count = 0
    for email in unprocessed_emails:

        #  Pass content to the local AI model (Qwen)

        ai_raw = process_email_with_ai(email.content)
        
        ai_result = {k.lower(): v for k, v in ai_raw.items()}
        
        email.priority = ai_result.get("priority", "Unassigned")
        email.sentiment = ai_result.get("sentiment", "Neutral")
        email.draft_reply_1 = ai_result.get("draft_reply_1", "")
        email.draft_reply_2 = ai_result.get("draft_reply_2", "")
        email.draft_reply_3 = ai_result.get("draft_reply_3", "")
        
        #  Routing Decision based on priority

        if email.priority == "Low":
            send_result = send_email(
                to_address=email.sender, 
                subject=f"Re: {email.subject}", 
                body=email.draft_reply_1
            )
            if send_result.get("status") == "success":
                email.status = "Auto-Sent"
                email.final_reply = email.draft_reply_1
            else:
                email.status = "Failed to Send"
        else:
            email.status = "Pending"
            
        # Save changes to the database

        db.commit()
        processed_count += 1
        
    return {
        "status": "success", 
        "fetched": fetch_result.get("fetched", 0), 
        "processed_by_ai": processed_count
    }

# HUMAN IN THE LOOP APPROVAL 

@app.post("/api/emails/{email_id}/approve")
async def approve_email(email_id: int, request: Request, db: Session = Depends(get_db)):
    email = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
    if not email:
        return {"status": "error", "message": "Email not found"}
        
    body = await request.json()
    final_text = body.get("final_reply", email.draft_reply_1)
    
    send_result = send_email(
        to_address=email.sender, 
        subject=f"Re: {email.subject}", 
        body=final_text
    )
    
    if send_result.get("status") == "success":
        email.status = "Approved & Sent"
        email.final_reply = final_text
        db.commit()
        return {"status": "success", "message": "Email approved and sent!"}
    
    return send_result