import React, { useState } from 'react';
import './advisor.css';

export default function AdvisorRequest({ onRequestCreated }) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    topic: 'Becas'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/advisor/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`✅ Solicitud creada. ${data.message}`);
        setFormData({ name: '', email: '', phone: '', topic: 'Becas' });

        // Llamar callback con datos de la solicitud
        if (onRequestCreated) {
          onRequestCreated(data);
        }

        // Cerrar modal después de 2 segundos
        setTimeout(() => {
          setIsOpen(false);
          setSuccess(null);
        }, 2000);
      } else {
        setError(data.error || 'Error al crear solicitud');
      }
    } catch (err) {
      setError('Error de conexión: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        className="btn-advisor-main"
        onClick={() => setIsOpen(true)}
        title="Conecta con un asesor de la universidad"
      >
        <span className="icon">📞</span>
        <span className="text">Hablar con Asesor</span>
      </button>

      {isOpen && (
        <div className="advisor-modal-overlay" onClick={() => setIsOpen(false)}>
          <div className="advisor-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Solicitar Asesor</h2>
              <button
                className="close-btn"
                onClick={() => setIsOpen(false)}
                aria-label="Cerrar"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="advisor-form">
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

              <div className="form-group">
                <label htmlFor="topic">Tema de consulta *</label>
                <select
                  id="topic"
                  name="topic"
                  value={formData.topic}
                  onChange={handleChange}
                  disabled={loading}
                >
                  <option value="Becas">💰 Becas</option>
                  <option value="Admisiones">📝 Admisiones</option>
                  <option value="Campus">🏫 Campus</option>
                  <option value="Horarios">⏰ Horarios</option>
                  <option value="Otra consulta">❓ Otra consulta</option>
                </select>
              </div>

              {error && <div className="form-error">{error}</div>}
              {success && <div className="form-success">{success}</div>}

              <button
                type="submit"
                className="submit-btn"
                disabled={loading}
              >
                {loading ? '⏳ Enviando...' : '📞 Solicitar Asesor'}
              </button>

              <p className="form-help">
                Un asesor se conectará contigo en breve. Tiempo estimado: 5-10 minutos.
              </p>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
