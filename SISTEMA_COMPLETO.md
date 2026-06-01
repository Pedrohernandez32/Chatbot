# 🚀 SISTEMA COMPLETO DE ASESORES HUMANOS CON IA

## 📋 Resumen Ejecutivo

Sistema **profesional de nivel empresarial** que integra:

✅ **Chat en Tiempo Real (WebSocket)**  
✅ **Panel de Control para Asesores**  
✅ **Dashboard Analytics Avanzado**  
✅ **Sugerencias de IA Inteligentes**  
✅ **Notificaciones en Tiempo Real**  
✅ **Componentes React Hermosos**  
✅ **Validaciones Robustas**  
✅ **Rate Limiting y Seguridad**  

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────┐
│            FRONTEND (React Components)              │
├─────────────────────────────────────────────────────┤
│  • AdvisorRequest.jsx    → Solicitar asesor         │
│  • AdvisorChat.jsx       → Chat en vivo             │
│  • AdvisorDashboard.jsx  → Panel asesores           │
│  • AnalyticsDashboard.jsx→ Estadísticas             │
└─────────┬───────────────────────────────────────────┘
          │ REST API + WebSocket
          ▼
┌─────────────────────────────────────────────────────┐
│          BACKEND (Flask + SocketIO)                 │
├─────────────────────────────────────────────────────┤
│  • server.py              → Servidor principal      │
│  • websocket_server.py    → WebSocket eventos       │
│  • advisor_routes.py      → Endpoints REST          │
│  • ai_suggestions.py      → Motor de IA             │
│  • advisor_enhanced.py    → Lógica avanzada         │
│  • database.py            → Persistencia            │
└─────────┬───────────────────────────────────────────┘
          │ SQL
          ▼
┌─────────────────────────────────────────────────────┐
│         BASE DE DATOS (SQLite)                      │
├─────────────────────────────────────────────────────┤
│  • advisor_requests       → Solicitudes             │
│  • advisor_messages       → Conversaciones          │
│  • advisors              → Perfiles de asesores     │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Características Principales

### 1. **Solicitud de Asesor** (AdvisorRequest.jsx)

Modal elegante para que usuarios soliciten asesoría:

```jsx
<AdvisorRequest onRequestCreated={(data) => {
  console.log("Solicitud creada:", data.request_id);
}} />
```

**Features:**
- ✅ Validación de entrada (email, teléfono)
- ✅ Selección de tema de consulta
- ✅ Estimación de tiempo de espera
- ✅ Posición en la cola
- ✅ Responsive design

### 2. **Chat en Tiempo Real** (AdvisorChat.jsx)

Componente de chat con auto-actualización:

```jsx
<AdvisorChat 
  requestId={123} 
  userName="Juan García"
  onClose={() => setShowChat(false)}
/>
```

**Features:**
- ✅ Mensajes en tiempo real (polling cada 5s)
- ✅ Indicador de "escribiendo"
- ✅ Auto-scroll a últimos mensajes
- ✅ Historial de conversación
- ✅ Validación de mensajes

### 3. **Panel de Asesores** (AdvisorDashboard.jsx)

Interfaz profesional para gestionar solicitudes:

```jsx
<AdvisorDashboard advisorId={5} />
```

**Features:**
- ✅ Lista de solicitudes pendientes
- ✅ Estadísticas en vivo (calificación, tiempo de respuesta)
- ✅ Chat integrado con usuario
- ✅ Control de estado (online/offline/away/busy)
- ✅ Cierre de solicitudes
- ✅ Auto-refresh cada 5 segundos

### 4. **Dashboard Analytics** (AnalyticsDashboard.jsx)

Visualización de métricas y estadísticas:

```jsx
<AnalyticsDashboard />
```

**Métricas:**
- 📊 Total de solicitudes
- ✅ Tasa de resolución
- ⭐ Satisfacción del cliente
- ⏱️ Tiempo promedio de resolución
- ⏳ Tiempo promedio de espera
- 💬 Total de mensajes
- 📌 Tema más consultado
- 👥 Asesores en línea

