# 🎯 Ejemplo de Integración - Sistema de Asesores

## 📱 Ejemplo 1: Integrar en Página Principal

```jsx
// App.jsx o Asistente Virtual UdeMedellin.html

import React, { useState } from 'react';
import AdvisorRequest from './AdvisorRequest.jsx';
import AdvisorChat from './AdvisorChat.jsx';

export default function ChatbotPage() {
  const [chatOpen, setChatOpen] = useState(false);
  const [requestId, setRequestId] = useState(null);

  return (
    <div className="chatbot-container">
      {/* Panel principal del chatbot */}
      <div className="chat-panel">
        <h2>🤖 Asistente Virtual UdeMedellín</h2>
        
        {/* Botón para solicitar asesor */}
        <AdvisorRequest 
          onRequestCreated={(data) => {
            console.log('✅ Solicitud creada:', data);
            setRequestId(data.request_id);
            setChatOpen(true);
          }}
        />
      </div>

      {/* Modal de chat cuando hay solicitud activa */}
      {chatOpen && requestId && (
        <div className="modal">
          <AdvisorChat 
            requestId={requestId}
            userName="Usuario"
            onClose={() => {
              setChatOpen(false);
              setRequestId(null);
            }}
          />
        </div>
      )}
    </div>
  );
}
```

---

## 👥 Ejemplo 2: Panel de Asesores (Admin)

```jsx
// AdvisorPanel.jsx

import React, { useState } from 'react';
import AdvisorDashboard from './AdvisorDashboard.jsx';

export default function AdvisorPanel() {
  // Solo mostrar si está logueado y es asesor
  const [user, setUser] = useState(null);

  return (
    <div className="advisor-panel-page">
      <AdvisorDashboard advisorId={user?.id} />
    </div>
  );
}
```

---

## 📊 Ejemplo 3: Dashboard de Estadísticas

```jsx
// AdminDashboard.jsx

import React from 'react';
import AnalyticsDashboard from './AnalyticsDashboard.jsx';

export default function AdminDashboard() {
  return (
    <div className="admin-dashboard">
      <h1>📊 Administración</h1>
      <AnalyticsDashboard />
    </div>
  );
}
```

---

## 🧠 Ejemplo 4: Usar Sugerencias de IA desde JavaScript

```javascript
// Obtener sugerencias cuando asesor empieza a escribir

async function obtenerSugerencias(mensajeUsuario) {
  const response = await fetch('/api/advisor/suggestions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: mensajeUsuario,
      conversation_history: []
    })
  });

  const data = await response.json();
  
  console.log('Intención detectada:', data.intent);
  console.log('Sugerencias:', data.suggestions);
  console.log('Acciones rápidas:', data.quick_actions);
  console.log('Preguntas de seguimiento:', data.followup_questions);
  console.log('Sentimiento:', data.sentiment);

  // Mostrar sugerencias en interfaz
  mostrarSugerencias(data.suggestions);
  mostrarAccionesRapidas(data.quick_actions);
}

// Uso
obtenerSugerencias("¿Cuáles son las becas disponibles?");
```

**Output:**
```json
{
  "intent": "becas",
  "suggestions": [
    "Tenemos varios tipos de becas disponibles: Excelencia, Meritoria, Socioeconómica y Permanencia. ¿Cuál tipo de beca te interesa?",
    "Las becas varían según tu desempeño académico y situación económica. ¿Cuál es tu contexto?"
  ],
  "quick_actions": [
    {"label": "Ver tipos de becas", "action": "show_becas"},
    {"label": "Requisitos de solicitud", "action": "requirements"}
  ],
  "followup_questions": [
    "¿Ya tienes un semestre de promedio académico?",
    "¿Necesitas becas para todo el programa o solo este semestre?"
  ],
  "sentiment": {"sentiment": "positive", "confidence": 0.8}
}
```

---

## 🔗 Ejemplo 5: WebSocket en Tiempo Real

