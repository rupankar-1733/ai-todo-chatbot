import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from api.database import db
from api.schemas import Task, ChatMessage
from api.nlp_utils import nlp_utils
from api.date_parser import date_parser
import json
import re


class TodoAgent:
    """
    Production AI Todo Agent - Final Version with LLM Intent Classification
    
    Architecture:
    Phase 1: Handle follow-ups (context preservation)
    Phase 1.5: LLM Intent Classification (greeting/casual/task_creation/task_operation)
    Phase 2: Based on intent - route to Python NLP or LLM
    Phase 3: Execute action
    """
    
    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY")
        
        print("🚀 Initializing AI Todo Agent v4.0 (LLM Intent Classification)")
        self.client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )
        print("✅ Groq LLM initialized")
        
        print("📊 Loading RAG model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ RAG model loaded")
        
        self.conversation_history: List[ChatMessage] = []
        self.current_username = None
        self.conversation_state = {
            "mode": "normal",
            "pending_task": None,
            "original_query": None
        }
        
    def set_username(self, username: str):
        self.current_username = username
        print(f"👤 User: {username}")
        
    def reset_conversation_state(self):
        self.conversation_state = {
            "mode": "normal",
            "pending_task": None,
            "original_query": None
        }
        print("🔄 State reset")
        
    def classify_intent(self, user_message: str) -> Dict[str, Any]:
        """
        LLM Intent Classification - Fast, accurate, context-aware
        Returns: {
            "intent": "greeting" | "casual" | "task_creation" | "task_operation",
            "confidence": "high" | "medium" | "low"
        }
        """
        prompt = f"""Classify the user's intent. Reply ONLY with JSON in this exact format:
{{"intent": "greeting/casual/task_creation/task_operation", "confidence": "high/medium/low"}}

Intent definitions:
- greeting: Introductions, greetings (e.g., "Hi I am John", "Hello", "Good morning")
- casual: General conversation, statements (e.g., "I work at Google", "How are you")
- task_creation: Creating a new task (e.g., "Buy flowers", "Call doctor tomorrow", "Meeting with boss")
- task_operation: Operating on existing tasks (e.g., "Show all tasks", "Complete buy laptop", "Delete meeting")

Examples:
User: "Hi I am pramit"
{{"intent": "greeting", "confidence": "high"}}

User: "I work at Google"
{{"intent": "casual", "confidence": "high"}}

User: "Buy flowers"
{{"intent": "task_creation", "confidence": "high"}}

User: "Call doctor tomorrow"
{{"intent": "task_creation", "confidence": "high"}}

User: "urgent meeting with team next week"
{{"intent": "task_creation", "confidence": "high"}}

User: "Show all my tasks"
{{"intent": "task_operation", "confidence": "high"}}

User: "Complete buy laptop"
{{"intent": "task_operation", "confidence": "high"}}

User: "I need to buy groceries but not sure when"
{{"intent": "task_creation", "confidence": "medium"}}

Now classify:
User: "{user_message}"
JSON:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            content = response.choices[0].message.content.strip()
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', content)
            if json_match:
                result = json.loads(json_match.group(0))
                print(f"🎯 Intent: {result.get('intent')} (Confidence: {result.get('confidence')})")
                return result
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"⚠️ Intent classification failed: {e}, using fallback")
            # Fallback: use task verb detection
            if nlp_utils.has_task_intent(user_message):
                return {"intent": "task_creation", "confidence": "low"}
            return {"intent": "casual", "confidence": "low"}

    def generate_embedding(self, text: str) -> List[float]:
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def parse_llm_response(self, response: str) -> Dict[str, Any]:
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
        all_tasks = db.get_all_tasks(self.current_username)
        title_lower = title_query.lower()
        
        for task in all_tasks:
            if task.title.lower() == title_lower:
                return task
        
        for task in all_tasks:
            if title_lower in task.title.lower() or task.title.lower() in title_lower:
                return task
        
        for task in all_tasks:
            if nlp_utils.fuzzy_match(title_lower, [task.title.lower()], threshold=0.7):
                return task
        
        return None

    def get_system_prompt(self) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        return f"""You are TaskMate, an AI assistant. Today is {today}.

