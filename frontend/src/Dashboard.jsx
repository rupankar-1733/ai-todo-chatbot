import React from 'react';
import './Dashboard.css';

function Dashboard({ tasks, darkMode }) {
  // Calculate statistics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const todoTasks = tasks.filter(t => t.status === 'todo').length;
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress').length;
  
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
  
  // Tasks by priority
  const urgentCount = tasks.filter(t => t.priority === 'urgent' && t.status !== 'completed').length;
  const highCount = tasks.filter(t => t.priority === 'high' && t.status !== 'completed').length;
  const mediumCount = tasks.filter(t => t.priority === 'medium' && t.status !== 'completed').length;
  const lowCount = tasks.filter(t => t.priority === 'low' && t.status !== 'completed').length;
  
  // Tasks completed today
  const today = new Date().toISOString().split('T')[0];
  const completedToday = tasks.filter(t => {
    if (t.status === 'completed' && t.created_at) {
      const taskDate = t.created_at.split('T')[0];
      return taskDate === today;
    }
    return false;
  }).length;

  return (
    <div className="dashboard">
      <h2>📊 Dashboard</h2>
      
      <div className="stats-grid">
        {/* Total Tasks */}
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-info">
            <h3>{totalTasks}</h3>
            <p>Total Tasks</p>
          </div>
        </div>

        {/* Completion Rate */}
        <div className="stat-card highlight">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <h3>{completionRate}%</h3>
            <p>Completion Rate</p>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${completionRate}%` }}></div>
          </div>
        </div>

        {/* Completed Today */}
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-info">
            <h3>{completedToday}</h3>
            <p>Completed Today</p>
          </div>
        </div>

        {/* Pending Tasks */}
        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-info">
            <h3>{todoTasks + inProgressTasks}</h3>
            <p>Pending Tasks</p>
          </div>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="status-breakdown">
        <h3>Task Status</h3>
        <div className="status-bars">
          <div className="status-bar-item">
            <div className="status-label">
              <span>📝 To Do</span>
              <span className="status-count">{todoTasks}</span>
            </div>
            <div className="status-bar">
              <div 
                className="status-bar-fill todo" 
                style={{ width: `${totalTasks > 0 ? (todoTasks / totalTasks) * 100 : 0}%` }}
              ></div>
            </div>
          </div>

          <div className="status-bar-item">
            <div className="status-label">
              <span>🔄 In Progress</span>
              <span className="status-count">{inProgressTasks}</span>
            </div>
            <div className="status-bar">
              <div 
                className="status-bar-fill in-progress" 
                style={{ width: `${totalTasks > 0 ? (inProgressTasks / totalTasks) * 100 : 0}%` }}
              ></div>
            </div>
          </div>

          <div className="status-bar-item">
            <div className="status-label">
              <span>✅ Completed</span>
              <span className="status-count">{completedTasks}</span>
            </div>
            <div className="status-bar">
              <div 
                className="status-bar-fill completed" 
                style={{ width: `${totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Priority Breakdown */}
      <div className="priority-breakdown">
        <h3>Active Tasks by Priority</h3>
        <div className="priority-grid">
          <div className="priority-item urgent">
            <div className="priority-count">{urgentCount}</div>
            <div className="priority-label">🔴 Urgent</div>
          </div>
          <div className="priority-item high">
            <div className="priority-count">{highCount}</div>
            <div className="priority-label">🟠 High</div>
          </div>
          <div className="priority-item medium">
            <div className="priority-count">{mediumCount}</div>
            <div className="priority-label">🟡 Medium</div>
          </div>
          <div className="priority-item low">
            <div className="priority-count">{lowCount}</div>
            <div className="priority-label">🟢 Low</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
