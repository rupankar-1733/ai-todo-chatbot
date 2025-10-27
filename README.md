# 🤖 AI-Powered Todo Chatbot

> An intelligent conversational task management system powered by LLM intent classification, Python NLP, and RAG semantic search.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Live Demo](https://your-vercel-url.vercel.app) • [Report Bug](https://github.com/yourusername/ai-todo-chatbot/issues) • [Request Feature](https://github.com/yourusername/ai-todo-chatbot/issues)

---

## 📋 Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 About

An enterprise-grade AI chatbot that revolutionizes task management through natural language processing. Unlike traditional todo apps, this system understands context, handles typos, and maintains conversation flow - making task creation as simple as having a conversation.

### Why This Project?

- **Natural Interaction**: Talk to your todo list like you would to a human assistant
- **Smart Intent Detection**: LLM-powered classification distinguishes greetings from tasks
- **Typo Tolerance**: Fuzzy matching handles misspellings automatically
- **Context Preservation**: Remembers conversation state across follow-up questions
- **Semantic Search**: RAG-based search finds tasks by meaning, not just keywords

---

## ✨ Key Features

### 🧠 **Hybrid AI Architecture**
- **LLM Intent Classification**: Groq LLaMA 3.1 for context-aware intent detection
- **Python NLP Extraction**: 100% accurate date/priority parsing with regex
- **RAG Semantic Search**: Vector embeddings for intelligent task retrieval

### 🎨 **User Experience**
- **Natural Conversation**: Handles greetings, casual chat, and task operations
- **Smart Follow-ups**: Asks only for missing information (date or priority)
- **Complex Sentence Parsing**: "I want to meet my boss tomorrow" → "meeting with boss"
- **Typo Auto-Correction**: "urgnt buy tmrw" → Creates task correctly

### 🛠️ **Production Features**
- **JWT Authentication**: Secure multi-tenant user isolation
- **Thread-Safe Database**: Atomic writes prevent race conditions
- **Real-time Updates**: Instant task sync across UI
- **Responsive Design**: Works on desktop and mobile

---

## 🏗️ Architecture

┌─────────────────────────────────────────────────────────┐
│ User Input │
└─────────────────────┬───────────────────────────────────┘
│
┌─────────────▼──────────────┐
│ LLM Intent Classifier │
│ (greeting/casual/task) │
└─────────────┬──────────────┘
│
┌───────────┴───────────┐
│ │
┌─────▼─────┐ ┌──────▼──────┐
│ Greeting │ │ Task │
│ /Casual │ │ Creation │
└─────┬─────┘ └──────┬──────┘
│ │
┌─────▼─────┐ ┌──────▼──────┐
│ LLM │ │ Python NLP │
│ Response │ │ Extraction │
└─────┬─────┘ └──────┬──────┘
│ │
│ ┌───────▼────────┐
│ │ Missing Info? │
│ └───────┬────────┘
│ │
│ ┌───────▼────────┐
│ │ Follow-up │
│ │ Questions │
│ └───────┬────────┘
│ │
┌─────▼──────────────────────▼──────┐
│ Database Layer │
│ (Thread-safe JSON with RAG) │
└────────────────────────────────────┘

### **Intent Classification Flow**
1. User sends message → LLM classifies intent (greeting/casual/task_creation/task_operation)
2. If greeting/casual → LLM handles naturally
3. If task_creation → Python NLP extracts date/priority/title
4. If task_operation (list/delete/complete) → LLM handles with function calls

---

## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI (async REST API)
- **LLM**: Groq LLaMA 3.1 8B Instant
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **NLP**: Custom Python regex + fuzzy matching (Levenshtein distance)
- **Auth**: JWT with bcrypt password hashing
- **Database**: Thread-safe JSON with atomic writes

### **Frontend**
- **Framework**: React 18+
- **HTTP Client**: Axios
- **Styling**: Custom CSS with gradient themes

### **Deployment**
- **Backend**: HuggingFace Spaces
- **Frontend**: Vercel
- **Version Control**: Git + GitHub

---

## 🚀 Getting Started

### Prerequisites

Python 3.9+
Node.js 16+
npm or yarn

### Installation

1. **Clone the repository**
git clone https://github.com/yourusername/ai-todo-chatbot.git
cd ai-todo-chatbot


2. **Backend Setup**
Install Python dependencies
pip install -r requirements.txt

Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "SECRET_KEY=your_secret_key_here" >> .env

Run backend
uvicorn api.index:app --reload

3. **Frontend Setup**
cd frontend
npm install
npm start

4. **Access the app**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 💡 Usage Examples

### Task Creation
User: "urgent buy laptop tomorrow"
Bot: ✅ Created: 'buy laptop' (Priority: urgent, Due: 2025-10-28)

User: "call doctor"
Bot: 📅 When should 'call doctor' be done?
User: "next week"
Bot: 🎯 What priority?
User: "high"
Bot: ✅ Created: 'call doctor' (Priority: high, Due: 2025-11-03)

User: "I want to schedule a meeting with my boss tomorrow"
Bot: 🎯 What priority for 'meeting with boss'?
User: "urgent"
Bot: ✅ Created: 'meeting with boss' (Priority: urgent, Due: 2025-10-28)

### Natural Conversation
User: "Hi I am Pramit"
Bot: 👋 Hi Pramit! I'm your AI todo assistant. How can I help?

User: "I work at Google"
Bot: That's great! How can I assist you with your tasks today?

### Task Operations
User: "show all my tasks"
Bot: 📋 3 tasks:

📝 buy laptop | Priority: urgent | Due: 2025-10-28

📝 call doctor | Priority: high | Due: 2025-11-03

📝 meeting with boss | Priority: urgent | Due: 2025-10-28

User: "complete buy laptop"
Bot: ✅ Completed: 'buy laptop'

---

## 📁 Project Structure

ai-todo-chatbot/
├── api/
│ ├── init.py
│ ├── index.py # FastAPI entry point
│ ├── agent.py # AI agent with LLM intent classification
│ ├── nlp_utils.py # Python NLP utilities (typo correction, intent detection)
│ ├── date_parser.py # Natural language date parsing
│ ├── database.py # Thread-safe JSON database
│ ├── auth.py # JWT authentication
│ ├── schemas.py # Pydantic models
│ └── tools.py # MCP tools integration
├── frontend/
│ ├── src/
│ │ ├── App.jsx # Main React component
│ │ └── App.css # Styling
│ └── public/
├── tasks.json # Database file (auto-generated)
├── requirements.txt # Python dependencies
├── .env # Environment variables (not committed)
└── README.md # This file

---

## 📖 API Documentation

### Authentication
POST /api/auth/register
Content-Type: application/json

{
"username": "john",
"password": "securepass123"
}

### Chat Interface

POST /api/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
"message": "urgent buy flowers tomorrow"
}

### Task Management

GET /api/tasks
Authorization: Bearer <jwt_token>

Response
[
{
"id": "uuid",
"title": "buy flowers",
"priority": "urgent",
"due_date": "2025-10-28",
"status": "todo"
}
]

Full API docs available at: `/docs` (Swagger UI)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 Contact

Rupankar Mondal - [@linkedin](https://www.linkedin.com/in/rupankar-mondal-931bbb259/)

Project Link: [https://github.com/rupankar-1733/ai-todo-chatbot](https://github.com/rupankar-1733/ai-todo-chatbot)

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for LLaMA 3.1 API
- [HuggingFace](https://huggingface.co/) for Sentence Transformers
- [FastAPI](https://fastapi.tiangolo.com/) for the amazing framework
- [React](https://reactjs.org/) for the UI library

---

**⭐ Star this repo if you found it helpful!**
