from typing import List, Dict, Any
from datetime import datetime, timedelta
import re

def parse_relative_date(date_string: str) -> str:
    """
    Parse relative date strings like 'tomorrow', 'next week', 'in 3 days'
    Returns ISO format date string
    """
    today = datetime.now()
    date_string = date_string.lower().strip()
    
    # Tomorrow
    if 'tomorrow' in date_string:
        return (today + timedelta(days=1)).date().isoformat()
    
    # Today
    if 'today' in date_string:
        return today.date().isoformat()
    
    # Next week
    if 'next week' in date_string:
        return (today + timedelta(weeks=1)).date().isoformat()
    
    # Next month
    if 'next month' in date_string:
        return (today + timedelta(days=30)).date().isoformat()
    
    # In X days
    days_match = re.search(r'in (\d+) days?', date_string)
    if days_match:
        days = int(days_match.group(1))
        return (today + timedelta(days=days)).date().isoformat()
    
    # In X weeks
    weeks_match = re.search(r'in (\d+) weeks?', date_string)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        return (today + timedelta(weeks=weeks)).date().isoformat()
    
    # Day of week (e.g., "monday", "next friday")
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day_name, day_num in weekdays.items():
        if day_name in date_string:
            days_ahead = day_num - today.weekday()
            if days_ahead <= 0 or 'next' in date_string:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).date().isoformat()
    
    # Return original if no pattern matched
    return date_string

def extract_priority(text: str) -> str:
    """
    Extract priority from text
    """
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['urgent', 'asap', 'critical', 'immediately']):
        return 'urgent'
    elif any(word in text_lower for word in ['high priority', 'important', 'high']):
        return 'high'
    elif any(word in text_lower for word in ['low priority', 'low', 'minor']):
        return 'low'
    else:
        return 'medium'

def extract_tags(text: str) -> List[str]:
    """
    Extract hashtags from text
    """
    return re.findall(r'#(\w+)', text)

def format_task_list(tasks: List[Dict[str, Any]]) -> str:
    """
    Format a list of tasks into a readable string
    """
    if not tasks:
        return "No tasks found."
    
    output = f"Found {len(tasks)} task(s):\n\n"
    
    for i, task in enumerate(tasks, 1):
        output += f"{i}. {task['title']}\n"
        output += f"   Priority: {task['priority']} | Status: {task['status']}\n"
        
        if task.get('due_date'):
            output += f"   Due: {task['due_date']}\n"
        
        if task.get('category'):
            output += f"   Category: {task['category']}\n"
        
        if task.get('description'):
            output += f"   Description: {task['description']}\n"
        
        output += f"   ID: {task['id']}\n\n"
    
    return output

def get_task_stats(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for a list of tasks
    """
    total = len(tasks)
    
    if total == 0:
        return {
            "total": 0,
            "completed": 0,
            "in_progress": 0,
            "todo": 0,
            "completion_rate": 0
        }
    
    completed = sum(1 for task in tasks if task['status'] == 'completed')
    in_progress = sum(1 for task in tasks if task['status'] == 'in_progress')
    todo = sum(1 for task in tasks if task['status'] == 'todo')
    
    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "todo": todo,
        "completion_rate": round((completed / total) * 100, 1) if total > 0 else 0
    }