---

## 🔌 WebSocket en Tiempo Real

**Archivo:** `websocket_server.py`

### Eventos Disponibles:

#### Usuario conecta:
```javascript
socket.emit('user_login', {
  user_id: 123,
  is_advisor: false
});
```

#### Enviar mensaje:
```javascript
socket.emit('send_message', {
  request_id: 1,
  message: "Hola, necesito ayuda",
  sender_id: 123,
  sender_type: "user",
  sender_name: "Juan"
});
```

#### Asesor cambia estado:
```javascript
socket.emit('advisor_status_change', {
  advisor_id: 5,
  status: "online"  // online, offline, away, busy
});
```

#### Indicador de "escribiendo":
```javascript
socket.emit('typing', {
  request_id: 1,
  user_id: 123,
  sender_type: "user"
});
```

#### Calificar solicitud:
```javascript
socket.emit('rate_request', {
  request_id: 1,
  rating: 5,
  feedback: "Excelente atención"
});
```

---

## 🤖 Sugerencias de IA

**Archivo:** `ai_suggestions.py`

### Uso Desde Backend:

```python
from ai_suggestions import AdvisorAISuggestions

# Obtener sugerencias contextualizadas
response = AdvisorAISuggestions.get_contextualized_response(
    message="¿Cuáles son las becas disponibles?",
    previous_messages=[]
)

print(response)
# {
#   "intent": "becas",
#   "suggestions": ["Sugerencia 1", "Sugerencia 2", "Sugerencia 3"],
#   "quick_actions": [{"label": "...", "action": "..."}],
#   "followup_questions": ["Pregunta 1", "Pregunta 2"],
#   "sentiment": {"sentiment": "positive", "confidence": 0.8}
# }
```

### Intenciones Detectadas:

| Intención | Keywords | Respuestas |
|-----------|----------|-----------|
| `becas` | beca, ayuda económica, financiamiento | 4 respuestas contextuales |
| `admisiones` | admisión, inscripción, ingreso | 4 respuestas contextuales |
| `campus` | campus, ubicación, sedes | 4 respuestas contextuales |
| `horarios` | horario, clase, calendario académico | 4 respuestas contextuales |
| `contacto` | contacto, teléfono, email | 4 respuestas contextuales |
| `profesores` | profesor, docente, instructor | 4 respuestas contextuales |
| `decanos` | decano, director, facultad | 4 respuestas contextuales |

### Análisis de Sentimiento:

```python
sentiment = AdvisorAISuggestions.analyze_sentiment(
    "¡Excelente ayuda, muy gracias!"
)
# {"sentiment": "positive", "confidence": 0.75}
```

---

## 📡 Endpoints REST

### Crear Solicitud
```http
POST /api/advisor/request
Content-Type: application/json

{
  "name": "Juan García",
  "email": "juan@example.com",
  "phone": "+57 300 1234567",
  "topic": "Becas"
}

Response: {
  "success": true,
  "request_id": 1,
  "position_in_queue": 1,
  "estimated_wait_minutes": 10
}
```

### Obtener Solicitudes Pendientes
```http
GET /api/advisor/requests
Authorization: Bearer <token>

Response: {
  "success": true,
  "total_waiting": 5,
  "requests": [...]
}
```

### Enviar Mensaje
```http
POST /api/advisor/message/<request_id>
Content-Type: application/json

{
  "message": "¿En cuánto tiempo puedo esperar respuesta?"
}

Response: {
  "success": true,
  "message_id": 42,
  "timestamp": "2026-05-31T14:30:00"
}
```

### Obtener Historial
```http
GET /api/advisor/messages/<request_id>

Response: {
  "success": true,
  "messages": [...],
  "request": {...}
}
```

