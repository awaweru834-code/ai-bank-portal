from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from core.database import Base # We import the master blueprint we made yesterday!
from sqlalchemy.sql import func

# 1. We build our Class, but we inherit from the SQLAlchemy 'Base'
class UserDB(Base):
    
    # 2. We name the actual table in the SQL database
    __tablename__ = "users"
    
    # 3. We define the columns (Just like an Excel sheet!)
    
    # primary_key=True means this is the unique ID number (like a social security number)
    # index=True makes it super fast for the database to search for this ID
    id = Column(Integer, primary_key=True, index=True)
    
    # We define a String column for their name. unique=True means no two users can have the same name!
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # We define a Float (decimal number) column for their money
    balance = Column(Float, default=0.0)
class ChatMessage(Base):  # <--- Changed to match ai_logic.py
    __tablename__ = "chat_messages"  # <--- Standard SQL naming convention
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) 
    agent_type = Column(String) 
    role = Column(String)       
    content = Column(Text)    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())