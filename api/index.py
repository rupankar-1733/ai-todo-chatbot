from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from api.agent import agent
from api.database import db
from api.auth import auth_service

app = FastAPI(title="AI Todo Chatbot API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://ai-todo-chatbot-1.vercel.app",
                   "https://rupankar-1733-ai-todo-chatbot.hf.space",
                   "*" ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class TaskResponse(BaseModel):
    tasks: List[dict]
    count: int

# Dependency to get current user from token
def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Verify token and get current user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = auth_service.verify_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Todo Chatbot API is running!",
        "version": "2.1.0",
        "status": "healthy",
        "features": ["authentication", "chat", "tasks", "RAG", "user-isolation", "PATCH-support"]
    }

# ========== AUTH ENDPOINTS ==========
@app.post("/api/signup")
async def signup(request: SignupRequest):
    """Register a new user"""
    try:
        result = auth_service.create_user(
            request.username,
            request.email,
            request.password
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {"message": result["message"]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

@app.post("/api/login")
async def login(request: LoginRequest):
    """Login and get JWT token"""
    try:
        token = auth_service.authenticate_user(request.username, request.password)
        
        if not token:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        return {
            "token": token,
            "username": request.username,
            "message": "Login successful"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@app.get("/api/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    """Verify if token is valid"""
    return {
        "username": user["username"],
        "email": user["email"],
        "valid": True
    }

# ========== PROTECTED CHAT ENDPOINTS ==========
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    """
    Main chat endpoint where users send messages (Protected)
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # SET USERNAME FOR THIS SESSION - USER ISOLATION
        agent.set_username(user["username"])
        response = agent.chat(request.message)
        
        return ChatResponse(response=response)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat error for user {user['username']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/api/chat/clear")
async def clear_conversation(user: dict = Depends(get_current_user)):
    """Clear the conversation history (Protected)"""
    try:
        agent.conversation_history = []
        return {"message": "Conversation history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")

@app.get("/api/chat/history")
async def get_conversation_history(user: dict = Depends(get_current_user)):
    """Get the conversation history (Protected)"""
    try:
        return {
            "history": [msg.to_dict() for msg in agent.conversation_history],
            "count": len(agent.conversation_history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

# ========== PROTECTED TASK ENDPOINTS ==========
@app.get("/api/tasks", response_model=TaskResponse)
async def get_tasks(
    user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all tasks with optional filters (Protected) - USER ISOLATED"""
    try:
        tasks = db.search_tasks(
            username=user["username"],  # USER-SPECIFIC ISOLATION
            status=status,
            priority=priority,
            category=category
        )
        
        return TaskResponse(
            tasks=[task.to_dict() for task in tasks],
            count=len(tasks)
        )
    
    except Exception as e:
        print(f"❌ Get tasks error for user {user['username']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str, user: dict = Depends(get_current_user)):
    """Get a specific task by ID (Protected) - USER ISOLATED"""
    try:
        task = db.get_task(task_id, user["username"])  # USER-SPECIFIC
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get task error for user {user['username']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching task: {str(e)}")

@app.patch("/api/tasks/{task_id}")
async def update_task_endpoint(
    task_id: str,
    update_data: dict,
    user: dict = Depends(get_current_user)
):
    """Update a specific task (Protected) - USER ISOLATED"""
    try:
        print(f"🔄 PATCH /api/tasks/{task_id} - User: {user['username']}")
        print(f"📝 Update data: {update_data}")
        
        updated_task = db.update_task(
            task_id=task_id,
            username=user["username"],
            title=update_data.get("title"),
            description=update_data.get("description"),
            priority=update_data.get("priority"),
            status=update_data.get("status"),
            due_date=update_data.get("due_date"),
            category=update_data.get("category")
        )
        
        if not updated_task:
            print(f"❌ Task {task_id} not found for user {user['username']}")
            raise HTTPException(status_code=404, detail="Task not found or you don't have permission")
        
        print(f"✅ Task updated successfully! New status: {updated_task.status}")
        return {
            "success": True,
            "message": "Task updated successfully",
            "task": updated_task.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Update task error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, user: dict = Depends(get_current_user)):
    """Delete a specific task (Protected) - USER ISOLATED"""
    try:
        success = db.delete_task(task_id, user["username"])  # USER-SPECIFIC
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Delete task error for user {user['username']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

# For Vercel serverless function
handler = app
