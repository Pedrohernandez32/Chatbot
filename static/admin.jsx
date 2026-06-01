/* ============================================================
   Admin Panel — Gestión completa del sistema
   ============================================================ */
const { useState, useEffect, useCallback } = React;

const ADMIN_TABS = [
  { id: 'dashboard', label: 'Dashboard', Ic: IconShield },
  { id: 'usuarios', label: 'Usuarios', Ic: IconUsers },
  { id: 'conversaciones', label: 'Conversaciones', Ic: IconChat },
  { id: 'preguntas', label: 'Preguntas desconocidas', Ic: IconHelp },
  { id: 'respuestas', label: 'Respuestas aprendidas', Ic: IconCheck },
  { id: 'contenido', label: 'Contenido', Ic: IconDoc },
];

function AdminDashboard() {
  const [stats, setStats] = useState({
    usuarios: 0,
    conversaciones: 0,
    preguntasDesconocidas: 0,
    respuestasAprendidas: 0,
  });

  useEffect(() => {
    // Cargar estadísticas
    Promise.all([
      fetch('/api/admin/users').then(r => r.json()),
      fetch('/api/admin/conversations').then(r => r.json()),
      fetch('/api/admin/unknown').then(r => r.json()),
      fetch('/api/admin/learn').then(r => r.json()),
    ]).then(([users, convs, unknown, learned]) => {
      setStats({
        usuarios: users.length || 0,
        conversaciones: convs.length || 0,
        preguntasDesconocidas: unknown.questions?.length || 0,
        respuestasAprendidas: learned.responses?.length || 0,
      });
    }).catch(e => console.error('Error cargando estadísticas:', e));
  }, []);

  return (
    <div className="admin-section">
      <h2>📊 Dashboard</h2>
      <div className="admin-grid">
        <div className="stat-card">
          <div className="stat-icon"><IconUsers s={32} /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.usuarios}</div>
            <div className="stat-label">Usuarios registrados</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><IconChat s={32} /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.conversaciones}</div>
            <div className="stat-label">Conversaciones</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><IconHelp s={32} /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.preguntasDesconocidas}</div>
            <div className="stat-label">Preguntas desconocidas</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><IconCheck s={32} /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.respuestasAprendidas}</div>
            <div className="stat-label">Respuestas aprendidas</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AdminUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/admin/users')
      .then(r => r.json())
      .then(data => {
        setUsuarios(data || []);
        setLoading(false);
      })
      .catch(e => {
        console.error('Error:', e);
        setLoading(false);
      });
  }, []);

  return (
    <div className="admin-section">
      <h2>👥 Gestión de Usuarios</h2>
      {loading ? (
        <p>Cargando usuarios...</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Fecha creación</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((u, i) => (
              <tr key={i}>
                <td>{u.id}</td>
                <td><strong>{u.username}</strong></td>
                <td>{u.email}</td>
                <td>{u.is_admin ? '👨‍💼 Admin' : '👤 Usuario'}</td>
                <td>{new Date(u.created_at).toLocaleDateString('es-CO')}</td>
                <td><button className="btn btn-small">Editar</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function AdminConversaciones() {
  const [conversaciones, setConversaciones] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/admin/conversations')
      .then(r => r.json())
      .then(data => {
        setConversaciones(data || []);
        setLoading(false);
      })
      .catch(e => {
        console.error('Error:', e);
        setLoading(false);
      });
  }, []);

  return (
    <div className="admin-section">
      <h2>💬 Conversaciones recientes</h2>
      {loading ? (
        <p>Cargando conversaciones...</p>
      ) : conversaciones.length === 0 ? (
        <p>Sin conversaciones registradas</p>
      ) : (
        <div className="conversations-list">
          {conversaciones.slice(0, 20).map((c, i) => (
            <div key={i} className="conversation-item">
              <div className="conv-user">👤 {c.user_id || 'Anónimo'}</div>
              <div className="conv-message">
                <strong>P:</strong> {c.user_message?.substring(0, 80)}...
              </div>
              <div className="conv-response">
                <strong>R:</strong> {c.response?.substring(0, 80)}...
              </div>
              <div className="conv-vote">{c.vote ? '👍' : c.vote === false ? '👎' : '⏳'}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AdminPreguntas() {
  const [preguntas, setPreguntas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newAnswer, setNewAnswer] = useState('');
  const [selectedQ, setSelectedQ] = useState(null);

  useEffect(() => {
    fetch('/api/admin/unknown')
      .then(r => r.json())
      .then(data => {
        setPreguntas(data.questions || []);
        setLoading(false);
      });
  }, []);

  const handleSaveAnswer = async (question) => {
    if (!newAnswer.trim()) return;
    try {
      const res = await fetch('/api/admin/learn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          answer: newAnswer,
          keywords: question.toLowerCase(),
        }),
      });
      if (res.ok) {
        setPreguntas(preguntas.filter(p => p !== question));
        setNewAnswer('');
        setSelectedQ(null);
        alert('✅ Respuesta guardada');
      }
    } catch (e) {
      alert('❌ Error al guardar');
    }
  };

  return (
    <div className="admin-section">
      <h2>❓ Preguntas desconocidas ({preguntas.length})</h2>
      {loading ? (
        <p>Cargando preguntas...</p>
      ) : preguntas.length === 0 ? (
        <p>✅ Sin preguntas desconocidas - ¡Excelente!</p>
      ) : (
        <div className="questions-list">
          {preguntas.map((q, i) => (
            <div key={i} className="question-item">
              <div className="q-text">
                <strong>Q:</strong> {q}
              </div>
              <div className="q-actions">
                <button
                  className="btn btn-small"
                  onClick={() => setSelectedQ(selectedQ === q ? null : q)}
                >
                  {selectedQ === q ? 'Cancelar' : 'Responder'}
                </button>
              </div>
              {selectedQ === q && (
                <div className="q-answer-form">
                  <textarea
                    value={newAnswer}
                    onChange={(e) => setNewAnswer(e.target.value)}
                    placeholder="Escribe la respuesta..."
                    rows="3"
                  />
                  <button
                    className="btn btn-primary"
                    onClick={() => handleSaveAnswer(q)}
                  >
                    Guardar respuesta
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AdminRespuestas() {
  const [respuestas, setRespuestas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/admin/learn')
      .then(r => r.json())
      .then(data => {
        setRespuestas(data.responses || []);
        setLoading(false);
      });
  }, []);

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar esta respuesta?')) return;
    try {
      await fetch(`/api/admin/learn/${id}`, { method: 'DELETE' });
      setRespuestas(respuestas.filter(r => r.id !== id));
      alert('✅ Respuesta eliminada');
    } catch {
      alert('❌ Error al eliminar');
    }
  };

  return (
    <div className="admin-section">
      <h2>📚 Respuestas aprendidas ({respuestas.length})</h2>
      {loading ? (
        <p>Cargando respuestas...</p>
      ) : respuestas.length === 0 ? (
        <p>Sin respuestas aprendidas aún</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Keywords</th>
              <th>Respuesta</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {respuestas.map((r, i) => (
              <tr key={i}>
                <td><code>{r.keywords}</code></td>
                <td>{r.response?.substring(0, 60)}...</td>
                <td>
                  <button
                    className="btn btn-small btn-danger"
                    onClick={() => handleDelete(r.id)}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function AdminContenido() {
  return (
    <div className="admin-section">
      <h2>📝 Editor de Contenido</h2>
      <div className="content-sections">
        <div className="content-card">
          <h3>🎓 Carreras</h3>
          <p>Editar información de programas académicos</p>
          <button className="btn btn-primary">Editar carreras</button>
        </div>
        <div className="content-card">
          <h3>💰 Becas</h3>
          <p>Gestionar información de becas y financiación</p>
          <button className="btn btn-primary">Editar becas</button>
        </div>
        <div className="content-card">
          <h3>🏢 Campus</h3>
          <p>Actualizar detalles e imágenes del campus</p>
          <button className="btn btn-primary">Editar campus</button>
        </div>
        <div className="content-card">
          <h3>📱 Contacto</h3>
          <p>Información de contacto y ubicaciones</p>
          <button className="btn btn-primary">Editar contacto</button>
        </div>
      </div>
    </div>
  );
}

function AdminPanel({ user, logout }) {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderTab = () => {
    switch (activeTab) {
      case 'dashboard': return <AdminDashboard />;
      case 'usuarios': return <AdminUsuarios />;
      case 'conversaciones': return <AdminConversaciones />;
      case 'preguntas': return <AdminPreguntas />;
      case 'respuestas': return <AdminRespuestas />;
      case 'contenido': return <AdminContenido />;
      default: return <AdminDashboard />;
    }
  };

  return (
    <section className="sec admin-panel" id="admin-panel">
      <div className="wrap">
        <div className="admin-header">
          <div className="admin-info">
            <h1>🛡️ Panel Administrativo</h1>
            <p>Bienvenido, {user?.name || 'Administrador'}</p>
          </div>
          <button className="btn btn-danger" onClick={logout}>
            Cerrar sesión
          </button>
        </div>

        <div className="admin-tabs">
          {ADMIN_TABS.map((tab) => (
            <button
              key={tab.id}
              className={'admin-tab' + (activeTab === tab.id ? ' active' : '')}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.Ic s={18} /> {tab.label}
            </button>
          ))}
        </div>

        <div className="admin-content">
          {renderTab()}
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { AdminPanel });
