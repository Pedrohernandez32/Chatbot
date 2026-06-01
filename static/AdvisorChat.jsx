import React, { useState, useEffect, useRef } from 'react';
import './advisor.css';

export default function AdvisorChat({ requestId, userName = 'Usuario', onClose }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [advisorInfo, setAdvisorInfo] = useState(null);
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Cargar mensajes iniciales
  useEffect(() => {
    loadMessages();
  }, [requestId]);

  // Auto-scroll a los últimos mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadMessages = async () => {
    try {
      const response = await fetch(`/api/advisor/messages/${requestId}`);
      const data = await response.json();

      if (data.success) {
        setMessages(data.messages);
        setAdvisorInfo(data.request);
      } else {
        setError('No se pudieron cargar los mensajes');
      }
    } catch (err) {
      setError('Error al cargar: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputMessage.trim()) return;

    const messageToSend = inputMessage.trim();
    setInputMessage('');
    setIsTyping(false);

    try {
      const response = await fetch(`/api/advisor/message/${requestId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageToSend })
      });

      if (response.ok) {
        // Recargar mensajes para ver el nuevo
        await loadMessages();
      } else {
        setError('Error al enviar mensaje');
      }
    } catch (err) {
      setError('Error de conexión');
    }
  };

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
    setIsTyping(true);

    // Limpiar timeout anterior
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Esperar 3 segundos sin escribir para marcar como "no escribiendo"
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
    }, 3000);
  };

  if (isLoading) {
    return (
      <div className="advisor-chat-container">
        <div className="loading">⏳ Cargando chat...</div>
      </div>
    );
  }

  return (
    <div className="advisor-chat-container">
      <div className="chat-header">
        <div className="header-info">
          <h3>Chat con Asesor</h3>
          {advisorInfo && (
            <p className="request-topic">📌 {advisorInfo.topic}</p>
          )}
        </div>
        <button className="close-chat-btn" onClick={onClose} title="Cerrar chat">
          ✕
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="no-messages">
            <p>👋 Aún no hay mensajes</p>
            <p>Envía un mensaje para comenzar la conversación</p>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`message ${msg.sender_type === 'advisor' ? 'advisor-msg' : 'user-msg'}`}
              >
                <div className="message-content">
                  <strong className="sender">
                    {msg.sender_type === 'advisor' ? '👤 Asesor' : '👤 Tú'}
                  </strong>
                  <p className="text">{msg.message}</p>
                  <small className="timestamp">
                    {new Date(msg.created_at).toLocaleTimeString()}
                  </small>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="typing-indicator">
                <span>✍️ Escribiendo...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {error && <div className="chat-error">{error}</div>}

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={handleInputChange}
          placeholder="Escribe tu mensaje..."
          maxLength="5000"
          disabled={isLoading}
          className="message-input"
        />
        <button
          type="submit"
          disabled={!inputMessage.trim() || isLoading}
          className="send-btn"
          title="Enviar mensaje"
        >
          📤 Enviar
        </button>
      </form>
    </div>
  );
}
