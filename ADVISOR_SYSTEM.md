# 👨‍💼 Sistema de Asesores Humanos - Documentación

## Descripción General

Sistema completo para que usuarios puedan solicitar hablar con un **asesor humano** en tiempo real. Incluye:

✅ Solicitud de asesor  
✅ Cola de espera  
✅ Chat en vivo  
✅ Panel para asesores  
✅ Historial de conversaciones  

---

## 📝 API Endpoints

### 1. Solicitar Asesor

**Endpoint:** `POST /api/advisor/request`

**Request:**
```json
{
  "name": "Juan García",
  "email": "juan@example.com",
  "phone": "+57 300 1234567",
  "topic": "Becas"
}
```

**Response:**
```json
{
  "success": true,
  "request_id": 1,
  "message": "Solicitud creada. Un asesor se conectará pronto."
}
```

---

### 2. Obtener Solicitudes Pendientes (Asesores)

**Endpoint:** `GET /api/advisor/requests`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "requests": [
    {
      "id": 1,
      "name": "Juan García",
      "email": "juan@example.com",
      "phone": "+57 300 1234567",
      "topic": "Becas",
      "status": "waiting",
      "created_at": "2026-05-31 10:30:00"
    }
  ]
}
```

---

### 3. Asignar Solicitud a Asesor

**Endpoint:** `POST /api/advisor/assign/<request_id>`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Solicitud asignada"
}
```

---

### 4. Enviar Mensaje

**Endpoint:** `POST /api/advisor/message/<request_id>`

**Request:**
```json
{
  "message": "Hola, ¿puedo ayudarte con información de becas?"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Mensaje enviado"
}
```

---

### 5. Obtener Historial de Mensajes

**Endpoint:** `GET /api/advisor/messages/<request_id>`

**Response:**
```json
{
  "success": true,
  "request": {
    "id": 1,
    "name": "Juan García",
    "topic": "Becas",
    "status": "assigned"
  },
  "messages": [
    {
      "id": 1,
      "request_id": 1,
      "sender_id": null,
      "sender_type": "user",
      "message": "Hola, necesito info sobre becas",
      "created_at": "2026-05-31 10:31:00"
    },
    {
      "id": 2,
      "request_id": 1,
      "sender_id": 5,
      "sender_type": "advisor",
      "message": "¡Hola! Soy asesor de becas. ¿Qué tipo de beca necesitas?",
      "created_at": "2026-05-31 10:32:00"
    }
  ]
}
```

---

### 6. Cerrar Solicitud

**Endpoint:** `POST /api/advisor/close/<request_id>`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Solicitud cerrada"
}
```

---

### 7. Actualizar Estado de Asesor

**Endpoint:** `POST /api/advisor/status`

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "status": "online"  // online | offline
}
```

**Response:**
```json
{
  "success": true,
  "status": "online"
}
```

---

### 8. Obtener Asesores Disponibles

**Endpoint:** `GET /api/advisor/available`

**Response:**
```json
{
  "success": true,
  "advisors": [
    {
      "id": 5,
      "user_id": 5,
      "department": "Becas",
      "status": "online",
      "current_chats": 1,
      "max_chats": 3
    }
  ],
  "available": true
}
```

---

## 🏗️ Estructura de Base de Datos

### Tabla: `advisor_requests`

| Campo | Tipo | Descripción |
|-------|------|-----------|
| id | INTEGER | ID único |
| user_id | INTEGER | ID del usuario (NULL si anónimo) |
| name | TEXT | Nombre del solicitante |
| email | TEXT | Email de contacto |
| phone | TEXT | Teléfono (opcional) |
| topic | TEXT | Tema de la consulta |
| message | TEXT | Mensaje inicial |
| status | TEXT | waiting/assigned/resolved |
| assigned_to | INTEGER | ID del asesor asignado |
| created_at | TIMESTAMP | Fecha de creación |
| resolved_at | TIMESTAMP | Fecha de resolución |

### Tabla: `advisor_messages`

| Campo | Tipo | Descripción |
|-------|------|-----------|
| id | INTEGER | ID único |
| request_id | INTEGER | ID de la solicitud |
| sender_id | INTEGER | ID de quien envía (NULL si usuario anónimo) |
| sender_type | TEXT | user/advisor |
| message | TEXT | Contenido del mensaje |
| created_at | TIMESTAMP | Fecha de envío |

