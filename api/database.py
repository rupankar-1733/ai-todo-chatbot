import json
import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from api.schemas import Task
from threading import Lock


class Database:
    """
    Enterprise-grade database with thread-safe operations
    Features: Write-through caching, automatic reload, thread safety
    """
    
    def __init__(self, tasks_file: str = "tasks.json"):
        self.tasks_file = tasks_file
        self.tasks: Dict[str, dict] = {}
        self._lock = Lock()  # Thread safety
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file with error handling"""
        with self._lock:
            if os.path.exists(self.tasks_file):
                try:
                    with open(self.tasks_file, 'r') as f:
                        self.tasks = json.load(f)
                    print(f"✅ Loaded {len(self.tasks)} tasks from {self.tasks_file}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    self.tasks = {}
                except Exception as e:
                    print(f"❌ Error loading tasks: {e}")
                    self.tasks = {}
            else:
                self.tasks = {}
                print(f"📝 No existing tasks file, starting fresh")
    
    def save_tasks(self):
        """Thread-safe save with atomic write"""
        with self._lock:
            try:
                # Write to temporary file first (atomic operation)
                temp_file = f"{self.tasks_file}.tmp"
                with open(temp_file, 'w') as f:
                    json.dump(self.tasks, f, indent=2)
                
                # Rename to actual file (atomic on POSIX systems)
                os.replace(temp_file, self.tasks_file)
                print(f"💾 Saved {len(self.tasks)} tasks to {self.tasks_file}")
            except Exception as e:
                print(f"❌ Error saving tasks: {e}")
                # Clean up temp file if exists
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    def create_task(
        self,
        title: str,
        username: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None
    ) -> Task:
        """Create a new task with timestamps"""
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        task_data = {
            "id": task_id,
            "username": username,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "todo",
            "due_date": due_date,
            "category": category,
            "tags": tags or [],
            "embedding": embedding,
            "created_at": now,
            "updated_at": now
        }
        
        with self._lock:
            self.tasks[task_id] = task_data
        
        self.save_tasks()  # Immediate write
        
        print(f"✅ Created task: {task_id} - '{title}' for user {username} (priority: {priority}, due: {due_date})")
        
        return Task(**task_data)
    
    def get_task(self, task_id: str, username: str) -> Optional[Task]:
        """Get a specific task by ID for a user"""
        self.load_tasks()  # Always reload for consistency
        task_data = self.tasks.get(task_id)
        if task_data and task_data.get("username") == username:
            return Task(**task_data)
        return None
    
    def get_all_tasks(self, username: str) -> List[Task]:
        """Get all tasks for a user"""
        self.load_tasks()  # Always reload for consistency
        user_tasks = [
            Task(**task_data) 
            for task_data in self.tasks.values() 
            if task_data.get("username") == username
        ]
        print(f"📋 Loaded {len(user_tasks)} tasks for user {username}")
        return user_tasks
    
    def update_task(
        self,
        task_id: str,
        username: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Task]:
        """Update a task"""
        self.load_tasks()  # Always reload
        task_data = self.tasks.get(task_id)
        
        if not task_data or task_data.get("username") != username:
            print(f"❌ Task {task_id} not found or wrong user")
            return None
        
        # Update fields
        if title is not None:
            task_data["title"] = title
        if description is not None:
            task_data["description"] = description
        if priority is not None:
            task_data["priority"] = priority
        if status is not None:
            task_data["status"] = status
        if due_date is not None:
            task_data["due_date"] = due_date
        if category is not None:
            task_data["category"] = category
        
        task_data["updated_at"] = datetime.now().isoformat()
        
        with self._lock:
            self.tasks[task_id] = task_data
        
        self.save_tasks()  # Immediate write
        
        print(f"✅ Updated task: {task_id} - status: {status}")
        
        return Task(**task_data)
    
    def delete_task(self, task_id: str, username: str) -> bool:
        """Delete a task"""
        self.load_tasks()  # Always reload
        task_data = self.tasks.get(task_id)
        
        if not task_data or task_data.get("username") != username:
            print(f"❌ Task {task_id} not found or wrong user")
            return False
        
        with self._lock:
            del self.tasks[task_id]
        
        self.save_tasks()  # Immediate write
        
        print(f"🗑️ Deleted task: {task_id}")
        return True
    
    def search_tasks(
        self,
        username: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Task]:
        """Search tasks with filters"""
        self.load_tasks()  # Always reload
        results = []
        
        for task_data in self.tasks.values():
            if task_data.get("username") != username:
                continue
            
            if status and task_data.get("status") != status:
                continue
            if priority and task_data.get("priority") != priority:
                continue
            if category and task_data.get("category") != category:
                continue
            
            results.append(Task(**task_data))
        
        print(f"🔍 Search found {len(results)} tasks for user {username}")
        return results
    
    def semantic_search(
        self,
        query_embedding: List[float],
        username: str,
        top_k: int = 10,
        threshold: float = 0.3
    ) -> List[Task]:
        """RAG: Semantic search using vector embeddings"""
        import numpy as np
        
        self.load_tasks()  # Always reload
        results = []
        
        for task_data in self.tasks.values():
            if task_data.get("username") != username:
                continue
            
            task_embedding = task_data.get("embedding")
            if not task_embedding:
                continue
            
            # Calculate cosine similarity
            try:
                similarity = np.dot(query_embedding, task_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(task_embedding)
                )
                
                if similarity >= threshold:
                    results.append((similarity, Task(**task_data)))
            except:
                pass
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x[0], reverse=True)
        return [task for _, task in results[:top_k]]
    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user from auth service (delegated to auth.py)"""
        from api.auth import auth_service
        return auth_service.users.get(username)


# Global database instance
db = Database()
