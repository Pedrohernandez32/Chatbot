import React, { useState, useEffect } from 'react';
import './advisor.css';

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('day'); // day, week, month

  useEffect(() => {
    loadAnalytics();
    const interval = setInterval(loadAnalytics, 10000); // Recargar cada 10 segundos
    return () => clearInterval(interval);
  }, [timeRange]);

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`/api/advisor/analytics?range=${timeRange}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();

      if (data.success) {
        setAnalytics(data.metrics);
        setLoading(false);
      }
    } catch (err) {
      setError('Error al cargar análisis: ' + err.message);
    }
  };

  if (loading) {
    return <div className="analytics-loading">⏳ Cargando análisis...</div>;
  }

  if (!analytics) {
    return <div className="analytics-error">Error al cargar datos</div>;
  }

  // Simular datos para gráficos (en producción, usar Chart.js o Recharts)
  const satisfactionPercentage = Math.round((analytics.customer_satisfaction_avg || 0) / 5 * 100);
  const closureRate = analytics.closed_requests / Math.max(1, analytics.total_requests) * 100;

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h1>📊 Dashboard de Análisis</h1>
        <div className="time-range">
          <button
            className={timeRange === 'day' ? 'active' : ''}
            onClick={() => setTimeRange('day')}
          >
            Hoy
          </button>
          <button
            className={timeRange === 'week' ? 'active' : ''}
            onClick={() => setTimeRange('week')}
          >
            Esta semana
          </button>
          <button
            className={timeRange === 'month' ? 'active' : ''}
            onClick={() => setTimeRange('month')}
          >
            Este mes
          </button>
        </div>
      </div>

      {error && <div className="analytics-error">{error}</div>}

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>📥 Total de Solicitudes</h3>
          <div className="metric-value">{analytics.total_requests}</div>
          <div className="metric-detail">
            {analytics.closed_requests} cerradas · {analytics.total_requests - analytics.closed_requests} pendientes
          </div>
        </div>

        <div className="metric-card">
          <h3>✅ Tasa de Resolución</h3>
          <div className="metric-value">{Math.round(closureRate)}%</div>
          <div className="metric-bar">
            <div className="bar-fill" style={{ width: `${closureRate}%` }}></div>
          </div>
        </div>

        <div className="metric-card">
          <h3>⭐ Satisfacción del Cliente</h3>
          <div className="metric-value">{satisfactionPercentage}%</div>
          <div className="star-rating">
            {[...Array(5)].map((_, i) => (
              <span key={i} className={i < Math.round(analytics.customer_satisfaction_avg || 0) ? 'filled' : ''}>
                ★
              </span>
            ))}
          </div>
        </div>

        <div className="metric-card">
          <h3>⏱️ Tiempo Promedio de Resolución</h3>
          <div className="metric-value">{Math.round(analytics.avg_resolution_time_minutes || 0)}</div>
          <div className="metric-unit">minutos</div>
        </div>

        <div className="metric-card">
          <h3>⏳ Tiempo Promedio de Espera</h3>
          <div className="metric-value">{Math.round(analytics.avg_wait_time_minutes || 0)}</div>
          <div className="metric-unit">minutos</div>
        </div>

        <div className="metric-card">
          <h3>💬 Total de Mensajes</h3>
          <div className="metric-value">{analytics.total_messages}</div>
          <div className="metric-detail">
            {analytics.total_requests > 0 ? (
              `${(analytics.total_messages / analytics.total_requests).toFixed(1)} mensajes/solicitud`
            ) : (
              '0 mensajes/solicitud'
            )}
          </div>
        </div>
      </div>

      <div className="analytics-charts">
        <div className="chart-container">
          <h3>📊 Distribución de Estados</h3>
          <div className="status-distribution">
            {analytics.requests_by_status && Object.entries(analytics.requests_by_status).map(([status, count]) => (
              <div key={status} className="status-item">
                <span className="status-label">
                  {status === 'waiting' && '⏳ Esperando'}
                  {status === 'assigned' && '👤 Asignado'}
                  {status === 'active' && '💬 Activo'}
                  {status === 'closed' && '✅ Cerrado'}
                  {status === 'rated' && '⭐ Calificado'}
                </span>
                <div className="status-bar">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${(count / Math.max(1, analytics.total_requests)) * 100}%`
                    }}
                  ></div>
                </div>
                <span className="status-count">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-container">
          <h3>🔝 Temas Más Consultados</h3>
          <div className="topic-distribution">
            <p className="most-common-topic">
              📌 {analytics.most_common_topic || 'Sin datos'}
            </p>
          </div>
        </div>

        <div className="chart-container">
          <h3>👥 Asesores en Línea</h3>
          <div className="advisors-info">
            <p className="advisor-count">
              <span className="online-badge">{analytics.advisors_online}</span>
              de <span className="total-badge">{analytics.advisors_total}</span> en línea
            </p>
            <div className="availability-bar">
              <div
                className="availability-fill"
                style={{
                  width: `${(analytics.advisors_online / Math.max(1, analytics.advisors_total)) * 100}%`
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div className="analytics-insights">
        <h3>💡 Insights</h3>
        <ul className="insights-list">
          <li>
            {analytics.avg_resolution_time_minutes < 30
              ? '⚡ Excelente tiempo de resolución'
              : '⏱️ Considera mejorar tiempo de respuesta'}
          </li>
          <li>
            {analytics.customer_satisfaction_avg >= 4
              ? '😊 Alta satisfacción del cliente'
              : '📈 Hay oportunidad de mejorar'}
          </li>
          <li>
            {analytics.advisors_online > 0
              ? `✅ Tienes ${analytics.advisors_online} asesor${analytics.advisors_online > 1 ? 'es' : ''} disponible${analytics.advisors_online > 1 ? 's' : ''}`
              : '⚠️ No hay asesores en línea'}
          </li>
        </ul>
      </div>
    </div>
  );
}