### Tabla: `advisors`

| Campo | Tipo | Descripción |
|-------|------|-----------|
| id | INTEGER | ID único |
| user_id | INTEGER | ID del usuario asesor |
| department | TEXT | Departamento (Becas, Admisiones, etc) |
| status | TEXT | online/offline |
| current_chats | INTEGER | Chats activos |
| max_chats | INTEGER | Máximo de chats simultáneos |
| last_active | TIMESTAMP | Última actividad |

---

## 💻 Flujo de Uso

### Para Usuarios:

```
1. Usuario cliquea "Hablar con Asesor"
   ↓
2. Rellena formulario (nombre, email, tema)
   ↓
3. Crea solicitud via POST /api/advisor/request
   ↓
4. Entra en cola de espera
   ↓
5. Espera a que un asesor se conecte
   ↓
6. Chat en vivo via POST /api/advisor/message/<id>
   ↓
7. Asesor cierra la conversación
```

### Para Asesores:

```
1. Asesor inicia sesión
   ↓
2. Cambia estado a online via POST /api/advisor/status
   ↓
3. Ve solicitudes pendientes via GET /api/advisor/requests
   ↓
4. Cliquea en una solicitud para asignarla
   ↓
5. POST /api/advisor/assign/<id>
   ↓
6. Obtiene historial de mensajes via GET /api/advisor/messages/<id>
   ↓
7. Envía mensajes via POST /api/advisor/message/<id>
   ↓
8. Cierra solicitud cuando termina
   ↓
9. POST /api/advisor/close/<id>
```

---

## 🎯 Ejemplo de Implementación Frontend

### Botón para Solicitar Asesor

```html
<button class="btn-asesor" onclick="solicitarAsesor()">
  📞 Hablar con Asesor
</button>

<div id="modal-asesor" style="display:none">
  <form onsubmit="crearSolicitud(event)">
    <input type="text" placeholder="Tu nombre" id="nombre" required>
    <input type="email" placeholder="Tu email" id="email" required>
    <input type="tel" placeholder="Tu teléfono" id="telefono">
    <select id="tema">
      <option>Becas</option>
      <option>Admisiones</option>
      <option>Campus</option>
      <option>Horarios</option>
      <option>Otra consulta</option>
    </select>
    <button type="submit">Solicitar Asesor</button>
  </form>
</div>

<script>
async function solicitarAsesor() {
  const nombre = document.getElementById('nombre').value;
  const email = document.getElementById('email').value;
  const telefono = document.getElementById('telefono').value;
  const tema = document.getElementById('tema').value;

  const response = await fetch('/api/advisor/request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: nombre,
      email: email,
      phone: telefono,
      topic: tema
    })
  });

  const data = await response.json();
  if (data.success) {
    const requestId = data.request_id;
    // Redirigir a chat o mostrar panel de espera
    entrarEnChat(requestId);
  }
}

async function entrarEnChat(requestId) {
  // Mostrar chat en vivo
  // Obtener mensajes previos
  const response = await fetch(`/api/advisor/messages/${requestId}`);
  const data = await response.json();
  
  // Mostrar historial
  mostrarMensajes(data.messages);
  
  // Configurar WebSocket o polling para nuevos mensajes
}
</script>
```

---

## 🔐 Seguridad

✅ Requiere autenticación para asesores  
✅ Usuarios anónimos pueden solicitar (sin login)  
✅ Validación de entrada (XSS protection)  
✅ Rate limiting en solicitudes  
✅ Historial encriptado  

---

## 📊 Estadísticas Disponibles

```
- Solicitudes por tema
- Tiempo promedio de respuesta
- Satisfacción de usuarios
- Carga de asesores
- Solicitudes sin asignar
```

---

## 🚀 Próximas Mejoras

- [ ] WebSocket para chat en tiempo real (vs polling)
- [ ] Notificaciones push cuando asesor se conecta
- [ ] Calificación de atención
- [ ] Feedback automático
- [ ] Integración con WhatsApp/Telegram
- [ ] IA para sugerir respuestas a asesores
- [ ] Transcripciones de chat
- [ ] Analytics dashboard

---

**Versión:** 1.0  
**Última actualización:** 31 de mayo de 2026  
**Status:** ✅ IMPLEMENTADO Y LISTO PARA USAR
