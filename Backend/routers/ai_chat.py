from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from core import auth
from core.database import get_db
from services.ai_logic import generate_ai_response

router = APIRouter(tags=["AI Assistant"])

@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    # 1. Accept the incoming WebSocket handshake
    await websocket.accept()
    
    # 2. Extract the token directly from the HttpOnly cookie
    token = websocket.cookies.get("access_token")
    
    if not token:
        await websocket.send_text("UNAUTHORIZED: Missing secure cookie")
        await websocket.close(code=1008)
        return

    # 3. Authenticate the User
    try:
        current_user = auth.get_current_user(token=token, db=db)
    except HTTPException:
        await websocket.send_text("SESSION_EXPIRED")
        await websocket.close(code=1008)
        return

    # 4. Continuous Communication Loop
    try:
        while True:
            user_text = await websocket.receive_text()
            
            try:
                # 5. Delegate all AI, tools, and vector search to the service layer
                reply_generator = generate_ai_response(
                    user_text=user_text,
                    account_id=current_user.id,
                    actual_balance=current_user.balance,
                    db=db
                )
                
                # 6. Stream tokens directly to React over the socket
                for word in reply_generator:
                    await websocket.send_text(word)
                    
                # 7. Notify the frontend that generation has completed
                await websocket.send_text("[DONE]")
                
            except Exception as e:
                await websocket.send_text(f"\n❌ Error processing request: {str(e)}")
                await websocket.send_text("[DONE]")

    except WebSocketDisconnect:
        # Failsafe logging for when the user navigates away from the tab
        user_id = getattr(current_user, 'id', 'anonymous')
        print(f"User {user_id} disconnected from chat session.")