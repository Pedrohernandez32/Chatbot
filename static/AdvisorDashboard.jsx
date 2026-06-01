import React, { useState, useEffect } from 'react';
import './advisor.css';

export default function AdvisorDashboard({ advisorId }) {
  const [requests, setRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('online');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadRequests();
    loadStats();
    const interval = setInterval(() => {
      loadRequests();
      loadStats();
    }, 5000); // Recargar cada 5 segundos

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedRequest) {
      loadMessages(selectedRequest.id);
    }
  }, [selectedRequest]);

  const loadRequests = async () => {
    try {
      const response = await fetch('/api/advisor/requests', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();

      if (data.success) {
        setRequests(data.requests);
        setLoading(false);
      }
    } catch (err) {
      setError('Error al cargar solicitudes: ' + err.message);
    }
  };

  const loadMessages = async (requestId) => {
    try {
      const response = await fetch(`/api/advisor/messages/${requestId}`);
      const data = await response.json();

      if (data.success) {
        setMessages(data.messages);
      }
    } catch (err) {
      console.error('Error al cargar mensajes:', err);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/advisor/analytics', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();

      if (data.success) {
        setStats(data.metrics);
      }
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      const response = await fetch('/api/advisor/status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        setStatus(newStatus);
      }
    } catch (err) {
      setError('Error al cambiar estado');
    }
  };

  const handleAssignRequest = async (requestId) => {
    try {
      const response = await fetch(`/api/advisor/assign/${requestId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        setSelectedRequest(requests.find(r => r.id === requestId));
        await loadRequests();
      }
    } catch (err) {
      setError('Error al asignar solicitud');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!newMessage.trim() || !selectedRequest) return;

    try {
      const response = await fetch(`/api/advisor/message/${selectedRequest.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: newMessage })
      });

      if (response.ok) {
        setNewMessage('');
        await loadMessages(selectedRequest.id);
      }
    } catch (err) {
      setError('Error al enviar mensaje');
    }
  };

  const handleCloseRequest = async () => {
    if (!selectedRequest) return;

    try {
      const response = await fetch(`/api/advisor/close/${selectedRequest.id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        setSelectedRequest(null);
        await loadRequests();
      }
    } catch (err) {
      setError('Error al cerrar solicitud');
    }
  };

  return (
    <div className="advisor-dashboard">
      <div className="dashboard-header">
        <h1>📊 Panel de Asesores</h1>
        <div className="status-controls">
          <label>Estado:</label>
          <select value={status} onChange={(e) => handleStatusChange(e.target.value)}>
            <option value="online">🟢 En línea</option>
            <option value="away">🟡 Ausente</option>
            <option value="busy">🔴 Ocupado</option>
            <option value="offline">⚫ Offline</option>
          </select>
        </div>
      </div>

      {stats && (
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Solicitudes Activas</h3>
            <p className="stat-value">{stats.active_requests || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Calificación Promedio</h3>
            <p className="stat-value">⭐ {(stats.avg_rating || 0).toFixed(1)}</p>
          </div>
          <div className="stat-card">
            <h3>Tiempo Promedio Resolución</h3>
            <p className="stat-value">{Math.round(stats.avg_resolution_time_minutes || 0)} min</p>
          </div>
          <div className="stat-card">
            <h3>Score de Rendimiento</h3>
            <p className="stat-value">{Math.round(stats.performance_score || 0)}/100</p>
          </div>
        </div>
      )}

      {error && <div className="dashboard-error">{error}</div>}

      <div className="dashboard-content">
        <div className="requests-list">
          <h2>Solicitudes Pendientes ({requests.length})</h2>

          {loading ? (
            <div className="loading">⏳ Cargando...</div>
          ) : requests.length === 0 ? (
            <div className="no-requests">
              <p>✅ No hay solicitudes pendientes</p>
            </div>
          ) : (
            <ul className="requests">
              {requests.map((req) => (
                <li
                  key={req.id}
                  className={`request-item ${selectedRequest?.id === req.id ? 'active' : ''}`}
                  onClick={() => setSelectedRequest(req)}
                >
                  <div className="request-header">
                    <strong>{req.name}</strong>
                    <span className={`status ${req.status}`}>
                      {req.status === 'waiting' && '⏳ Esperando'}
                      {req.status === 'assigned' && '👤 Asignado'}
                      {req.status === 'active' && '💬 Activo'}
                    </span>
                  </div>
                  <p className="topic">📌 {req.topic}</p>
                  <p className="email">📧 {req.email}</p>
                  {req.status === 'waiting' && (
                    <button
                      className="assign-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAssignRequest(req.id);
                      }}
                    >
                      Asignar a Mí
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="chat-panel">
          {selectedRequest ? (
            <>
              <div className="chat-header">
                <h2>{selectedRequest.name}</h2>
                <p>{selectedRequest.topic}</p>
              </div>

              <div className="messages-container">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`message ${msg.sender_type === 'advisor' ? 'advisor' : 'user'}`}
                  >
                    <strong>{msg.sender_type === 'advisor' ? 'Tú' : selectedRequest.name}</strong>
                    <p>{msg.message}</p>
                    <small>{new Date(msg.created_at).toLocaleTimeString()}</small>
                  </div>
                ))}
              </div>

              <form onSubmit={handleSendMessage} className="message-form">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Escribe tu respuesta..."
                  maxLength="5000"
                />
                <button type="submit" disabled={!newMessage.trim()}>
                  📤 Enviar
                </button>
              </form>

              <button className="close-request-btn" onClick={handleCloseRequest}>
                ✓ Cerrar Solicitud
              </button>
            </>
          ) : (
            <div className="no-selection">
              <p>👈 Selecciona una solicitud para ver el chat</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