```javascript
// Conectar al WebSocket

const socket = io('http://localhost:5000');

// 1. Usuario se conecta
socket.emit('user_login', {
  user_id: 123,
  is_advisor: false
});

// 2. Unirse a sala de solicitud
socket.emit('join_request', {
  request_id: 1,
  user_id: 123
});

// 3. Escuchar nuevos mensajes
socket.on('new_message', (data) => {
  console.log('Nuevo mensaje:', data.message);
  console.log('De:', data.sender_name);
  console.log('Tipo:', data.sender_type);
  
  // Agregar mensaje a la interfaz
  agregarMensajeAlChat(data);
});

// 4. Enviar mensaje
socket.emit('send_message', {
  request_id: 1,
  message: "Hola, necesito ayuda con becas",
  sender_id: 123,
  sender_type: "user",
  sender_name: "Juan García"
});

// 5. Mostrar indicador de "escribiendo"
socket.on('user_typing', (data) => {
  mostrarIndicadorEscribiendo(data.user_id);
});

// 6. Asesor cambia estado
socket.emit('advisor_status_change', {
  advisor_id: 5,
  status: "online"
});

// 7. Escuchar cambios de estado
socket.on('advisor_status_updated', (data) => {
  console.log(`Asesor ${data.advisor_id} está ${data.status}`);
  actualizarEstadoAsesor(data.advisor_id, data.status);
});

// 8. Desconectar
socket.disconnect();
```

---

## 📝 Ejemplo 6: Llamar Endpoints REST desde Python

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# 1. Crear solicitud
response = requests.post(f'{BASE_URL}/api/advisor/request', json={
    'name': 'Carlos López',
    'email': 'carlos@example.com',
    'phone': '+57 300 1234567',
    'topic': 'Becas'
})

data = response.json()
request_id = data['request_id']
print(f"✅ Solicitud creada: #{request_id}")
print(f"   Posición en cola: {data['position_in_queue']}")
print(f"   Tiempo estimado: {data['estimated_wait_minutes']} minutos")

# 2. Obtener solicitudes pendientes (requiere auth)
headers = {'Authorization': 'Bearer <tu_token>'}
response = requests.get(f'{BASE_URL}/api/advisor/requests', headers=headers)
requests_data = response.json()
print(f"\n📋 Solicitudes pendientes: {len(requests_data['requests'])}")

# 3. Enviar mensaje
response = requests.post(f'{BASE_URL}/api/advisor/message/{request_id}', json={
    'message': '¿Qué tipos de becas hay para estudiantes de ingeniería?'
})

msg_data = response.json()
print(f"\n💬 Mensaje enviado (ID: {msg_data['message_id']})")

# 4. Obtener historial
response = requests.get(f'{BASE_URL}/api/advisor/messages/{request_id}')
messages = response.json()

print(f"\n📨 Historial de {len(messages['messages'])} mensajes:")
for msg in messages['messages']:
    sender = "Asesor" if msg['sender_type'] == 'advisor' else "Tú"
    print(f"  {sender}: {msg['message']}")

# 5. Obtener sugerencias de IA
response = requests.post(f'{BASE_URL}/api/advisor/suggestions', json={
    'message': '¿Cómo solicito una beca de excelencia?',
    'conversation_history': []
})

suggestions = response.json()
print(f"\n🤖 Sugerencias de IA para: '{suggestions['intent']}'")
for i, sugg in enumerate(suggestions['suggestions'], 1):
    print(f"  {i}. {sugg}")

# 6. Cambiar estado del asesor
response = requests.post(
    f'{BASE_URL}/api/advisor/status',
    headers=headers,
    json={'status': 'online'}
)

status_data = response.json()
print(f"\n✅ Estado actualizado a: {status_data['status']}")

# 7. Obtener analytics
response = requests.get(
    f'{BASE_URL}/api/advisor/analytics?range=day',
    headers=headers
)

