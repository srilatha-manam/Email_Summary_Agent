import logging
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('database.log')  # Logs to a file
    ]
)
logger = logging.getLogger(__name__)

# PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:root@localhost:5432/email_ai_agent"

# Create engine and session
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("Database engine and session factory initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database engine: {str(e)}")
    raise RuntimeError(f"Database initialization failed: {str(e)}")

# Define the Emails table
class Email(Base):
    __tablename__ = "emails"
    id = Column(String, primary_key=True)
    subject = Column(String)
    body = Column(String)
    priority = Column(Integer)
    summary = Column(String)

def init_db():
    """Initialize the database by creating tables if they don't exist."""
    try:
        Base.metadata.create_all(bind=engine)
        session = SessionLocal()
        logger.info("Database tables created successfully (if not already present)")
        return session
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during database initialization: {str(e)}")
        raise RuntimeError(f"Failed to initialize database: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise RuntimeError(f"Unexpected error initializing database: {str(e)}")

def save_email(session, email_id, subject, body, priority, summary):
    """Saves an email to the database. If the email_id already exists, it
    updates the existing record. If it doesn't exist, it inserts a new
    record. The record is then committed to the database."""
    try:
        email = Email(id=email_id, subject=subject, body=body, priority=priority, summary=summary)
        session.merge(email)  # Upserts: updates if exists, inserts if not
        session.commit()
        logger.info(f"Email saved successfully: ID={email_id}, Subject={subject}")
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error saving email ID={email_id}: {str(e)}")
        session.rollback()  # Roll back on error
        raise ValueError(f"Failed to save email ID={email_id}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error saving email ID={email_id}: {str(e)}")
        session.rollback()  # Roll back on error
        raise RuntimeError(f"Unexpected error saving email ID={email_id}: {str(e)}")

def get_all_emails(session):
    """Retrieve all emails from the database."""
    try:
        emails = session.query(Email).all()
        logger.info(f"Retrieved {len(emails)} emails from the database")
        return [{"id": e.id, "subject": e.subject, "body": e.body, "priority": e.priority, "summary": e.summary} for e in emails]
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error retrieving emails: {str(e)}")
        raise ValueError(f"Failed to retrieve emails: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error retrieving emails: {str(e)}")
        raise RuntimeError(f"Unexpected error retrieving emails: {str(e)}")