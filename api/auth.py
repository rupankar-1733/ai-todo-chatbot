import os
import jwt
import bcrypt
import re
from datetime import datetime, timedelta
from typing import Optional
import json

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours


def is_valid_email(email: str) -> bool:
    """Validate email format and check if domain has MX records"""
    # Basic format check
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False
    
    # Extract domain
    try:
        domain = email.split('@')[1].lower()
        
        # Check if domain has valid MX records (mail servers)
        if DNS_AVAILABLE:
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                return len(mx_records) > 0
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                return False
        else:
            # If DNS not available, just validate format
            return True
            
    except Exception as e:
        print(f"Email validation error: {e}")
        return False


class AuthService:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, username: str, email: str, password: str) -> dict:
        """Create new user with email validation"""
        
        # Validate email format and domain
        if not is_valid_email(email):
            return {
                "success": False, 
                "error": "Invalid email or domain does not exist"
            }
        
        # Check if username exists
        if username in self.users:
            return {"success": False, "error": "Username already exists"}
        
        # Check if email exists
        if any(u.get("email") == email for u in self.users.values()):
            return {"success": False, "error": "Email already exists"}
        
        # Create user
        user_data = {
            "username": username,
            "email": email,
            "password": self.hash_password(password),
            "created_at": datetime.now().isoformat()
        }
        
        self.users[username] = user_data
        self.save_users()
        
        return {"success": True, "message": "User created successfully"}
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token"""
        user = self.users.get(username)
        if not user:
            return None
        
        if not self.verify_password(password, user["password"]):
            return None
        
        # Create JWT token
        payload = {
            "username": username,
            "email": user["email"],
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


auth_service = AuthService()
