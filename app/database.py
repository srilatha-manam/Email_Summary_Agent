from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your PostgreSQL connection string
DATABASE_URL = "postgres://postgres:root@localhost:5432"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Email(Base):
    __tablename__ = "emailagent"
    id = Column(String, primary_key=True)
    subject = Column(String)
    snippet = Column(String)
    summary = Column(String)

Base.metadata.create_all(bind=engine)

def save_email(db, email_id, subject, snippet, summary):
    email = Email(id=email_id, subject=subject, snippet=snippet, summary=summary)
    db.merge(email)  # Updates if exists, inserts if not
    db.commit()
