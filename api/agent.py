import os
from typing import List, Dict, Any
from groq import Groq
from sentence_transformers import SentenceTransformer
from api.database import db
from api.schemas import Task, ChatMessage
import json
import re

class TodoAgent:
    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY")
        
        print("Initializing Groq LLM...")
        self.client = Groq(api_key=groq_key)
        print("Groq initialized!")
        
        print("Loading embedding model for RAG...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("RAG embedding model loaded!")
        
        self.conversation_history: List[ChatMessage] = []
        self.current_username = None  # Current user
        
    def set_username(self, username: str):
        """Set the current username for this session"""
        self.current_username = username
        
    def get_system_prompt(self) -> str:
        return """You are TaskMate, a task management AI. You MUST ONLY respond with valid JSON for actions.

**CRITICAL RULES**:
1. NEVER invent or hallucinate tasks
2. ALWAYS use the provided functions
3. NEVER make up task data
4. ONLY return actual database results

When users request actions, respond with ONLY this JSON format:
{"function": "function_name", "parameters": {"param": "value"}}

**Available Functions**:

create_task - Create new task
Parameters: title (required), description, priority (low/medium/high/urgent), due_date (YYYY-MM-DD)

list_tasks - List/filter tasks
Parameters: status (todo/in_progress/completed), priority (low/medium/high/urgent), category

search_tasks - Semantic search using AI
Parameters: query (required) - natural language search

delete_task - Delete a task
Parameters: title (required) - task name or partial match

complete_task - Mark task as completed
Parameters: title (required) - task name or partial match

update_task - Update existing task
Parameters: title (required), new_title, description, priority, status

**Examples**:

User: "Show all tasks"
You: {"function": "list_tasks", "parameters": {}}

User: "Find tasks about work"
You: {"function": "search_tasks", "parameters": {"query": "work"}}

User: "Create urgent task call doctor"
You: {"function": "create_task", "parameters": {"title": "call doctor", "priority": "urgent"}}

User: "Delete milk task"
You: {"function": "delete_task", "parameters": {"title": "milk"}}

User: "Mark task done"
You: {"function": "complete_task", "parameters": {"title": "task"}}

User: "List high priority tasks"
You: {"function": "list_tasks", "parameters": {"priority": "high"}}

For casual conversation ONLY (greetings, thanks), respond normally. For ANY task-related query, use JSON functions."""

    def generate_embedding(self, text: str) -> List[float]:
        """RAG: Generate vector embeddings for semantic search"""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract function calls"""
        try:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
            if json_match:
                json_str = json_match.group(0)
                function_call = json.loads(json_str)
                if "function" in function_call:
                    return {"type": "function_call", "data": function_call}
        except:
            pass
        return {"type": "message", "data": response}

    def find_task_by_title(self, title_query: str) -> Task:
        """Find task by partial title match for current user"""
        all_tasks = db.get_all_tasks(self.current_username)
        title_lower = title_query.lower()
        
        # Exact match first
        for task in all_tasks:
            if task.title.lower() == title_lower:
                return task
        
        # Partial match
        for task in all_tasks:
            if title_lower in task.title.lower() or task.title.lower() in title_lower:
                return task
        
        return None

    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the requested function"""
        try:
            if function_name == "create_task":
                title = parameters.get("title")
                if not title:
                    return {"success": False, "error": "Title required"}
                
                description = parameters.get("description", "")
                embedding = self.generate_embedding(f"{title} {description}")
                
                task = db.create_task(
                    title=title,
                    username=self.current_username,  # USER-SPECIFIC
                    description=description,
                    priority=parameters.get("priority", "medium"),
                    due_date=parameters.get("due_date"),
                    category=parameters.get("category"),
                    tags=parameters.get("tags"),
                    embedding=embedding
                )
                return {
                    "success": True,
                    "message": f"✅ Created: '{task.title}' (Priority: {task.priority})",
                    "task": task.to_dict()
                }
            
            elif function_name == "list_tasks":
                tasks = db.search_tasks(
                    username=self.current_username,  # USER-SPECIFIC
                    status=parameters.get("status"),
                    priority=parameters.get("priority"),
                    category=parameters.get("category")
                )
                return {
                    "success": True,
                    "tasks": [task.to_dict() for task in tasks],
                    "count": len(tasks)
                }
            
            elif function_name == "search_tasks":
                query = parameters.get("query")
                if not query:
                    return {"success": False, "error": "Search query required"}
                
                # Expand medical/health related queries
                query_expanded = query
                medical_terms = ["medical", "health", "healthcare", "appointment"]
                if any(term in query.lower() for term in medical_terms):
                    query_expanded = query + " doctor dentist clinic hospital checkup"
                
                query_embedding = self.generate_embedding(query_expanded)
                tasks = db.semantic_search(
                    query_embedding, 
                    username=self.current_username,  # USER-SPECIFIC
                    top_k=10, 
                    threshold=0.25
                )
                
                return {
                    "success": True,
                    "tasks": [task.to_dict() for task in tasks],
                    "count": len(tasks),
                    "message": f"🔍 Found {len(tasks)} task(s) matching '{query}'"
                }
            
            elif function_name == "delete_task":
                title = parameters.get("title")
                if not title:
                    return {"success": False, "error": "Task title required"}
                
                task = self.find_task_by_title(title)
                if not task:
                    return {"success": False, "error": f"Task containing '{title}' not found"}
                
                success = db.delete_task(task.id, self.current_username)  # USER-SPECIFIC
                if success:
                    return {"success": True, "message": f"🗑️ Deleted: '{task.title}'"}
                return {"success": False, "error": "Failed to delete task"}
            
            elif function_name == "complete_task":
                title = parameters.get("title")
                if not title:
                    return {"success": False, "error": "Task title required"}
                
                task = self.find_task_by_title(title)
                if not task:
                    return {"success": False, "error": f"Task containing '{title}' not found"}
                
                updated_task = db.update_task(
                    task_id=task.id, 
                    username=self.current_username,  # USER-SPECIFIC
                    status="completed"
                )
                if updated_task:
                    return {
                        "success": True,
                        "message": f"✅ Completed: '{updated_task.title}'",
                        "task": updated_task.to_dict()
                    }
                return {"success": False, "error": "Failed to complete task"}
            
            elif function_name == "update_task":
                title = parameters.get("title")
                if not title:
                    return {"success": False, "error": "Task title required"}
                
                task = self.find_task_by_title(title)
                if not task:
                    return {"success": False, "error": f"Task containing '{title}' not found"}
                
                updated_task = db.update_task(
                    task_id=task.id,
                    username=self.current_username,  # USER-SPECIFIC
                    title=parameters.get("new_title"),
                    description=parameters.get("description"),
                    priority=parameters.get("priority"),
                    status=parameters.get("status"),
                    due_date=parameters.get("due_date"),
                    category=parameters.get("category")
                )
                
                if updated_task:
                    return {
                        "success": True,
                        "message": f"📝 Updated: '{updated_task.title}'",
                        "task": updated_task.to_dict()
                    }
                return {"success": False, "error": "Failed to update task"}
            
            else:
                return {"success": False, "error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def clear_old_context(self):
        """Keep only last 8 messages to prevent confusion and hallucinations"""
        if len(self.conversation_history) > 8:
            self.conversation_history = self.conversation_history[-8:]

    def chat(self, user_message: str) -> str:
        """Main chat interface"""
        if not self.current_username:
            return "Error: No user authenticated"
            
        self.clear_old_context()
        self.conversation_history.append(ChatMessage("user", user_message))
        
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        for msg in self.conversation_history[-6:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.3,
                max_tokens=400,
            )
            
            llm_response = completion.choices[0].message.content
            parsed = self.parse_llm_response(llm_response)
            
            if parsed["type"] == "function_call":
                function_data = parsed["data"]
                result = self.execute_function(
                    function_data.get("function"),
                    function_data.get("parameters", {})
                )
                
                if result.get("success"):
                    final_response = result.get("message", "Done!")
                    
                    if "tasks" in result:
                        tasks = result["tasks"]
                        if len(tasks) == 0:
                            final_response = "No tasks found matching your criteria."
                        else:
                            task_word = "task" if len(tasks) == 1 else "tasks"
                            final_response = f"📋 {len(tasks)} {task_word} found:\n"
                            
                            for i, task in enumerate(tasks[:10], 1):
                                emoji = "✅" if task['status'] == 'completed' else "🔄" if task['status'] == 'in_progress' else "📝"
                                final_response += f"\n{i}. {emoji} {task['title']}"
                                
                                details = []
                                if task['priority']:
                                    details.append(f"Priority: {task['priority']}")
                                if task['status'] != 'completed':
                                    details.append(f"Status: {task['status'].replace('_', ' ')}")
                                if task.get('due_date'):
                                    details.append(f"Due: {task['due_date']}")
                                if task.get('category'):
                                    details.append(f"Category: {task['category']}")
                                
                                if details:
                                    final_response += f"\n   {' | '.join(details)}"
                else:
                    final_response = f"❌ {result.get('error')}"
                
                self.conversation_history.append(ChatMessage("assistant", final_response))
                return final_response
            else:
                final_response = parsed["data"].strip()
                self.conversation_history.append(ChatMessage("assistant", final_response))
                return final_response
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.conversation_history.append(ChatMessage("assistant", error_msg))
            return error_msg

# Global agent instance
agent = TodoAgent()
