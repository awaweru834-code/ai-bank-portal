import json
import os
from typing import Optional
from sqlalchemy.orm import Session
from groq import Groq
from sentence_transformers import SentenceTransformer

from core import models

# 1. Initialize the Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Lazy Loader for Local Embeddings (Saves your 512MB RAM)
_embedding_model: Optional[SentenceTransformer] = None

def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Check the user's secure bank balance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "integer", "description": "The user's account ID number."}
                },
                "required": ["account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "Search the company policy database to answer questions about rules, procedures, or HR.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {"type": "string", "description": "The specific keyword to search for."}
                },
                "required": ["search_query"]
            }
        }
    }
]

def process_chat_message(user_text: str, current_user, db: Session, pinecone_index) -> str:
    account_id = current_user.id
    
    # Save new user message to PostgreSQL
    db.add(models.ChatMessage(user_id=account_id, role="user", content=user_text))
    db.commit()

    # Fetch past memory (Limit to 10 for context)
    past_messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.user_id == account_id)
        .order_by(models.ChatMessage.id.desc())
        .limit(10)
        .all()
    )
    past_messages.reverse()
    
    # Build the Memory Context for Groq
    user_history = []
    
    system_prompt = (
        f"You are an elite, secure AI Assistant for a bank named Hank. The current user's account_id is {account_id}. "
        "You have two tools at your disposal: get_balance and search_policy. "
        "Use your own intelligence for general greetings, but use tools for specific banking queries."
    )
    user_history.append({"role": "system", "content": system_prompt})
    
    for msg in past_messages:
        if msg.role in ["user", "assistant", "tool"]:
            user_history.append({"role": msg.role, "content": msg.content})

    # FIRST CALL: Trigger Groq Generation with the active model
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=user_history,
        tools=AGENT_TOOLS
    )

    message = response.choices[0].message
    final_text = ""

    # TOOL EXECUTION ENGINE
    if message.tool_calls:
        # Append the assistant's tool call message to history
        user_history.append(message)
        
        for tc in message.tool_calls:
            try:
                arguments = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                arguments = {}
                
            tool_name = tc.function.name
            result_content = ""
            
            if tool_name == "get_balance":
                target_id = arguments.get("account_id")
                if target_id != account_id:
                    result_content = "SECURITY ALERT: You are not authorized."
                else:
                    result_content = f"Secure data accessed: Balance is ${current_user.balance}"
            
            elif tool_name == "search_policy":
                query = arguments.get("search_query", "")
                try:
                    # THE HYBRID FIX: Local CPU for embeddings, Groq for reasoning
                    model = get_embedding_model()
                    vector = model.encode(query).tolist()
                    
                    search_results = pinecone_index.query(vector=vector, top_k=3, include_metadata=True)
                    context_chunks = [match["metadata"]["text"] for match in search_results["matches"]]
                    result_content = "POLICY FOUND:\n" + "\n\n".join(context_chunks) if context_chunks else "No policies found."
                except Exception as e:
                    result_content = f"Database error during policy search: {str(e)}"

            user_history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tool_name,
                "content": result_content
            })
            
        # SECOND CALL: Synthesize the tool data via Groq
        final_response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=user_history,
            tools=AGENT_TOOLS
              # <-- ADD THIS LINE
        )
        final_text = final_response.choices[0].message.content
    else:
        final_text = message.content

    # Save the final AI response to the database
    db.add(models.ChatMessage(user_id=account_id, role="assistant", content=final_text))
    db.commit()

    # ENFORCE MEMORY LIMIT: Keep only the most recent 10 messages
    kept_message_ids = (
        db.query(models.ChatMessage.id)
        .filter(models.ChatMessage.user_id == account_id)
        .order_by(models.ChatMessage.id.desc())
        .limit(10)
        .all()
    )
    
    if kept_message_ids:
        oldest_kept_id = kept_message_ids[-1][0]
        db.query(models.ChatMessage).filter(
            models.ChatMessage.user_id == account_id, 
            models.ChatMessage.id < oldest_kept_id
        ).delete()
        db.commit()

    return final_text