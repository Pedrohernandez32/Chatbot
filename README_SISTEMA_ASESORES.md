# 🎓 Sistema de Asesores Humanos - Universidad de Medellín

## 🌟 Resumen

Sistema **PROFESIONAL DE NIVEL EMPRESARIAL** que permite a estudiantes hablar con asesores en tiempo real. Incluye:

- ✅ **Chat Instantáneo** - WebSocket con mensajes en tiempo real
- ✅ **Panel de Asesores** - Gestión profesional de solicitudes
- ✅ **Dashboard Analytics** - Métricas y estadísticas avanzadas
- ✅ **Inteligencia Artificial** - Sugerencias contextuales y detección de intención
- ✅ **Componentes Hermosos** - React con diseño moderno y responsivo
- ✅ **Validaciones Robustas** - Email, teléfono, seguridad
- ✅ **Rate Limiting** - Protección contra abuso (30 req/min)

---

## 🚀 Características Principales

### Para Usuarios
```
1. Hacer click en "Hablar con Asesor"
2. Rellenar formulario (nombre, email, tema)
3. Esperar en la cola (ver posición y tiempo estimado)
4. Chat en vivo con asesor profesional
5. Calificar la atención (1-5 estrellas)
```

### Para Asesores
```
1. Iniciar sesión
2. Ver solicitudes pendientes en panel
3. Asignar solicitudes a sí mismos
4. Chat en vivo con usuarios
5. Ver estadísticas personales (rating, tiempo, satisfacción)
6. Cambiar estado (online/offline/away/busy)
```

### Para Administradores
```
1. Ver dashboard con métricas globales
2. Análisis de solicitudes por tema
3. Satisfacción del cliente
4. Carga de asesores
5. Tiempo promedio de respuesta
6. Tendencias y insights automáticos
```

---

## 📁 Estructura de Archivos

```
Chatbot/
├── Backend
│   ├── server.py                    ← Servidor principal (Flask)
│   ├── websocket_server.py          ← WebSocket en tiempo real
│   ├── advisor_routes.py            ← Endpoints REST
│   ├── advisor_enhanced.py          ← Lógica avanzada
│   ├── ai_suggestions.py            ← Motor de IA (NLU)
│   ├── ai_suggestions_routes.py     ← Endpoints de IA
│   ├── database.py                  ← Persistencia
│   └── info_plugin.py               ← Plugin de información
│
├── Frontend
│   ├── AdvisorRequest.jsx           ← Modal de solicitud
│   ├── AdvisorChat.jsx              ← Chat usuario
│   ├── AdvisorDashboard.jsx         ← Panel asesores
│   ├── AnalyticsDashboard.jsx       ← Dashboard admin
│   └── advisor.css                  ← Estilos profesionales
│
└── Documentación
    ├── SISTEMA_COMPLETO.md          ← Doc técnica completa
    ├── EJEMPLO_INTEGRACION.md       ← Ejemplos de uso
    └── ADVISOR_SYSTEM.md            ← API Reference (antiguo)
```

---

## 🔧 Instalación Rápida

### 1. Instalar Dependencias
```bash
pip install flask flask-cors flask-login flask-socketio python-socketio python-engineio
```

### 2. Inicializar Base de Datos
```bash
python
>>> from database import init_db
>>> init_db()
>>> exit()
```

### 3. Ejecutar Servidor
```bash
python server.py
# Servidor escuchando en http://localhost:5000
```

### 4. Usar Componentes
```jsx
import AdvisorRequest from './AdvisorRequest.jsx';

// En tu página
<AdvisorRequest onRequestCreated={(data) => {
  console.log('Solicitud creada:', data.request_id);
}} />
```

---

## 🎯 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-----------|
| `POST` | `/api/advisor/request` | Crear solicitud |
| `GET` | `/api/advisor/requests` | Ver pendientes (admin) |
| `POST` | `/api/advisor/message/<id>` | Enviar mensaje |
| `GET` | `/api/advisor/messages/<id>` | Obtener historial |
| `POST` | `/api/advisor/status` | Cambiar estado asesor |
| `POST` | `/api/advisor/suggestions` | Obtener sugerencias IA |
| `POST` | `/api/advisor/intent` | Detectar intención |
| `POST` | `/api/advisor/sentiment` | Analizar sentimiento |
| `GET` | `/api/advisor/analytics` | Métricas del sistema |

**Documentación completa:** [SISTEMA_COMPLETO.md](SISTEMA_COMPLETO.md)

---

## 🤖 Inteligencias Artificial (NLU)

### Intenciones Detectadas

Cuando un usuario pregunta algo, el sistema detecta automáticamente:

| Intención | Ejemplos | Respuestas |
|-----------|----------|----------|
| **becas** | "¿Qué becas hay?" | 4 respuestas contextuales |
| **admisiones** | "¿Cómo ingreso?" | 4 respuestas contextuales |
| **campus** | "¿Dónde están?" | 4 respuestas contextuales |
| **horarios** | "¿A qué hora?" | 4 respuestas contextuales |
| **contacto** | "¿Cómo llamo?" | 4 respuestas contextuales |
| **profesores** | "¿Quiénes son?" | 4 respuestas contextuales |
| **decanos** | "¿Quién dirige?" | 4 respuestas contextuales |

### Análisis de Sentimiento

```python
sentiment = AdvisorAISuggestions.analyze_sentiment(
    "¡Excelente servicio, muchas gracias!"
)
# Output: {"sentiment": "positive", "confidence": 0.85}
```

### Preguntas de Seguimiento

Sistema genera preguntas automáticas para profundizar:

