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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [refreshKey, setRefreshKey] = useState(0); // NEW: Force refresh key
  const chatEndRef = useRef(null);

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

  // NEW: Refetch when refreshKey changes
  useEffect(() => {
    if (token && isLoggedIn) {
      fetchTasks();
    }
  }, [refreshKey]);

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

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
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
      // Force refresh
      setRefreshKey(prev => prev + 1);
    } catch (error) {
      console.error('Failed to complete task');
    }
  };

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

  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const filteredTasks = getFilteredTasks();

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={toggleSidebar}></div>
      )}

      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>📋 Your Tasks</h2>
          <button className="close-sidebar" onClick={toggleSidebar}>✕</button>
        </div>

        <div className="sidebar-tabs">
          <button 
            className={`sidebar-tab ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            📋 All ({tasks.length})
          </button>
          <button 
            className={`sidebar-tab ${activeTab === 'today' ? 'active' : ''}`}
            onClick={() => setActiveTab('today')}
          >
            📅 Today
          </button>
          <button 
            className={`sidebar-tab ${activeTab === 'week' ? 'active' : ''}`}
            onClick={() => setActiveTab('week')}
          >
            📆 This Week
          </button>
          <button 
            className={`sidebar-tab ${activeTab === 'urgent' ? 'active' : ''}`}
            onClick={() => setActiveTab('urgent')}
          >
            🔥 Urgent
          </button>
          <button 
            className={`sidebar-tab ${activeTab === 'high' ? 'active' : ''}`}
            onClick={() => setActiveTab('high')}
          >
            ⭐ High
          </button>
          <button 
            className={`sidebar-tab ${activeTab === 'completed' ? 'active' : ''}`}
            onClick={() => setActiveTab('completed')}
          >
            ✅ Completed
          </button>
        </div>

        <div className="sidebar-tasks">
          {filteredTasks.length === 0 ? (
            <div className="empty-sidebar">
              <p>No tasks found</p>
            </div>
          ) : (
            filteredTasks.map((task) => (
              <div key={task.id} className="sidebar-task">
                <div className="sidebar-task-header">
                  <span className={`priority-dot ${task.priority}`}></span>
                  <h4>{task.title}</h4>
                </div>
                {task.due_date && (
                  <p className="sidebar-task-date">📅 {task.due_date}</p>
                )}
                <span className={`priority-badge-small ${task.priority}`}>
                  {task.priority.toUpperCase()}
                </span>
                <div className="sidebar-task-actions">
                  {task.status !== 'completed' && (
                    <button 
                      onClick={() => completeTask(task.id)}
                      className="sidebar-action-btn complete"
                      title="Mark as complete"
                    >
                      ✓
                    </button>
                  )}
                  <button 
                    onClick={() => deleteTask(task.id)}
                    className="sidebar-action-btn delete"
                    title="Delete task"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        <button className="refresh-tasks-btn" onClick={() => fetchTasks()}>
          🔄 Refresh Tasks
        </button>
      </div>

      <div className="main-content">
        <header className="app-header">
          <div className="header-left">
            <button className="hamburger-btn" onClick={toggleSidebar}>
              ☰
            </button>
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

        <div className="chat-container-fullscreen">
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
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your message..."
              disabled={loading}
            />
            <button onClick={sendMessage} disabled={loading} className="send-btn">
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
