from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

# 1. Setup the SQLite database file
DATABASE_URL = "sqlite:///./emails.db"

# 2. Create the engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Define the Email Model (Schema)
class EmailRecord(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String)
    content = Column(Text)
    
    # AI Analysis Fields
    priority = Column(String, default="Unassigned")  # Low, Medium, High
    draft_reply = Column(Text, nullable=True)
    
    # State tracking
    final_reply = Column(Text, nullable=True)
    status = Column(String, default="Pending")       # Pending, Auto-Sent, Approved & Sent
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# 4. Create the tables in the database
Base.metadata.create_all(bind=engine)