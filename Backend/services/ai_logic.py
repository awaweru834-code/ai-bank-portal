import json
import os
from typing import Optional  # noqa: F401

from core import models
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

# 1. Load environment variables (this automatically pulls in HF_TOKEN for Hugging Face)
load_dotenv()

# 2. Lazy Loader for the Embedding Model
_embedding_model: SentenceTransformer | None = None

def get_embedding_model() -> SentenceTransformer:
    """Loads the model only on the first RAG request to keep startup instantaneous."""
    global _embedding_model
    if _embedding_model is None:
        # The library automatically uses the HF_TOKEN from your .env file
        _embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
            # NOTE: Uncomment the line below after the model downloads successfully once
            # local_files_only=True 
        )
    return _embedding_model

# 3. AI Logic Engine
def generate_ai_response(
    user_text: str, 
    account_id: int, 
    actual_balance: float, 
    db: Session,
    client,             # Injected Groq Client
    embedding_model,    # Injected SentenceTransformer (via get_embedding_model)
    index,              # Injected Pinecone Index
    agent_tools: list   # Injected Tool Definitions
):
    """Generator function that streams AI tokens and handles internal tool calls."""
    
    # Save new user message to DB
    db.add(models.ChatMessage(user_id=account_id, role="user", content=user_text))
    db.commit()

    # Fetch past memory (Stateless chat memory from PostgreSQL)
    past_messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.user_id == account_id)
        .order_by(models.ChatMessage.id.desc())
        .limit(5)
        .all()
    )
    past_messages.reverse()
    
    # Build the Memory Context
    user_history = []
    system_prompt = (
        f"You are an elite, secure AI Assistant for a bank. The current user's account_id is {account_id}. "
        "You have two tools at your disposal: get_balance and search_policy. "
        "If the user asks a question that requires a tool, use it silently. "
    )
    user_history.append({"role": "system", "content": system_prompt})
    
    for msg in past_messages:
        if msg.role in ["user", "assistant"]:
            user_history.append({"role": msg.role, "content": msg.content})

    # FIRST CALL: Enable Streaming via Groq/Llama 3
    response_stream = client.chat.completions.create(
        model="llama3-8b-8192", # Update to your specific Groq model string
        messages=user_history, 
        tools=agent_tools,
        stream=True 
    )

    final_text = ""
    is_tool_call = False
    tool_calls_data = {}

    # Catch the stream fragments
    for chunk in response_stream:
        delta = chunk.choices[0].delta

        if delta.content:
            final_text += delta.content
            yield delta.content 

        if delta.tool_calls:
            is_tool_call = True
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tool_calls_data:
                    tool_calls_data[idx] = {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": ""}
                    }
                if tc.function.arguments:
                    tool_calls_data[idx]["function"]["arguments"] += tc.function.arguments

    # TOOL EXECUTION ENGINE
    if is_tool_call:
        formatted_tool_calls = [tool_calls_data[i] for i in sorted(tool_calls_data.keys())]
        user_history.append({"role": "assistant", "tool_calls": formatted_tool_calls})

        for tc in formatted_tool_calls:
            try:
                arguments = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                arguments = {}
                
            tool_name = tc["function"]["name"]
            result_content = ""
            
            if tool_name == "get_balance":
                target_id = arguments.get("account_id")
                if target_id != account_id:
                    result_content = "SECURITY ALERT: You are not authorized."
                else:
                    result_content = f"Secure data accessed: Balance is ${actual_balance}"
            
            elif tool_name == "search_policy":
                query = arguments.get("search_query", "")
                try:
                    # Uses the injected model safely
                    vector = embedding_model.encode(query).tolist()
                    search_results = index.query(vector=vector, top_k=3, include_metadata=True)
                    context_chunks = [match["metadata"]["text"] for match in search_results["matches"]]
                    result_content = "POLICY FOUND:\n" + "\n\n".join(context_chunks) if context_chunks else "No policies found."
                except Exception as e:
                    result_content = f"Database error during policy search: {str(e)}"

            user_history.append({
                "role": "tool", 
                "tool_call_id": tc["id"], 
                "name": tool_name, 
                "content": result_content
            })
        
        # SECOND CALL: Synthesize the tool data
        final_response_stream = client.chat.completions.create(
            model="llama3-8b-8192", # Ensure this matches your first call
            messages=user_history,
            stream=True
        )
        
        for chunk in final_response_stream:
            token = chunk.choices[0].delta.content
            if token:
                final_text += token
                yield token 

    # Save the fully assembled string to the database
    db.add(models.ChatMessage(user_id=account_id, role="assistant", content=final_text))
    db.commit()