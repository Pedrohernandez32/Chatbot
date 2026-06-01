/**
 * Componente de Solicitud de Asesor - Integrado en la UI Principal
 * Versión mejorada para uso en app.jsx
 */

import React, { useState, useEffect } from 'react';

export default function AdvisorRequestIntegrado({ onRequestCreated, theme = 'light' }) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [step, setStep] = useState('form'); // form, waiting, chat
  const [requestData, setRequestData] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    topic: 'Becas'
  });

  // Auto-cerrar mensaje de éxito después de 3 segundos
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/advisor/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setRequestData(data);
        setSuccess(`✅ ${data.message}`);
        setStep('waiting');

        if (onRequestCreated) {
          onRequestCreated(data);
        }

        // Auto-limpiar después de 3 segundos
        setTimeout(() => {
          setFormData({ name: '', email: '', phone: '', topic: 'Becas' });
        }, 3000);
      } else {
        setError(data.error || 'Error al crear solicitud');
      }
    } catch (err) {
      setError('Error de conexión: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setStep('form');
    setSuccess(null);
    setError(null);
    setRequestData(null);
  };

  const topics = [
    { value: 'Becas', label: '💰 Becas y Financiamiento' },
    { value: 'Admisiones', label: '📝 Admisiones e Inscripción' },
    { value: 'Campus', label: '🏫 Campus e Infraestructura' },
    { value: 'Horarios', label: '⏰ Horarios y Calendario' },
    { value: 'Carreras', label: '🎓 Programas y Carreras' },
    { value: 'Otra consulta', label: '❓ Otra consulta' }
  ];

  return (
    <>
      {/* Botón flotante o en línea */}
      <button
        className={`advisor-btn ${theme}`}
        onClick={() => setIsOpen(true)}
        title="Conecta con un asesor en línea"
        aria-label="Hablar con Asesor"
      >
        <span className="advisor-icon">📞</span>
        <span className="advisor-text">Hablar con Asesor</span>
        <span className="advisor-badge">En vivo</span>
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="advisor-overlay" onClick={handleClose}>
          <div className="advisor-modal" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="advisor-modal-header">
              <div className="header-content">
                <h2>
                  <span className="icon">👨‍💼</span>
                  Asesor en Línea
                </h2>
                <p className="subtitle">Conecta con un profesional de UdeMedellín</p>
              </div>
              <button
                className="close-button"
                onClick={handleClose}
                aria-label="Cerrar"
              >
                ✕
              </button>
            </div>

            {/* Contenido según paso */}
            {step === 'form' ? (
              <>
                {/* Formulario */}
                <form onSubmit={handleSubmit} className="advisor-form">
                  <div className="form-grid">
                    <div className="form-group">
                      <label htmlFor="name">Nombre completo *</label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Juan García"
                        required
                        disabled={loading}
                        autoFocus
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="email">Correo electrónico *</label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="tu@email.com"
                        required
                        disabled={loading}
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="phone">Teléfono (opcional)</label>
                      <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        placeholder="+57 300 1234567"
                        disabled={loading}
                      />
                    </div>

                    <div className="form-group full">
                      <label htmlFor="topic">Tema de consulta *</label>
                      <select
                        id="topic"
                        name="topic"
                        value={formData.topic}
                        onChange={handleChange}
                        disabled={loading}
                      >
                        {topics.map(t => (
                          <option key={t.value} value={t.value}>{t.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Mensajes de error/éxito */}
                  {error && (
                    <div className="form-message error">
                      <span>❌</span>
                      {error}
                    </div>
                  )}
                  {success && (
                    <div className="form-message success">
                      <span>✅</span>
                      {success}
                    </div>
                  )}

                  {/* Botón submit */}
                  <button
                    type="submit"
                    className="submit-button"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner">⏳</span> Conectando...
                      </>
                    ) : (
                      <>
                        <span>📞</span> Solicitar Asesor
                      </>
                    )}
                  </button>

                  {/* Info de ayuda */}
                  <div className="form-help">
                    <p>
                      ✨ Un asesor se conectará contigo en breve.
                      <br />
                      Tiempo estimado: <strong>5-15 minutos</strong>
                    </p>
                  </div>
                </form>
              </>
            ) : (
              <>
                {/* Pantalla de espera */}
                <div className="waiting-screen">
                  <div className="waiting-content">
                    <div className="loading-animation">
                      <div className="spinner-circle"></div>
                      <p className="waiting-text">Conectando con un asesor...</p>
                    </div>

                    {requestData && (
                      <div className="request-info">
                        <p className="request-id">
                          <strong>ID Solicitud:</strong> #{requestData.request_id}
                        </p>
                        <p className="queue-position">
                          <strong>Tu posición en la cola:</strong> #{requestData.position_in_queue}
                        </p>
                        <p className="wait-time">
                          <strong>Tiempo estimado:</strong> {requestData.estimated_wait_minutes} minutos
                        </p>
                        <p className="advisors-available">
                          <strong>Asesores disponibles:</strong> {requestData.advisors_available}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Botón para cerrar */}
                  <button
                    type="button"
                    className="close-modal-button"
                    onClick={handleClose}
                  >
                    Cerrar ventana
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <style>{`
        .advisor-btn {
          position: relative;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 24px;
          background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(30, 64, 175, 0.3);
          z-index: 100;
        }

        .advisor-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(30, 64, 175, 0.4);
        }

        .advisor-btn .advisor-icon {
          font-size: 18px;
        }

        .advisor-btn .advisor-badge {
          position: absolute;
          top: -8px;
          right: 0;
          background: #16a34a;
          color: white;
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 10px;
          font-weight: 700;
        }

        @media (max-width: 768px) {
          .advisor-btn .advisor-text {
            display: none;
          }
        }

        .advisor-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .advisor-modal {
          background: white;
          border-radius: 12px;
          box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
          width: 90%;
          max-width: 500px;
          max-height: 90vh;
          overflow: auto;
          animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
          from { transform: translateY(30px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        .advisor-modal-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 24px;
          background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
          color: white;
          border-radius: 12px 12px 0 0;
        }

        .header-content h2 {
          margin: 0 0 8px 0;
          font-size: 22px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .header-content .subtitle {
          margin: 0;
          font-size: 13px;
          opacity: 0.9;
        }

        .close-button {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          font-size: 24px;
          width: 36px;
          height: 36px;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .close-button:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .advisor-form {
          padding: 24px;
        }

        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin-bottom: 16px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
        }

        .form-group.full {
          grid-column: 1 / -1;
        }

        .form-group label {
          font-weight: 600;
          margin-bottom: 8px;
          color: #374151;
          font-size: 14px;
        }

        .form-group input,
        .form-group select {
          padding: 12px;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-size: 14px;
          font-family: inherit;
          transition: all 0.2s;
        }

        .form-group input:focus,
        .form-group select:focus {
          outline: none;
          border-color: #1e40af;
          box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        }

        .form-message {
          padding: 12px;
          border-radius: 6px;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
        }

        .form-message.error {
          background: #fee2e2;
          color: #dc2626;
        }

        .form-message.success {
          background: #dcfce7;
          color: #16a34a;
        }

        .submit-button {
          width: 100%;
          padding: 14px;
          background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          font-size: 16px;
          cursor: pointer;
          transition: all 0.3s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .submit-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(30, 64, 175, 0.3);
        }

        .submit-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .form-help {
          margin-top: 16px;
          padding: 12px;
          background: #f3f4f6;
          border-radius: 6px;
          font-size: 13px;
          color: #6b7280;
          text-align: center;
        }

        .form-help p {
          margin: 0;
        }

        .waiting-screen {
          padding: 40px 24px;
          text-align: center;
        }

        .waiting-content {
          margin-bottom: 24px;
        }

        .loading-animation {
          margin-bottom: 24px;
        }

        .spinner-circle {
          width: 50px;
          height: 50px;
          border: 4px solid #f3f4f6;
          border-top-color: #1e40af;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .waiting-text {
          margin: 16px 0;
          color: #374151;
          font-weight: 500;
        }

        .request-info {
          background: #f9fafb;
          border-left: 4px solid #1e40af;
          padding: 16px;
          border-radius: 6px;
          text-align: left;
          margin: 16px 0;
        }

        .request-info p {
          margin: 8px 0;
          font-size: 14px;
          color: #374151;
        }

        .close-modal-button {
          padding: 12px 24px;
          background: #f3f4f6;
          color: #374151;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.2s;
        }

        .close-modal-button:hover {
          background: #e5e7eb;
        }

        @media (max-width: 600px) {
          .form-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </>
  );
}
