import logging
from fastapi import FastAPI, HTTPException
from app.gmail_client import fetch_emails
from app.prioritizer import prioritize_email
from app.summarizer import summarizer
from app.database import init_db, save_email, get_all_emails
from app.memory import add_to_memory, get_memory
from rich.console import Console

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('app.log')  # Logs to a file
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()
console = Console()

# Initialize database with exception handling
try:
    db_session = init_db()
    logger.info("FastAPI application started and database session initialized")
except RuntimeError as e:
    logger.error(f"Failed to initialize database session: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))

@app.get("/check-emails")
def check_emails():
    """Fetch, prioritize, summarize, and store emails, notifying via CLI."""
    try:
        logger.info("Starting /check-emails endpoint")
        emails = fetch_emails(max_results=10)
        important_emails = []
        
        for email in emails:
            try:
                priority = prioritize_email(email['subject'], email['body'])
                if priority >= 6:  # Threshold for "important"
                    summary = summarizer.summarize(email['body'])
                    save_email(db_session, email['id'], email['subject'], email['body'], priority, summary)
                    add_to_memory(email['id'], email['subject'], priority, summary)
                    important_emails.append({
                        "id": email['id'], "subject": email['subject'], "priority": priority, "summary": summary
                    })
                    logger.debug(f"Processed important email ID={email['id']}, Subject={email['subject']}")
            except ValueError as e:
                logger.error(f"ValueError processing email ID={email['id']}: {str(e)}")
                continue  # Skip this email and continue
            except RuntimeError as e:
                logger.error(f"RuntimeError processing email ID={email['id']}: {str(e)}")
                continue  # Skip this email and continue
            except Exception as e:
                logger.error(f"Unexpected error processing email ID={email['id']}: {str(e)}")
                continue  # Skip this email and continue
        
        # CLI output (optional, since n8n will handle notifications)
        for email in important_emails:
            color = "red" if email['priority'] >= 10 else "yellow" if email['priority'] >= 8 else "green"
            console.print(f"[{color}]{email['subject']} (Priority: {email['priority']})[/]: {email['summary']}")
        
        logger.info(f"Completed /check-emails: Found {len(important_emails)} important emails")
        return {"important_emails": important_emails, "memory": get_memory()}
    
    except ValueError as e:
        logger.error(f"ValueError in /check-emails: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"RuntimeError in /check-emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /check-emails: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/email-history")
def email_history():
    """Retrieve all stored emails and memory history."""
    try:
        logger.info("Starting /email-history endpoint")
        emails = get_all_emails(db_session)
        memory = get_memory()
        logger.info(f"Completed /email-history: Retrieved {len(emails)} emails")
        return {"emails": emails, "memory": memory}
    
    except ValueError as e:
        logger.error(f"ValueError in /email-history: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"RuntimeError in /email-history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /email-history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=8000)