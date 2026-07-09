from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Import from your core and services folders
from core.database import get_db
from core import models
from core import auth
from core.rate_limiter import limiter
from services.ai_logic import generate_bank_response, generate_rag_response

# Create the dedicated AI doorway
router = APIRouter(tags=["AI Assistant"])

# ==========================================
# BOUNCERS (Pydantic Schemas)
# ==========================================
class ChatRequest(BaseModel):
    user_text: str

class RAGRequest(BaseModel):
    user_question: str

# ==========================================
# DOORWAYS (Endpoints)
# ==========================================

# DOORWAY 1: The Smart AI Chat (Locked with Auth)
@router.post("/bank-chat")
@limiter.limit("10/minute")
async def smart_bank_chat(request: Request, incoming_data: ChatRequest, username: str = Depends(auth.verify_token), db: Session = Depends(get_db)):
    
    # 1. Verify user in database
    verified_user = db.query(models.UserDB).filter(models.UserDB.username == username).first()
    if not verified_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    # 2. Pass the data to the isolated AI Brain!
    answer = generate_bank_response(
        user_text=incoming_data.user_text, 
        account_id=verified_user.id, 
        actual_balance=verified_user.balance,
        db=db
    )
    
    # 3. Return the AI's answer
    return {"ai_reply": answer}

# DOORWAY 2: Chat with the PDF (RAG) (Locked with Auth)
@router.post("/ask-pdf")
@limiter.limit("10/minute")
def ask_pdf_endpoint(request: Request, incoming_data: RAGRequest, username: str = Depends(auth.verify_token), db: Session = Depends(get_db)):
    
    # 1. Verify user in database
    verified_user = db.query(models.UserDB).filter(models.UserDB.username == username).first()
    if not verified_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        # Pass the question, the user's ID, and the database session to the brain!
        answer = generate_rag_response(
            user_question=incoming_data.user_question,
            account_id=verified_user.id,
            db=db
        )
        return {"ai_reply": answer}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"The AI Brain is temporarily unavailable. Error: {str(e)}"
        )