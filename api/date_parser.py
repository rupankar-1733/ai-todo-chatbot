"""
Enterprise Date Parser for AI Todo System
Handles complex date expressions with high accuracy
"""
from datetime import datetime, timedelta
from typing import Optional
import re


class DateParser:
    """Advanced date parsing with natural language support"""
    
    @staticmethod
    def parse_relative_date(text: str, base_date: Optional[datetime] = None) -> Optional[str]:
        """
        Parse relative dates from natural language
        Returns ISO date string (YYYY-MM-DD) or None
        """
        if base_date is None:
            base_date = datetime.now()
        
        text_lower = text.lower().strip()
        
        # Direct keyword mapping
        if "today" in text_lower or "tody" in text_lower:
            return base_date.strftime("%Y-%m-%d")
        
        if "tomorrow" in text_lower or "tmrw" in text_lower or "tmw" in text_lower:
            return (base_date + timedelta(days=1)).strftime("%Y-%m-%d")
        
        if "day after tomorrow" in text_lower or "dayaftertomorrow" in text_lower:
            return (base_date + timedelta(days=2)).strftime("%Y-%m-%d")
        
        if "next week" in text_lower or "nxt week" in text_lower:
            return (base_date + timedelta(days=7)).strftime("%Y-%m-%d")
        
        if "this week" in text_lower:
            days_until_friday = (4 - base_date.weekday()) % 7
            return (base_date + timedelta(days=days_until_friday)).strftime("%Y-%m-%d")
        
        # Parse "in X days"
        match = re.search(r'in\s+(\d+)\s+days?', text_lower)
        if match:
            days = int(match.group(1))
            return (base_date + timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Parse "next monday", "next friday", etc.
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for day_name, day_num in weekdays.items():
            if f"next {day_name}" in text_lower:
                days_ahead = day_num - base_date.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return (base_date + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        # Parse specific date formats (YYYY-MM-DD, DD/MM/YYYY, etc.)
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # 2025-10-28
            r'(\d{2})/(\d{2})/(\d{4})',  # 28/10/2025
            r'(\d{2})-(\d{2})-(\d{4})',  # 28-10-2025
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if '-' in pattern and pattern.startswith(r'(\d{4})'):
                        # YYYY-MM-DD format
                        year, month, day = match.groups()
                        return f"{year}-{month}-{day}"
                    else:
                        # DD/MM/YYYY or DD-MM-YYYY format
                        day, month, year = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    pass
        
        return None
    
    @staticmethod
    def has_date_reference(text: str) -> bool:
        """Check if text contains any date reference"""
        date_keywords = [
            'today', 'tomorrow', 'tmrw', 'day after', 'next week',
            'this week', 'in', 'days', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in date_keywords)


# Global instance
date_parser = DateParser()
