import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Grab the URL from the environment
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

# Create the Cloud Engine
# Notice we removed connect_args={"check_same_thread": False}! That was only for SQLite.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()