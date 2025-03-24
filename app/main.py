from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.gmail_client import fetch_emails
from app.summarizer import summarizer
from app.memory import add_to_memory, get_memory
from app.database import SessionLocal, save_email

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/fetch-and-summarize")
def fetch_and_summarize_emails(db: Session = Depends(get_db)):
    emails = fetch_emails(max_results=5)
    results = []
    
    for email in emails:
        summary = summarizer.summarize(email['snippet'])
        save_email(db, email['id'], email['subject'], email['snippet'], summary)
        add_to_memory(email['id'], email['subject'], summary)
        results.append({
            "id": email['id'],
            "subject": email['subject'],
            "snippet": email['snippet'],
            "summary": summary
        })
    
    return {"emails": results, "memory": get_memory()}

@app.get("/history")
def get_history():
    return {"chat_history": get_memory()}
