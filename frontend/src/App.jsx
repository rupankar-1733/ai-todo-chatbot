import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Login from './Login';
import './App.css';

const API_URL = 'https://raka-1733-ai-todo-chatbot.hf.space';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [token, setToken] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState('all'); // NEW: Tab state
  const [currentPage, setCurrentPage] = useState(1); // NEW: Pagination
  const tasksPerPage = 8; // NEW: Limit tasks per page
  const chatEndRef = useRef(null);

  // Check for existing session
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUsername = localStorage.getItem('username');
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';

    if (savedToken && savedUsername) {
      setToken(savedToken);
      setUsername(savedUsername);
      setIsLoggedIn(true);
      fetchTasks(savedToken);
    }

    setDarkMode(savedDarkMode);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleLoginSuccess = (newToken, newUsername) => {
    setToken(newToken);
    setUsername(newUsername);
    setIsLoggedIn(true);
    fetchTasks(newToken);
    setMessages([{
      role: 'assistant',
      content: `👋 Hi ${newUsername}! I'm your AI todo assistant.`
    }]);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setIsLoggedIn(false);
    setToken('');
    setUsername('');
    setMessages([]);
    setTasks([]);
  };

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode);
  };

  const fetchTasks = async (authToken) => {
    try {
      const response = await axios.get(`${API_URL}/api/tasks`, {
        headers: { Authorization: `Bearer ${authToken || token}` }
      });
      setTasks(response.data.tasks || []);
    } catch (error) {
      console.error('Failed to fetch tasks');
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/api/chat`,
        { message: input },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const aiMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, aiMessage]);
      
      // Refresh tasks after AI response
      await fetchTasks();
    } catch (error) {
      const errorMessage = { 
        role: 'assistant', 
        content: '❌ Sorry, something went wrong.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await axios.delete(`${API_URL}/api/tasks/${taskId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchTasks();
    } catch (error) {
      console.error('Failed to delete task');
    }
  };

  const completeTask = async (taskId) => {
    try {
      await axios.patch(
        `${API_URL}/api/tasks/${taskId}`,
        { status: 'completed' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await fetchTasks();
    } catch (error) {
      console.error('Failed to complete task');
    }
  };

  // NEW: Filter tasks based on active tab
  const getFilteredTasks = () => {
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

    switch (activeTab) {
      case 'today':
        return tasks.filter(t => t.due_date === today && t.status !== 'completed');
      case 'week':
        return tasks.filter(t => t.due_date && t.due_date <= nextWeek && t.status !== 'completed');
      case 'urgent':
        return tasks.filter(t => t.priority === 'urgent' && t.status !== 'completed');
      case 'high':
        return tasks.filter(t => t.priority === 'high' && t.status !== 'completed');
      case 'completed':
        return tasks.filter(t => t.status === 'completed');
      case 'all':
      default:
        return tasks;
    }
  };

  // NEW: Paginate filtered tasks
  const getPaginatedTasks = () => {
    const filtered = getFilteredTasks();
    const startIndex = (currentPage - 1) * tasksPerPage;
    const endIndex = startIndex + tasksPerPage;
    return filtered.slice(startIndex, endIndex);
  };

  const totalPages = Math.ceil(getFilteredTasks().length / tasksPerPage);

  // Reset to page 1 when changing tabs
  useEffect(() => {
    setCurrentPage(1);
  }, [activeTab]);

  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const displayedTasks = getPaginatedTasks();

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <h1>🤖 AI Todo Assistant</h1>
        </div>
        <div className="header-right">
          <button onClick={toggleDarkMode} className="icon-btn">
            {darkMode ? '☀️' : '🌙'}
          </button>
          <div className="user-menu">
            <span className="username">{username}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="tabs-container">
        <button 
          className={`tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          📋 All
        </button>
        <button 
          className={`tab ${activeTab === 'today' ? 'active' : ''}`}
          onClick={() => setActiveTab('today')}
        >
          📅 Today
        </button>
        <button 
          className={`tab ${activeTab === 'week' ? 'active' : ''}`}
          onClick={() => setActiveTab('week')}
        >
          📆 This Week
        </button>
        <button 
          className={`tab ${activeTab === 'urgent' ? 'active' : ''}`}
          onClick={() => setActiveTab('urgent')}
        >
          🔥 Urgent
        </button>
        <button 
          className={`tab ${activeTab === 'high' ? 'active' : ''}`}
          onClick={() => setActiveTab('high')}
        >
          ⭐ High Priority
        </button>
        <button 
          className={`tab ${activeTab === 'completed' ? 'active' : ''}`}
          onClick={() => setActiveTab('completed')}
        >
          ✅ Completed
        </button>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading} className="send-btn">
            Send
          </button>
        </div>
      </div>

      {/* Tasks Container - Fixed Height, No Scroll */}
      <div className="tasks-container">
        <div className="tasks-header">
          <h2>📋 Your Tasks ({getFilteredTasks().length})</h2>
          <button onClick={() => fetchTasks()} className="refresh-btn">🔄 Refresh</button>
        </div>

        <div className="tasks-grid">
          {displayedTasks.length === 0 ? (
            <div className="empty-state">
              <p>No tasks found. Create one using the chat!</p>
            </div>
          ) : (
            displayedTasks.map((task) => (
              <div key={task.id} className="task-card">
                <div className="task-header-row">
                  <span className={`priority-badge ${task.priority}`}>
                    {task.priority}
                  </span>
                  <span className={`status-badge ${task.status}`}>
                    {task.status.replace('_', ' ')}
                  </span>
                </div>
                <h3 className="task-title">{task.title}</h3>
                {task.due_date && (
                  <p className="task-date">📅 Due: {task.due_date}</p>
                )}
                <div className="task-actions">
                  {task.status !== 'completed' && (
                    <button 
                      onClick={() => completeTask(task.id)}
                      className="action-btn complete"
                    >
                      ✓
                    </button>
                  )}
                  <button 
                    onClick={() => deleteTask(task.id)}
                    className="action-btn delete"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination">
            <button 
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="page-btn"
            >
              ← Prev
            </button>
            <span className="page-info">
              Page {currentPage} of {totalPages}
            </span>
            <button 
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="page-btn"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
