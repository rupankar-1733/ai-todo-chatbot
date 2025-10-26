import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Login from './Login';
import './App.css';
import Dashboard from './Dashboard';

const API_URL = 'https://raka-1733-ai-todo-chatbot.hf.space';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [token, setToken] = useState('');
  
  // DARK MODE STATE
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hi! I\'m your AI todo assistant. Try saying:\n• "Add buy groceries"\n• "Show me all tasks"\n• "Create high priority task to finish report"'
    }
  ]);
  const [input, setInput] = useState('');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // APPLY DARK MODE
  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode);
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  // Check for existing token on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUsername = localStorage.getItem('username');
    
    if (savedToken && savedUsername) {
      verifyToken(savedToken, savedUsername);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const verifyToken = async (token, username) => {
    try {
      await axios.get(`${API_URL}/api/verify`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setToken(token);
      setUsername(username);
      setIsAuthenticated(true);
      loadTasks(token);
    } catch (error) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      setIsAuthenticated(false);
    }
  };

  const handleLoginSuccess = (newToken, newUsername) => {
    setToken(newToken);
    setUsername(newUsername);
    setIsAuthenticated(true);
    loadTasks(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setToken('');
    setUsername('');
    setIsAuthenticated(false);
    setTasks([]);
    setMessages([{
      role: 'assistant',
      content: '👋 Hi! I\'m your AI todo assistant.'
    }]);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadTasks = async (authToken = token) => {
    try {
      const response = await axios.get(`${API_URL}/api/tasks`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setTasks(response.data.tasks);
    } catch (error) {
      console.error('Error loading tasks:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, 
        { message: userMessage },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
      loadTasks();
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '❌ Error: Could not process request.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm('Delete this task?')) return;
    
    try {
      await axios.delete(`${API_URL}/api/tasks/${taskId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadTasks();
      setMessages(prev => [...prev, { role: 'assistant', content: '✅ Task deleted' }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: '❌ Error deleting task' }]);
    }
  };

  const getStatusEmoji = (status) => {
    return status === 'completed' ? '✅' : status === 'in_progress' ? '🔄' : '📝';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'priority-urgent',
      high: 'priority-high',
      medium: 'priority-medium',
      low: 'priority-low'
    };
    return colors[priority] || 'priority-medium';
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className={`app ${darkMode ? 'dark' : ''}`}>
      <div className="container">
        <div className="header">
          <div>
            <h1>🤖 AI Todo Assistant</h1>
            <p>Chat with me to manage your tasks naturally!</p>
          </div>
          <div className="header-right">
            <button onClick={toggleDarkMode} className="dark-mode-toggle" title="Toggle Dark Mode">
              {darkMode ? '☀️' : '🌙'}
            </button>
            <span className="username">👤 {username}</span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
        
        <Dashboard tasks={tasks} darkMode={darkMode} />

        <div className="chat-container">
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="avatar">
                  {msg.role === 'assistant' ? 'AI' : 'You'}
                </div>
                <div className="message-content">
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message assistant">
                <div className="avatar">AI</div>
                <div className="message-content loading">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </div>

        <div className="task-list-container">
          <div className="task-list-header">
            <h2>📋 Your Tasks ({tasks.length})</h2>
            <button onClick={() => loadTasks()} className="refresh-btn">
              Refresh
            </button>
          </div>
          <div className="task-list">
            {tasks.length === 0 ? (
              <p className="no-tasks">No tasks yet. Create one by chatting above!</p>
            ) : (
              tasks.map(task => (
                <div key={task.id} className="task-card">
                  <div className="task-info">
                    <div className="task-title">
                      <span className="task-emoji">{getStatusEmoji(task.status)}</span>
                      <h3>{task.title}</h3>
                    </div>
                    {task.description && (
                      <p className="task-description">{task.description}</p>
                    )}
                    <div className="task-meta">
                      {task.status !== 'completed' && (
                        <span className={`priority-badge ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                      )}
                      <span className="status-badge">
                        {task.status.replace('_', ' ')}
                      </span>
                      {task.due_date && (
                        <span className="due-date">Due: {task.due_date}</span>
                      )}
                    </div>
                  </div>
                  <button 
                    onClick={() => deleteTask(task.id)} 
                    className="delete-btn"
                    title="Delete task"
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
