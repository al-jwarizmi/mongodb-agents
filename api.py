from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import uuid
from main import CustomerSupportSystem
from config.logging_config import setup_logging

# Initialize logging
setup_logging()

app = FastAPI(
    title="Frodo - Mattress Expert API",
    description="API for the Frodo multi-agent customer support system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the customer support system
support_system = CustomerSupportSystem()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Send a message to the chat system using HTTP."""
    try:
        session_id = message.session_id or str(uuid.uuid4())
        response = await support_system.process_query(message.message, session_id)
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """Chat with the system using WebSocket for real-time communication."""
    try:
        await websocket.accept()
        active_connections[session_id] = websocket
        
        # Send welcome message
        await websocket.send_json({
            "type": "assistant",
            "content": "Welcome to Sleep Better! I'm Frodo, your personal sleep consultant. How may I assist you today?"
        })
        
        while True:
            try:
                # Receive message
                message = await websocket.receive_text()
                
                # Send typing indicator
                await websocket.send_json({
                    "type": "status",
                    "content": "typing"
                })
                
                # Process message
                response = await support_system.process_query(message, session_id)
                
                # Send response
                await websocket.send_json({
                    "type": "assistant",
                    "content": response
                })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": str(e)
                })
                
    finally:
        if session_id in active_connections:
            del active_connections[session_id]

@app.post("/chat/{session_id}/clear")
async def clear_chat(session_id: str):
    """Clear the chat history for a session."""
    support_system.clear_conversation(session_id)
    
    # Send welcome message
    welcome_message = "Welcome to Sleep Better! I'm Frodo, your personal sleep consultant. How may I assist you today?"
    
    # If there's an active WebSocket connection, send the welcome message through it
    if session_id in active_connections:
        await active_connections[session_id].send_json({
            "type": "assistant",
            "content": welcome_message
        })
    
    return {
        "status": "success",
        "message": "Chat history cleared",
        "welcome_message": welcome_message
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 