For task operations:
- list_tasks: {{"function": "list_tasks", "parameters": {{"status": "todo/completed", "priority": "low/medium/high/urgent"}}}}
- search_tasks: {{"function": "search_tasks", "parameters": {{"query": "text"}}}}
- delete_task: {{"function": "delete_task", "parameters": {{"title": "task name"}}}}
- complete_task: {{"function": "complete_task", "parameters": {{"title": "task name"}}}}

For greetings and casual conversation, respond naturally without JSON."""

    def handle_incomplete_task(self, title: str, missing: List[str], original_message: str = None) -> str:
        extracted_date = date_parser.parse_relative_date(original_message or title)
        extracted_priority = nlp_utils.extract_priority(original_message or title)
        
        self.conversation_state = {
            "mode": "awaiting_info",
            "pending_task": {
                "title": title,
                "due_date": extracted_date,
                "priority": extracted_priority
            },
            "missing": missing,
            "original_query": original_message or title
        }
        
        if not extracted_date and not extracted_priority:
            return f"📝 To create '{title}':\n\n📅 When? (today, tomorrow, next week)\n🎯 Priority? (low, medium, high, urgent)"
        elif not extracted_date:
            return f"📅 When should '{title}' be done?"
        elif not extracted_priority:
            return f"🎯 What priority for '{title}'?\n\n[Low] [Medium] [High] [Urgent]"

    def process_followup_response(self, user_input: str) -> Dict[str, Any]:
        pending = self.conversation_state.get("pending_task", {})
        
        extracted_date = date_parser.parse_relative_date(user_input)
        extracted_priority = nlp_utils.extract_priority(user_input)
        
        if extracted_date and not pending.get("due_date"):
            pending["due_date"] = extracted_date
        
        if extracted_priority and not pending.get("priority"):
            pending["priority"] = extracted_priority
        
        self.conversation_state["pending_task"] = pending
        
        if pending.get("due_date") and pending.get("priority"):
            return self.create_task_from_pending()
        
        if not pending.get("due_date"):
            return {"type": "ask_more", "message": "📅 When?"}
        elif not pending.get("priority"):
            return {"type": "ask_more", "message": "🎯 Priority?"}

    def create_task_from_pending(self) -> Dict[str, Any]:
        pending = self.conversation_state.get("pending_task", {})
        result = self.execute_function("create_task", pending)
        self.reset_conversation_state()
        return {"type": "complete", "result": result}

    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if function_name == "create_task":
                title = parameters.get("title")
                if not title:
                    return {"success": False, "error": "Title required"}
                
                existing_task = self.find_task_by_title(title)
                if existing_task and existing_task.status != "completed":
                    return {"success": False, "error": f"Task '{title}' exists"}
                
                embedding = self.generate_embedding(title)
                task = db.create_task(
                    title=title,
                    username=self.current_username,
                    priority=parameters.get("priority") or "medium",
                    due_date=parameters.get("due_date"),
                    embedding=embedding
                )
                
                return {
                    "success": True,
                    "message": f"✅ Created: '{task.title}' (Priority: {task.priority}, Due: {task.due_date or 'None'})",
                    "task": task.to_dict()
                }
            
            elif function_name == "list_tasks":
                tasks = db.search_tasks(
                    username=self.current_username,
                    status=parameters.get("status"),
                    priority=parameters.get("priority")
                )
                return {"success": True, "tasks": [t.to_dict() for t in tasks], "count": len(tasks)}
            
            elif function_name == "complete_task":
                title = parameters.get("title")
                task = self.find_task_by_title(title)
                if not task:
                    return {"success": False, "error": f"Task '{title}' not found"}
                
                updated = db.update_task(task.id, self.current_username, status="completed")
                return {"success": True, "message": f"✅ Completed: '{updated.title}'"}
            
            elif function_name == "delete_task":
                title = parameters.get("title")
                task = self.find_task_by_title(title)
                if not task:
                    return {"success": False, "error": f"Task '{title}' not found"}
                
                db.delete_task(task.id, self.current_username)
                return {"success": True, "message": f"🗑️ Deleted: '{task.title}'"}
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}

    def handle_llm_conversation(self, user_message: str) -> str:
        """Handle natural conversation and task operations via LLM"""
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
                max_tokens=400
            )
            
            llm_response = completion.choices[0].message.content
            parsed = self.parse_llm_response(llm_response)
            
            if parsed["type"] == "function_call":
                result = self.execute_function(
                    parsed["data"].get("function"),
                    parsed["data"].get("parameters", {})
                )
                
                if result.get("success"):
                    final_response = result.get("message", "Done!")
                    if "tasks" in result:
                        tasks = result["tasks"]
                        if len(tasks) > 0:
                            final_response = f"📋 {len(tasks)} task(s):\n"
                            for i, t in enumerate(tasks[:10], 1):
                                emoji = "✅" if t['status'] == 'completed' else "📝"
                                final_response += f"\n{i}. {emoji} {t['title']}"
                else:
                    final_response = f"❌ {result.get('error')}"
            else:
                final_response = parsed["data"].strip()
            
            self.conversation_history.append(ChatMessage("assistant", final_response))
            return final_response
            
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_old_context(self):
        if len(self.conversation_history) > 8:
            self.conversation_history = self.conversation_history[-8:]

    def chat(self, user_message: str) -> str:
        """
        MAIN INTERFACE - Production Version with LLM Intent Classification
        """
        if not self.current_username:
            return "Error: No user authenticated"
        
        print(f"\n{'='*60}")
        print(f"💬 User: {user_message}")
        print(f"{'='*60}")
        
        # PHASE 1: Handle follow-ups
        if self.conversation_state.get("mode") == "awaiting_info":
            followup_result = self.process_followup_response(user_message)
            if followup_result["type"] == "ask_more":
                return followup_result["message"]
            elif followup_result["type"] == "complete":
                result = followup_result["result"]
                return result.get("message") if result.get("success") else f"❌ {result.get('error')}"
        
        # PHASE 1.5: LLM Intent Classification
        print("🎯 Classifying intent...")
        intent_result = self.classify_intent(user_message)
        intent = intent_result.get("intent", "casual")
        
        # PHASE 2: Route based on intent
        if intent in ["greeting", "casual", "task_operation"]:
            print(f"💬 {intent.title()} - using LLM")
            return self.handle_llm_conversation(user_message)
        
        # PHASE 3: Task creation via Python NLP
        if intent == "task_creation":
            print("📋 Task creation - using Python NLP")
            
            extracted_date = date_parser.parse_relative_date(user_message)
            extracted_priority = nlp_utils.extract_priority(user_message)
            
            word_count = len(user_message.split())
            if word_count > 10:
                clean_title = nlp_utils.extract_task_title_llm(user_message, self.client)
            else:
                clean_title = nlp_utils.extract_task_title(user_message)
            
            if not clean_title:
                return "❌ Could not extract task title"
            
            print(f"📊 Extracted - Title: '{clean_title}', Date: {extracted_date}, Priority: {extracted_priority}")
            
            if extracted_date and extracted_priority:
                result = self.execute_function("create_task", {
                    "title": clean_title,
                    "due_date": extracted_date,
                    "priority": extracted_priority
                })
                return result.get("message") if result.get("success") else f"❌ {result.get('error')}"
            
            missing = []
            if not extracted_date:
                missing.append("date")
            if not extracted_priority:
                missing.append("priority")
            
            return self.handle_incomplete_task(clean_title, missing, user_message)
        
        # Fallback
        return self.handle_llm_conversation(user_message)


# Global instance
agent = TodoAgent()
