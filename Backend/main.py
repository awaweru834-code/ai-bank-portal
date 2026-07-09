from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.database import engine
from core import models
from core.rate_limiter import limiter

from routers import bank, ai_chat

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import get_db # Your database dependency

print("Booting up database engine...")
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise Smart Bank & AI API")
# Tell the browser these frontend URLs are safe
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://172.19.208.1:3000", # The specific WSL network IP from your logs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods like POST, GET, OPTIONS
    allow_headers=["*"], # Allows all headers
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(bank.router)
app.include_router(ai_chat.router)

@app.get("/")
def health_check():
    return {"status": "All systems operational. Welcome to the Smart Bank."}
@app.get("/wake-up", tags=["System"])
def wake_up_services(db: Session = Depends(get_db)):
    """
    A lightweight Warm-Up Ping to eliminate Serverless Cold Starts.
    This forces PostgreSQL (Neon) to spin up its compute instance.
    """
    try:
        # Execute a practically invisible, zero-cost SQL command
        db.execute(text("SELECT 1"))
        
        return {
            "status": "awake", 
            "message": "PostgreSQL engine is warm and ready."
        }
    except Exception as e:
        # Print the exact error to the terminal so YOU can debug it
        print(f"⚠️ Wake-up ping failed: {e}") 
        
        # Throw the clean 503 error for the USER
        raise HTTPException(
            status_code=503, 
            detail="Services are currently waking up or unavailable."
        )
    