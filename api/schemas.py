from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Task(BaseModel):
    id: str
    username: str
    title: str
    description: Optional[str] = ""
    priority: str = "medium"
    status: str = "todo"
    due_date: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    embedding: Optional[List[float]] = None
    created_at: str
    updated_at: str

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date,
            "category": self.category,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Optional[str] = "medium"
    due_date: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    category: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

    def __init__(self, role: str, content: str):
        super().__init__(role=role, content=content)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class ConversationState(BaseModel):
    """Track multi-turn conversations for task creation"""
    mode: str = "normal"  # "normal", "awaiting_date", "awaiting_priority"
    pending_task: Optional[dict] = None
    original_query: Optional[str] = None