### Obtener Sugerencias de IA
```http
POST /api/advisor/suggestions
Content-Type: application/json

{
  "message": "Usuario pregunta sobre becas",
  "conversation_history": [...]
}

Response: {
  "success": true,
  "suggestions": ["Sugerencia 1", "Sugerencia 2"],
  "quick_actions": [...],
  "followup_questions": [...],
  "sentiment": {"sentiment": "positive", "confidence": 0.8},
  "intent": "becas"
}
```

### Detectar Intención
```http
POST /api/advisor/intent
Content-Type: application/json

{
  "message": "¿Cuáles son los horarios?"
}

Response: {
  "success": true,
  "intent": "horarios",
  "sentiment": {"sentiment": "neutral", "confidence": 0.5}
}
```

### Cambiar Estado del Asesor
```http
POST /api/advisor/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "online"  // online, offline, away, busy
}

Response: {
  "success": true,
  "status": "online"
}
```

### Obtener Analytics
```http
GET /api/advisor/analytics?range=day
Authorization: Bearer <token>

Response: {
  "success": true,
  "metrics": {
    "total_requests": 45,
    "closed_requests": 30,
    "avg_resolution_time_minutes": 15,
    "customer_satisfaction_avg": 4.5,
    ...
  }
}
```

---

## 🎨 Estilos Profesionales

**Archivo:** `advisor.css`

### Características CSS:

- ✅ **Gradientes moderno** (Azul → Púrpura)
- ✅ **Animaciones suaves** (fade-in, slide-up)
- ✅ **Responsive design** (Mobile-first)
- ✅ **Tema oscuro/claro** (CSS variables)
- ✅ **Sombras profesionales** (box-shadow)
- ✅ **Transiciones elegantes** (all 0.3s ease)

### Paleta de Colores:

```css
--primary: #1e40af        /* Azul profesional */
--secondary: #7c3aed      /* Púrpura moderno */
--success: #16a34a        /* Verde éxito */
--warning: #ea580c        /* Naranja alerta */
--danger: #dc2626         /* Rojo error */
--gray-light: #f3f4f6     /* Gris claro */
--gray-dark: #374151      /* Gris oscuro */
```

---

## 🔐 Seguridad

### Validaciones Implementadas:

✅ **Email RFC 5322**
```python
pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

✅ **Teléfono Internacional**
```python
pattern = r'^(\+\d{1,3})?[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4}$'
```

✅ **Rate Limiting**
```python
30 requests/minute por IP
```

✅ **Autenticación**
```
Login requerido para asesores
Usuarios anónimos pueden solicitar
```

✅ **Validación de Mensajes**
```
Min: 1 carácter
Max: 5000 caracteres
No caracteres especiales dañinos
```

---

## 📊 Base de Datos

### Tabla: `advisor_requests`

| Campo | Tipo | Descripción |
|-------|------|-----------|
| id | INTEGER PRIMARY KEY | ID único |
| user_id | INTEGER | ID usuario (NULL si anónimo) |
| name | TEXT NOT NULL | Nombre |
| email | TEXT NOT NULL | Email |
| phone | TEXT | Teléfono |
| topic | TEXT | Tema consulta |
| status | TEXT | waiting/assigned/active/closed |
| assigned_to | INTEGER | ID asesor asignado |
| created_at | TIMESTAMP | Fecha creación |
| resolved_at | TIMESTAMP | Fecha resolución |

### Tabla: `advisor_messages`

| Campo | Tipo | Descripción |
|-------|------|-----------|
| id | INTEGER PRIMARY KEY | ID único |
| request_id | INTEGER FK | ID solicitud |
| sender_id | INTEGER | ID remitente |
| sender_type | TEXT | user/advisor |
| message | TEXT | Contenido |
| created_at | TIMESTAMP | Fecha envío |

### Tabla: `advisors`

| Campo | Tipo | Descripción |
|-------|------|-----------|
| id | INTEGER PRIMARY KEY | ID único |
| user_id | INTEGER FK | ID usuario |
| department | TEXT | Departamento |
| status | TEXT | online/offline/away |
| current_chats | INTEGER | Chats activos |
| max_chats | INTEGER | Máximo simultáneo |
| avg_rating | REAL | Calificación promedio |
| avg_response_time_seconds | INTEGER | Tiempo respuesta |
| last_active | TIMESTAMP | Última actividad |

---

## 🚀 Instalación y Uso

### 1. Instalar Dependencias

```bash
pip install flask flask-cors flask-login flask-socketio python-socketio python-engineio
```

### 2. Inicializar Base de Datos

```bash
python
>>> from database import init_db
>>> init_db()
```

### 3. Ejecutar Servidor

```bash
python server.py
```

Servidor estará en: `http://localhost:5000`

