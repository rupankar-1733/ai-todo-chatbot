# 🤖 AI Todo Chatbot

A modern, AI-powered todo list application with natural language processing and semantic search.

## ✨ Features

- 🤖 **AI-Powered Chat Interface** - Manage tasks using natural language
- 🔍 **Semantic Search (RAG)** - Find tasks intelligently using vector embeddings
- 🔐 **User Authentication** - Secure JWT-based login system
- 📊 **Analytics Dashboard** - Track productivity and task completion
- 🌙 **Dark Mode** - Beautiful theme toggle
- 📱 **Responsive Design** - Works on all devices
- ⚡ **Real-time Updates** - Instant task synchronization

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Groq AI** - LLM for natural language understanding
- **Sentence Transformers** - Vector embeddings for RAG
- **JWT** - Secure authentication
- **bcrypt** - Password hashing

### Frontend
- **React** - UI framework
- **Axios** - HTTP client
- **CSS3** - Modern styling with dark mode

## 🚀 Live Demo

- **Frontend**: [Your Vercel URL]
- **Backend**: [Your HF Spaces URL]

## 📦 Installation

### Backend
cd todo-ai-chatbot
python -m venv aitodo
source aitodo/bin/activate # Windows: aitodo\Scripts\activate
pip install -r requirements.txt

### Frontend
cd frontend
npm install


## 🔑 Environment Variables

Create `.env` in root:
GROQ_API_KEY=your_groq_key
JWT_SECRET=your_secret_key


## 🏃 Run Locally

### Backend
uvicorn api.index:app --reload


### Frontend
cd frontend
npm start

## 🎯 Features in Detail

### Natural Language Task Management
- "Add urgent task to buy groceries"
- "Show me high priority tasks"
- "Mark dentist appointment as done"

### Semantic Search
- "Find tasks about work"
- "Show me medical appointments"
- Understands context and related terms

### Analytics
- Task completion rate
- Priority breakdown
- Status tracking

## 📝 License

MIT

## 👨‍💻 Author

[Your Name]
- GitHub: [https://github.com/rupankar-1733]
- LinkedIn: [https://www.linkedin.com/in/rupankar-mondal-931bbb259/]

---
Built with ❤️ using AI and modern web technologies