from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

#  Setup the SQLite database file

DATABASE_URL = "sqlite:///./emails.db"

#  Create the engine and session

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Email Model (Schema)

class EmailRecord(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String)
    content = Column(Text)
    priority = Column(String)
    
    #  COLUMNS ADDED HERE 
    sentiment = Column(String, default="Neutral")
    draft_reply_1 = Column(Text, nullable=True) # Positive/Accept
    draft_reply_2 = Column(Text, nullable=True) # Decline
    draft_reply_3 = Column(Text, nullable=True) # Ask Details
    
    
    final_reply = Column(Text, nullable=True)
    status = Column(String, default="Pending")

    
# Create the tables in the database

Base.metadata.create_all(bind=engine)