### 4. Usar Componentes en Frontend

```jsx
import AdvisorRequest from './AdvisorRequest.jsx';
import AdvisorChat from './AdvisorChat.jsx';
import AdvisorDashboard from './AdvisorDashboard.jsx';
import AnalyticsDashboard from './AnalyticsDashboard.jsx';

export default function App() {
  return (
    <>
      <AdvisorRequest onRequestCreated={(data) => {
        console.log("Solicitud creada:", data.request_id);
      }} />
      
      <AdvisorDashboard advisorId={5} />
      <AnalyticsDashboard />
    </>
  );
}
```

---

## 📈 Métricas de Rendimiento

### Sistema de Asignación Inteligente

```python
score = 0
score += 40 * (especialidad_coincide)      # 40%
score += 30 * (1 - carga_actual)           # 30%
score += 20 * (rating / 5.0)               # 20%
score += 10 * max(0, (60 - resp_time)/60)  # 10%
```

### Analytics en Tiempo Real

- ✅ Solicitudes por estado
- ✅ Tasa de resolución
- ✅ Satisfacción promedio
- ✅ Tiempo promedio respuesta
- ✅ Carga de asesores
- ✅ Tendencias por tema

---

## 🎓 Próximas Mejoras (Roadmap)

### FASE 2 (COMPLETADA)
- ✅ WebSocket en tiempo real
- ✅ Componentes React profesionales
- ✅ Dashboard analytics
- ✅ Sugerencias de IA
- ✅ Notificaciones en vivo

### FASE 3 (TODO)
- [ ] Integración WhatsApp/Telegram
- [ ] Video conferencias (Jitsi/Google Meet)
- [ ] Scheduling automático
- [ ] ML para predicción de demanda
- [ ] Integración CRM
- [ ] Mobile app nativa
- [ ] Análisis de sentimiento avanzado
- [ ] Transcripción de audio
- [ ] Feedback automático

---

## 📚 Archivos Creados

| Archivo | Descripción |
|---------|-----------|
| `websocket_server.py` | Servidor WebSocket con SocketIO |
| `AdvisorRequest.jsx` | Modal para solicitar asesor |
| `AdvisorChat.jsx` | Componente chat usuario |
| `AdvisorDashboard.jsx` | Panel para asesores |
| `AnalyticsDashboard.jsx` | Dashboard de estadísticas |
| `advisor.css` | Estilos profesionales |
| `ai_suggestions.py` | Motor de sugerencias IA |
| `ai_suggestions_routes.py` | Endpoints para IA |
| `SISTEMA_COMPLETO.md` | Esta documentación |

---

## 🤝 Soporte

Para consultas o reportar bugs:
- 📧 Email: arion7754@gmail.com
- 📞 Teléfono: +57 4 3309500
- 💬 Chat en línea: Sistema de asesores

---

**Versión:** 2.0 - PROFESIONAL  
**Estado:** ✅ LISTO PARA PRODUCCIÓN  
**Última actualización:** 31 de mayo de 2026  
**Autor:** Sistema de Chatbot - UdeMedellín