analytics = response.json()
metrics = analytics['metrics']
print(f"\n📊 Análisis del sistema:")
print(f"  - Total solicitudes: {metrics['total_requests']}")
print(f"  - Resoluciones: {metrics['closed_requests']}")
print(f"  - Satisfacción: {metrics['customer_satisfaction_avg']:.1f}⭐")
print(f"  - Tiempo promedio: {metrics['avg_resolution_time_minutes']} minutos")
```

---

## 🎨 Ejemplo 7: Personalizar Estilos

```css
/* Personalizar colores en tu aplicación */

:root {
  --primary: #1e40af;        /* Cambiar color primario */
  --secondary: #7c3aed;      /* Cambiar color secundario */
  --success: #16a34a;        /* Cambiar color éxito */
}

/* Cambiar tamaño del botón */
.btn-advisor-main {
  padding: 16px 32px;        /* Más grande */
  font-size: 18px;
}

/* Personalizar modal */
.advisor-modal {
  max-width: 600px;          /* Más ancho */
  border-radius: 12px;       /* Más redondeado */
}

/* Personalizar chat */
.advisor-chat-container {
  height: 700px;             /* Más alto */
  border: 2px solid var(--primary);
}
```

---

## 🔐 Ejemplo 8: Autenticación y Autorización

```javascript
// auth.js - Gestionar tokens y permisos

class AuthService {
  async login(email, password) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    
    if (data.user) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      return data.user;
    }
    
    throw new Error('Login fallido');
  }

  getToken() {
    return localStorage.getItem('token');
  }

  getUser() {
    return JSON.parse(localStorage.getItem('user'));
  }

  isAdvisor() {
    const user = this.getUser();
    return user?.is_admin || false;
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
}

// Usar en componentes
import AuthService from './auth.js';

export default function AdvisorDashboard() {
  const isAdvisor = AuthService.isAdvisor();
  
  if (!isAdvisor) {
    return <div>Acceso denegado - Solo para asesores</div>;
  }

  return <div>Panel de Asesores</div>;
}
```

---

## 📱 Ejemplo 9: Hacer Responsive en Móvil

```javascript
// Detectar si es móvil y adaptar interfaz

const isMobile = window.innerWidth <= 768;

if (isMobile) {
  // En móvil, mostrar chat en pantalla completa
  document.querySelector('.advisor-chat-container').style.height = '100vh';
  
  // Ocultar panel lateral de solicitudes
  document.querySelector('.requests-list').style.display = 'none';
}

// O usar CSS media queries
/* Automático con CSS */
@media (max-width: 768px) {
  .advisor-chat-container {
    height: 100vh;
  }
  
  .requests-list {
    display: none;
  }
}
```

---

## 🧪 Ejemplo 10: Testing de Endpoints

```bash
#!/bin/bash
# test_advisor_api.sh

BASE_URL="http://localhost:5000"

# 1. Crear solicitud
echo "📝 Creando solicitud..."
curl -X POST $BASE_URL/api/advisor/request \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+57 300 1234567",
    "topic": "Becas"
  }'

# 2. Obtener sugerencias de IA
echo -e "\n🤖 Obteniendo sugerencias..."
curl -X POST $BASE_URL/api/advisor/suggestions \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué becas hay disponibles?",
    "conversation_history": []
  }'

# 3. Detectar intención
echo -e "\n🎯 Detectando intención..."
curl -X POST $BASE_URL/api/advisor/intent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuáles son los horarios?"
  }'

# 4. Analizar sentimiento
echo -e "\n💭 Analizando sentimiento..."
curl -X POST $BASE_URL/api/advisor/sentiment \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¡Excelente ayuda, muchas gracias!"
  }'
```

---

## 📚 Recursos Adicionales

- **Documentación Completa:** [SISTEMA_COMPLETO.md](SISTEMA_COMPLETO.md)
- **API Reference:** Endpoints REST documentados arriba
- **WebSocket Events:** Ejemplos de Socket.io
- **Base de Datos:** Schema SQL en database.py
- **Estilos:** advisor.css con variables CSS personalizables

---

**¡Listo para usar! 🚀**

Todos los componentes están optimizados y listos para producción.
