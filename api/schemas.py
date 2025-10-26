from typing import Optional, List
from datetime import datetime

class Task:
    def __init__(
        self,
        id: str,
        title: str,
        username: str,  # ADD THIS
        description: Optional[str] = None,
        priority: str = "medium",
        status: str = "todo",
        due_date: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ):
        self.id = id
        self.title = title
        self.username = username  # ADD THIS
        self.description = description or ""
        
        if isinstance(priority, str):
            self.priority = priority
        else:
            self.priority = priority.value if hasattr(priority, 'value') else str(priority)
        
        if isinstance(status, str):
            self.status = status
        else:
            self.status = status.value if hasattr(status, 'value') else str(status)
            
        self.due_date = due_date
        self.category = category
        self.tags = tags or []
        self.created_at = created_at or datetime.now().isoformat()
        self.embedding = embedding or []

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "username": self.username,  # ADD THIS
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date,
            "category": self.category,
            "tags": self.tags,
            "created_at": self.created_at,
            "embedding": self.embedding
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content
        }
