import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pinecone import Pinecone

from core import auth, models
from core.database import get_db
from services.ai_logic import process_chat_message

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

# 1. Initialize Pinecone here so the router can pass it to the AI service
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "hank-bank-policies"))

class ChatRequest(BaseModel):
    message: str

@router.get("/history")
def get_chat_history(
    current_user: models.UserDB = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the constrained chat history (up to 10 messages) for the frontend UI."""
    past_messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.user_id == current_user.id)
        .order_by(models.ChatMessage.id.desc())
        .limit(10)
        .all()
    )
    
    past_messages.reverse()
    return [{"role": msg.role, "content": msg.content} for msg in past_messages]


@router.post("/chat")
def send_chat_message(
    request: ChatRequest,
    current_user: models.UserDB = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Processes a user message via standard REST, invoking the AI tools."""
    
    # 2. Pass the missing pinecone_index argument into the logic engine
    ai_response_text = process_chat_message(
        user_text=request.message,
        current_user=current_user,
        db=db,
        pinecone_index=pinecone_index
    )
    
    return {"role": "assistant", "content": ai_response_text}