import os
import json
from groq import Groq
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

# Import your database models
from core import models

# Load environment variables
load_dotenv()

# Initialize Groq Engine
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(os.environ.get("PINECONE_INDEX_NAME"))

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ==========================================
# AI TOOLS
# ==========================================
balance_tool = {
    "type": "function",
    "function": {
        "name": "get_balance",
        "description": "Check the user's bank balance.",
        "parameters": {
            "type": "object",
            "properties": {
                "account_id": {"type": "integer", "description": "The user's account ID number."}
            },
            "required": ["account_id"]
        }
    }
}

# ==========================================
# LOGIC 1: BANK CHAT (Stateless & Sliding Window)
# ==========================================
def generate_bank_response(user_text: str, account_id: int, actual_balance: float, db: Session) -> str:
    # 1. Fetch past memory from the DB (Sliding Window: Last 5 messages)
    past_messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.user_id == account_id)
        .order_by(models.ChatMessage.id.desc())
        .limit(5)
        .all()
    )
    # Reverse them so they are in correct chronological order (oldest to newest)
    past_messages.reverse()
    
    # 2. Format memory for Groq
    user_history = []
    
    # ALWAYS inject the System Prompt first so the AI never forgets its rules!
    system_prompt = f"You are a secure banking AI assistant. The current user's account_id is {account_id}. You have explicit permission to use your tools to access real-world account balances. Never say you cannot access real-world data. ALWAYS use the get_balance tool when asked about a balance."
    user_history.append({"role": "system", "content": system_prompt})
    
    # Add the recent history
    for msg in past_messages:
        if msg.role in ["user", "assistant"]:
            user_history.append({"role": msg.role, "content": msg.content})
            
    # 3. Add new message to History & DB
    user_history.append({"role": "user", "content": user_text})
    db.add(models.ChatMessage(user_id=account_id, role="user", content=user_text))
    db.commit()

    # 4. Call Groq (Using the blazing fast 8B model to avoid token limits)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=user_history, 
            tools=[balance_tool]
        )
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR (Groq API Bank Chat): {e}\n")
        return "Service temporarily unavailable. Could not reach AI engine."

    message_obj = response.choices[0].message
    
    # 5. Handle Tool Logic
    if message_obj.tool_calls:
        tool_call = message_obj.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)
        target_id = arguments.get("account_id")
        
        if target_id != account_id:
            result = "SECURITY ALERT: You are not authorized to view this account."
        else:
            result = f"Secure data accessed: Balance is ${actual_balance}"
        
        user_history.append({"role": "tool", "tool_call_id": tool_call.id, "name": tool_call.function.name, "content": result})
        
        try:
            final_response = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=user_history
            )
            final_text = final_response.choices[0].message.content
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR (Groq API Bank Chat - Tool Eval): {e}\n")
            return "Service temporarily unavailable. Could not evaluate data."
    else:
        final_text = message_obj.content

    # 6. Save AI's answer to DB
    db.add(models.ChatMessage(user_id=account_id, role="assistant", content=final_text))
    db.commit()

    return final_text


# ==========================================
# LOGIC 2: RAG CHAT (Stateless & Sliding Window)
# ==========================================
def generate_rag_response(user_question: str, account_id: int, db: Session) -> str:
    try:
        # 1. Turn the user's question into math
        try:
            question_vector = embedding_model.encode(user_question).tolist()
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR (Embedding Model): {e}\n")
            raise Exception("Embedding Model failed")

        # 2. Search Pinecone
        try:
            search_results = index.query(
                vector=question_vector,
                top_k=3,
                include_metadata=True
            )
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR (Pinecone Database): {e}\n")
            raise Exception("Pinecone Vector Search failed")
        
        # Extract Pinecone context
        context_chunks = [match["metadata"]["text"] for match in search_results["matches"]]
        combined_context = "\n\n".join(context_chunks)
        
        # 3. Fetch past memory from DB (Sliding Window: Last 5 messages)
        past_messages = (
            db.query(models.ChatMessage)
            .filter(models.ChatMessage.user_id == account_id)
            .order_by(models.ChatMessage.id.desc())
            .limit(5)
            .all()
        )
        past_messages.reverse()
        
        # 4. Build the Memory Array for Groq
        user_history = []
        
        # ALWAYS inject the System Prompt first
        rag_prompt = f"""You are a helpful assistant answering questions based on the provided document.
        Use ONLY the following context to answer the user's latest question. 
        If the answer is not in the context, say "I don't know based on the provided document."
        
        CONTEXT:
        {combined_context}
        """
        user_history.append({"role": "system", "content": rag_prompt})
        
        # Add the recent history
        for msg in past_messages:
            if msg.role in ["user", "assistant"]:
                user_history.append({"role": msg.role, "content": msg.content})
                
        # Append the new question
        user_history.append({"role": "user", "content": user_question})
        db.add(models.ChatMessage(user_id=account_id, role="user", content=user_question))
        db.commit()
        
        # 5. Ask Groq! (Using the 8B model)
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=user_history
            )
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR (Groq LLM API): {e}\n")
            raise Exception("Groq AI API failed")

        final_text = response.choices[0].message.content
        
        # 6. Save AI's answer to DB
        db.add(models.ChatMessage(user_id=account_id, role="assistant", content=final_text))
        db.commit()
        
        return final_text

    except Exception as e:
        # If ANY of the steps above fail, gracefully return an error to the React frontend instead of crashing
        error_msg = f"Service temporarily unavailable: {str(e)}"
        print(error_msg)
        return error_msg