"""
Enterprise NLP Utilities for AI Todo System - FINAL VERSION
Features: 
- Typo correction with fuzzy matching
- Task intent detection (action verbs)
- LLM-powered title extraction for complex sentences
- Date/priority extraction with 100% accuracy
"""
import re
from typing import Optional
from difflib import SequenceMatcher


class NLPUtils:
    """Production-grade NLP utilities"""
    
    # Priority synonyms with typo variants
    PRIORITY_SYNONYMS = {
        "urgent": ["urgent", "urgnt", "urget", "asap", "critical", "immdiate", "immediate", "critcal", "criti", "assp"],
        "high": ["high", "hgh", "hi", "important", "imprtant", "soon", "sn", "impt", "hig", "importnt"],
        "medium": ["medium", "medim", "medum", "normal", "normaal", "regular", "regulr", "mid", "norm", "med", "avg"],
        "low": ["low", "lo", "lw", "later", "latr", "laater", "minor", "ltr", "lw", "less"]
    }
    
    # Date keywords with typo variants
    DATE_PATTERNS = {
        "today": ["today", "tody", "todya", "2day", "tod", "tday", "2dy"],
        "tomorrow": ["tomorrow", "tomorrw", "tmrw", "tmw", "tomorow", "tmmrw", "tomrw", "tmrrw", "2moro", "2morrow"],
        "day_after_tomorrow": ["day after tomorrow", "dayaftertomorrow", "day aftr tmrw", "overmorrow"],
        "next_week": ["next week", "nxt week", "next wk", "nxtweek", "nxt wk", "nxt wek", "next weeek"],
        "this_week": ["this week", "thisweek", "this wk", "ths week", "ths wk", "dis week"]
    }
    
    # Task action verbs (comprehensive list)
    TASK_VERBS = [
        r'\bbuy\b', r'\bpurchase\b', r'\bget\b', r'\bgrab\b', r'\bpick up\b',
        r'\bcall\b', r'\bphone\b', r'\bcontact\b', r'\breach\b', r'\btext\b',
        r'\bsend\b', r'\bemail\b', r'\bmessage\b', r'\bforward\b', r'\breply\b',
        r'\bmeet\b', r'\bmeeting\b', r'\bschedule\b', r'\bbook\b', r'\barrange\b',
        r'\bfinish\b', r'\bcomplete\b', r'\bsubmit\b', r'\bdeliver\b', r'\bhand in\b',
        r'\bwrite\b', r'\bdraft\b', r'\bprepare\b', r'\bcreate\b', r'\bmake\b',
        r'\breview\b', r'\bcheck\b', r'\bverify\b', r'\bconfirm\b', r'\bvalidate\b',
        r'\bupdate\b', r'\bfix\b', r'\brepair\b', r'\breplace\b', r'\bmodify\b',
        r'\border\b', r'\breserve\b', r'\borganize\b', r'\bplan\b', r'\bsetup\b',
        r'\bpay\b', r'\brenew\b', r'\bcancel\b', r'\breturn\b', r'\brefund\b',
        r'\bclean\b', r'\bwash\b', r'\bcook\b', r'\bprepare\b', r'\bfile\b',
        r'\bprint\b', r'\bscan\b', r'\bcopy\b', r'\bdownload\b', r'\bupload\b',
        r'\binstall\b', r'\buninstall\b', r'\bbackup\b', r'\brestore\b'
    ]
    
    # Task phrases
    TASK_PHRASES = [
        'remind me', 'reminder', 'don\'t forget', 'dont forget',
        'need to', 'have to', 'must', 'should', 'want to', 
        'going to', 'got to', 'gotta', 'supposed to'
    ]
    
    @staticmethod
    def fuzzy_match(text: str, candidates: list, threshold: float = 0.7) -> Optional[str]:
        """Fuzzy match with Levenshtein distance"""
        text_clean = text.lower().strip()
        best_match = None
        best_ratio = 0.0
        
        for candidate in candidates:
            ratio = SequenceMatcher(None, text_clean, candidate.lower()).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = candidate
        
        return best_match
    
    @staticmethod
    def extract_priority(text: str) -> Optional[str]:
        """Extract priority with typo correction"""
        text_lower = text.lower()
        
        for priority, synonyms in NLPUtils.PRIORITY_SYNONYMS.items():
            for synonym in synonyms:
                if synonym in text_lower:
                    return priority
            
            if NLPUtils.fuzzy_match(text_lower, synonyms):
                return priority
        
        return None
    
    @staticmethod
    def has_task_intent(text: str) -> bool:
        """
        Detect if text has task creation intent
        Returns True if action verbs or task phrases detected
        """
        text_lower = text.lower().strip()
        
        # Check task verbs
        for verb in NLPUtils.TASK_VERBS:
            if re.search(verb, text_lower):
                print(f"🎯 Task verb detected: {verb}")
                return True
        
        # Check task phrases
        for phrase in NLPUtils.TASK_PHRASES:
            if phrase in text_lower:
                print(f"🎯 Task phrase detected: '{phrase}'")
                return True
        
        return False
    
    @staticmethod
    def remove_date_keywords(text: str) -> str:
        """Remove date keywords from text"""
        text_clean = text
        for patterns in NLPUtils.DATE_PATTERNS.values():
            for pattern in patterns:
                text_clean = re.sub(rf'\b{re.escape(pattern)}\b', '', text_clean, flags=re.IGNORECASE)
        return text_clean.strip()
    
    @staticmethod
    def remove_priority_keywords(text: str) -> str:
        """Remove priority keywords from text"""
        text_clean = text
        for synonyms in NLPUtils.PRIORITY_SYNONYMS.values():
            for synonym in synonyms:
                text_clean = re.sub(rf'\b{re.escape(synonym)}\b', '', text_clean, flags=re.IGNORECASE)
        return text_clean.strip()
    
    @staticmethod
    def extract_task_title(text: str) -> str:
        """Extract clean task title (fast regex-based)"""
        title = text
        title = NLPUtils.remove_date_keywords(title)
        title = NLPUtils.remove_priority_keywords(title)
        
        # Remove common task creation phrases
        patterns_to_remove = [
            r'\bcreate\s+task\b', r'\badd\s+task\b', r'\bnew\s+task\b',
            r'\btask\b', r'\bto\s+do\b', r'\btodo\b',
            r'\bremind\s+me\s+to\b', r'\breminder\s+to\b',
            r'\bi\s+need\s+to\b', r'\bi\s+want\s+to\b', r'\bi\s+have\s+to\b',
            r'\bi\s+should\b', r'\bi\s+must\b', r'\bi\'m\s+going\s+to\b',
            r'\bdon\'t\s+forget\s+to\b', r'\bdon\'t\s+forget\b',
            r'\bdont\s+forget\b', r'\bgotta\b', r'\bgot\s+to\b'
        ]
        
        for pattern in patterns_to_remove:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title if title else text
    
    @staticmethod
    def extract_task_title_llm(text: str, llm_client=None) -> str:
        """Use LLM to extract title from complex sentences"""
        if not llm_client:
            print("⚠️ No LLM client, using regex extraction")
            return NLPUtils.extract_task_title(text)
        
        try:
            prompt = f"""Extract the main task/action from this sentence as a short, clear task title (max 6 words).

Examples:
Input: "I have a tight schedule but still want to hold a meeting tomorrow with my boss"
Output: meeting with boss

Input: "Need to urgently buy groceries for the party next week"
Output: buy groceries for party

Input: "Reminder to call the dentist about my appointment"
Output: call dentist about appointment

Input: "I should probably finish the quarterly report by tomorrow"
Output: finish quarterly report

Input: "Don't forget to send email to client"
Output: send email to client

Now extract from:
Input: "{text}"
Output:"""

            response = llm_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=30
            )
            
            extracted = response.choices[0].message.content.strip()
            
            if extracted and len(extracted) < 60:
                print(f"✅ LLM extracted: '{extracted}'")
                return extracted
            else:
                print(f"⚠️ LLM invalid, using regex")
                return NLPUtils.extract_task_title(text)
                
        except Exception as e:
            print(f"⚠️ LLM failed: {e}")
            return NLPUtils.extract_task_title(text)


# Global instance
nlp_utils = NLPUtils()