```
Usuario: "¿Qué becas hay?"
Bot sugiere:
  1. "¿Ya tienes semestre de promedio?"
  2. "¿Necesitas beca para todo el programa?"
```

---

## 📊 Métricas y Analytics

El dashboard muestra en tiempo real:

```
📈 Total Solicitudes: 145
✅ Resoluciones: 120 (82.7%)
⭐ Satisfacción: 4.6/5 estrellas
⏱️ Tiempo Promedio: 12 minutos
⏳ Espera Promedio: 3 minutos
👥 Asesores Online: 5/8
💬 Mensajes Totales: 1,240
📌 Tema Popular: Becas (35%)
```

---

## 🔌 WebSocket - Eventos en Tiempo Real

```javascript
// Conectar
const socket = io('http://localhost:5000');

// Enviar mensaje
socket.emit('send_message', {
  request_id: 1,
  message: "Hola asesor",
  sender_id: 123
});

// Escuchar nuevos mensajes
socket.on('new_message', (data) => {
  console.log("Nuevo mensaje:", data.message);
});

// Indicador de "escribiendo"
socket.emit('typing', { request_id: 1 });
socket.on('user_typing', (data) => {
  // Mostrar indicador de que escriben
});
```

---

## 🎨 Diseño UI/UX

### Colores
```
Primario:   #1e40af  (Azul profesional)
Secundario: #7c3aed  (Púrpura moderno)
Éxito:      #16a34a  (Verde)
Error:      #dc2626  (Rojo)
Gris:       #f3f4f6  (Claro)
```

### Componentes
- ✨ Botones con gradiente
- ✨ Modales con animaciones
- ✨ Formularios con validación
- ✨ Chat con auto-scroll
- ✨ Dashboards responsivos
- ✨ Animaciones suaves (0.3s)

### Responsive
```
📱 Mobile:  < 480px  (Stack vertical)
📱 Tablet:  480-768px (2 columnas)
💻 Desktop: > 768px  (3+ columnas)
```

---

## 🔐 Seguridad

### Validaciones

✅ **Email:** RFC 5322 completo
```
juan.garcia+tag@ejemplo.co.uk → ✓
```

✅ **Teléfono:** Internacional +57 300 1234567
```
+57 3001234567 → ✓
3001234567     → ✓
+57 (300) 123-4567 → ✓
```

✅ **Mensajes:** 1-5000 caracteres
```
"" → ✗ (vacío)
"Hola" → ✓
"..." (5001 chars) → ✗ (muy largo)
```

### Rate Limiting

```
30 requests/minuto por IP
Reinicia cada 60 segundos
```

### Autenticación

```
- Usuarios anónimos pueden solicitar
- Asesores requieren login
- Admins requieren key especial
```

---

## 📚 Documentación

| Documento | Contenido |
|-----------|----------|
| [SISTEMA_COMPLETO.md](SISTEMA_COMPLETO.md) | Documentación técnica detallada |
| [EJEMPLO_INTEGRACION.md](EJEMPLO_INTEGRACION.md) | 10 ejemplos prácticos de uso |
| [ADVISOR_SYSTEM.md](ADVISOR_SYSTEM.md) | API Reference (versión 1.0) |
| Este archivo | Overview general |

---

## 🚀 Próximos Pasos

### FASE 3 (Roadmap Futuro)

- [ ] Integración WhatsApp/Telegram
- [ ] Video conferencias
- [ ] Scheduling automático
- [ ] Machine Learning avanzado
- [ ] Análisis de audio
- [ ] Mobile app nativa
- [ ] Integración CRM
- [ ] Transcripciones automáticas

---

## 💡 Tips y Trucos

### Para Usuarios

```
1. Se específico en tu pregunta
2. Incluye el tema de tu consulta
3. Ten tu email y teléfono listos
4. Califica la atención al terminar
```

### Para Asesores

```
1. Cambia a "online" cuando estés disponible
2. Las sugerencias de IA te ayudan a responder
3. Las preguntas de seguimiento profundizan
4. Tu calificación se basa en resolución rápida
```

### Para Administradores

```
1. Monitorea el dashboard en tiempo real
2. Detecta picos de demanda
3. Analiza temas populares
4. Mide satisfacción del cliente
```

---

## 🐛 Troubleshooting

### El servidor no inicia

```bash
# Verificar que el puerto 5000 está libre
lsof -i :5000

# Cambiar puerto en server.py
app.run(debug=True, port=5001)
```

### WebSocket no conecta

```javascript
// Verificar que socketio está cargado
console.log(io);  // Debe mostrar la librería

// Verificar URL del servidor
const socket = io('http://localhost:5000');
```

### Mensajes no se sincronizan

```
- Verificar que browser acepta cookies
- Limpiar localStorage
- Verificar conexión a internet
- Revisar console del navegador (F12)
```

---

## 📞 Soporte

### Contacto Universidad
- 📧 info@udemedellín.edu.co
- 📞 +57 4 3309500
- 🌐 www.udemedellín.edu.co

### Reportar Bugs
- Crear issue en GitHub
- Describir pasos para reproducir
- Incluir versión del navegador
- Incluir logs del servidor

---

## 📜 Licencia

Proyecto propietario de Universidad de Medellín (2026)

---

## 🎓 Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | Mayo 2026 | Sistema base de asesores |
| 2.0 | Mayo 2026 | WebSocket + IA + Analytics |
| 3.0 | Próximamente | WhatsApp + Video |

---

**Sistema implementado y listo para producción ✅**

Última actualización: 31 de mayo de 2026

Autor: Pedro Hernández (PedroHernandez32)
