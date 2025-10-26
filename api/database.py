import json
import os
from typing import List, Optional
from datetime import datetime
import uuid
from api.schemas import Task

class TaskDatabase:
    def __init__(self, db_file: str = "tasks.json"):
        self.db_file = db_file
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task) for task in data]
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def create_task(
        self,
        title: str,
        username: str,  # ADD USERNAME
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None
    ) -> Task:
        """Create a new task for a specific user"""
        task_id = str(uuid.uuid4())
        priority_clean = priority.lower()
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority_clean,
            status="todo",
            due_date=due_date,
            category=category,
            tags=tags,
            embedding=embedding,
            username=username  # ADD USERNAME
        )
        self.tasks.append(task)
        self.save_tasks()
        return task

    def get_task(self, task_id: str, username: str) -> Optional[Task]:
        """Get a task by ID for a specific user"""
        for task in self.tasks:
            if task.id == task_id and task.username == username:
                return task
        return None

    def get_all_tasks(self, username: str) -> List[Task]:
        """Get all tasks for a specific user"""
        return [task for task in self.tasks if task.username == username]

    def update_task(
        self,
        task_id: str,
        username: str,  # ADD USERNAME
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Task]:
        """Update an existing task for a specific user"""
        task = self.get_task(task_id, username)
        if not task:
            return None

        if title:
            task.title = title
        if description:
            task.description = description
        if priority:
            task.priority = priority.lower()
        if status:
            task.status = status.lower() if '_' not in status else status
        if due_date:
            task.due_date = due_date
        if category:
            task.category = category
        if tags:
            task.tags = tags

        self.save_tasks()
        return task

    def delete_task(self, task_id: str, username: str) -> bool:
        """Delete a task for a specific user"""
        task = self.get_task(task_id, username)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False

    def search_tasks(
        self,
        username: str,  # ADD USERNAME
        query: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Task]:
        """Search tasks by filters for a specific user"""
        results = [task for task in self.tasks if task.username == username]

        if status:
            status_clean = status.lower()
            results = [t for t in results if t.status == status_clean]
        if priority:
            priority_clean = priority.lower()
            results = [t for t in results if t.priority == priority_clean and t.status != 'completed']
        if category:
            results = [t for t in results if t.category == category]
        if query:
            query_lower = query.lower()
            results = [
                t for t in results
                if query_lower in t.title.lower() or query_lower in t.description.lower()
            ]

        return results

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    def semantic_search(self, query_embedding: List[float], username: str, top_k: int = 5, threshold: float = 0.25) -> List[Task]:
        """Search tasks using vector similarity for a specific user"""
        user_tasks = [task for task in self.tasks if task.username == username]
        scored_tasks = []
        
        for task in user_tasks:
            if task.embedding:
                similarity = self.cosine_similarity(query_embedding, task.embedding)
                if similarity > threshold:
                    scored_tasks.append((task, similarity))
        
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        return [task for task, score in scored_tasks[:top_k]]

# Global database instance
db = TaskDatabase()
