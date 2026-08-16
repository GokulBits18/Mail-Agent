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
    allow_origins=["*"],  # Allows all origins for local development
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

# --- THE MASTER PIPELINE ---
@app.get("/api/process-emails")
def process_inbox(db: Session = Depends(get_db)):
    # 1. Fetch unread emails
    fetch_result = fetch_unread_emails()
    if fetch_result.get("status") == "error":
        return fetch_result
        
    # 2. Query all emails that haven't been analyzed by AI yet
    unprocessed_emails = db.query(EmailRecord).filter(EmailRecord.priority == "Unassigned").all()
    
    processed_count = 0
    for email in unprocessed_emails:
        # 3. Pass content to the local Llama model
        ai_result = process_email_with_ai(email.content)
        
        email.priority = ai_result.get("priority", "Medium")
        email.draft_reply = ai_result.get("draft_reply", "")
        
        # 4. Routing Decision based on priority
        if email.priority == "Low":
            # Auto-send for Low priority
            send_result = send_email(
                to_address=email.sender, 
                subject=f"Re: {email.subject}", 
                body=email.draft_reply
            )
            if send_result.get("status") == "success":
                email.status = "Auto-Sent"
                email.final_reply = email.draft_reply
            else:
                email.status = "Failed to Send"
        else:
            # Hold Medium/High for human review
            email.status = "Pending"
            
        # Save changes to the database
        db.commit()
        processed_count += 1
        
    return {
        "status": "success", 
        "fetched": fetch_result.get("fetched", 0), 
        "processed_by_ai": processed_count
    }

# --- HUMAN IN THE LOOP APPROVAL ---
@app.post("/api/emails/{email_id}/approve")
async def approve_email(email_id: int, request: Request, db: Session = Depends(get_db)):
    email = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
    if not email:
        return {"status": "error", "message": "Email not found"}
        
    # Get the (potentially edited) text from the frontend
    body = await request.json()
    final_text = body.get("final_reply", email.draft_reply)
    
    # Send the approved email via SMTP
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