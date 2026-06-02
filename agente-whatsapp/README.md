# Agente WhatsApp - Universidad de Medellín

Bot de WhatsApp con inteligencia artificial local para responder consultas sobre programas académicos y becas de la Universidad de Medellín.

## Características

- 🤖 Respuestas inteligentes basadas en IA (OpenRouter)
- 💬 Integración con WhatsApp via Baileys
- 📱 Dashboard local para monitoreo
- 🗄️ Base de datos SQLite con persistencia
- 🔄 Sistema de cola de salida (outbox) confiable
- 🎯 Modo IA automático + modo escalada a humano
- 📊 Historial de conversaciones

## Stack Técnico

- **Backend**: Node.js 20+, TypeScript
- **Bot**: Baileys (WhatsApp Web)
- **Frontend**: Next.js 16 + React 19
- **Base de datos**: SQLite 3 con WAL mode
- **LLM**: OpenRouter (openai/gpt-4o-mini)
- **Estilos**: Tailwind CSS 4
- **Logs**: Pino (silenciado para Baileys)

## Requisitos

- Node.js 20.9.0 o superior
- npm/yarn
- Cuenta de OpenRouter con API key válida
- WhatsApp Desktop instalado (Baileys se conecta vía Web)

## Instalación

```bash
# Copiar ejemplo de variables de entorno
cp .env.example .env.local

# Editar .env.local con tus credenciales
# OPENROUTER_API_KEY=tu_api_key_aqui
# OPENROUTER_MODEL=openai/gpt-4o-mini

# Instalar dependencias
npm install

# Iniciar en desarrollo
npm run dev

# En otra terminal, iniciar el bot
npm run start:bot
```

## Desarrollo

### Estructura de Carpetas

```
src/
├── app/
│   ├── api/              # Rutas API
│   │   ├── status
│   │   ├── disconnect
│   │   ├── conversations
│   │   └── conversations/[id]/
│   ├── components/       # Componentes React
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── lib/
│   ├── db.ts             # SQLite + helpers
│   ├── openrouter.ts     # Llamadas a LLM
│   ├── system-prompt.ts
│   └── baileys/
│       ├── client.ts     # Socket initialization
│       └── handler.ts    # Message handling
scripts/
├── env-loader.ts         # Carga .env.local
└── start-bot.ts          # Punto de entrada del bot

data/                      # SQLite (gitignored)
auth/                      # Sesión WhatsApp (gitignored)
```

### Flujo de Mensajes

```
Usuario WhatsApp
         ↓
   Baileys Socket
         ↓
   handler.ts (handleIncomingMessage)
         ↓
   db.ts (insertMessage)
         ↓
   openrouter.ts (callOpenRouter)
         ↓
   db.ts (insertMessage + enqueueOutbox)
         ↓
   Baileys.sendMessage (periódicamente)
         ↓
   WhatsApp
```

## Uso

### Dashboard Local

Accede a `http://localhost:3000` para ver:
- Estado de conexión
- Código QR para escanear
- Lista de conversaciones activas
- Historial de mensajes por conversación
- Control de modo (IA/Humano)

### Modos de Operación

#### Modo IA (predeterminado)
- Bot responde automáticamente
- Usa OpenRouter para generar respuestas
- Mantiene contexto de última conversación

#### Modo HUMAN (escalada)
- Bot no responde automáticamente
- Ideal para transferir a operador humano
- Se activa manualmente desde el dashboard

### API Endpoints

```bash
# Estado de conexión
GET /api/status
# { status: "connected", phone: "573001234567", hasQr: false }

# Desconectar o cerrar sesión
POST /api/disconnect
# { clearAuth: true }  # true = borrar credenciales

# Listar conversaciones
GET /api/conversations
# [{ id, phone, name, mode, last_message_preview }]

# Eliminar conversación
DELETE /api/conversations
# { id: 1 }

# Obtener mensajes
GET /api/conversations/{id}/messages
# [{ id, role, content, created_at }]

# Enviar mensaje (para testing)
POST /api/conversations/{id}/messages
# { role: "user", content: "mensaje" }

# Cambiar modo
POST /api/conversations/{id}/mode
# { mode: "AI" | "HUMAN" }
```

## Configuración

### Variables de Entorno (.env.local)

```bash
# API Key de OpenRouter
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx

# Modelo LLM (default: openai/gpt-4o-mini)
OPENROUTER_MODEL=openai/gpt-4o-mini

# Node environment
NODE_ENV=development
```

### Estructura de Base de Datos

**Conversaciones**
- `id` (int, PK)
- `phone` (text, unique)
- `name` (text)
- `mode` (text: AI|HUMAN)
- `last_message_at` (int)
- `created_at` (int)

**Mensajes**
- `id` (int, PK)
- `conversation_id` (int, FK)
- `role` (text: user|assistant|human)
- `content` (text)
- `created_at` (int)

**Estado de Conexión**
- `id` (int, PK, siempre 1)
- `status` (text: disconnected|qr|connecting|connected)
- `qr_string` (text)
- `phone` (text)
- `updated_at` (int)

**Outbox (Cola de Salida)**
- `id` (int, PK)
- `conversation_id` (int)
- `phone` (text)
- `content` (text)
- `sent` (int: 0|1)
- `created_at` (int)

## Despliegue

### Local

```bash
# Terminal 1: Dashboard
npm run dev

# Terminal 2: Bot
npm run start:bot

# O ambos simultáneamente
npm run start:all
```

### Producción (Railway/Heroku compatible)

```bash
# Build
npm run build

# Start
npm start
```

Procesos:
- **web**: `npm run start` (Next.js en puerto 3000)
- **bot**: `npm run start:bot` (Script TSX)

### Contenedor (Nix Flake)

```bash
nix flake show
nix flake update
```

## Solución de Problemas

### "Code 440 - Device logged out"
- Baileys perdió sesión con WhatsApp
- Espera 15 segundos y reinicia automáticamente
- Si persiste, borra `auth/` y escanea código QR nuevamente

### Bot no responde
- Verifica `OPENROUTER_API_KEY` en `.env.local`
- Comprueba conexión a internet
- Revisa logs: `pm2 logs` (si usas PM2)

### Base de datos locked
- SQLite WAL es robusto, pero si ocurre:
  - Detén ambos procesos
  - Borra `data/messages.db-wal` y `data/messages.db-shm`
  - Reinicia

### QR no aparece
- Verifica que Baileys está conectando
- Revisa logs del bot: `npm run start:bot`
- Intenta desconectar y conectar de nuevo desde dashboard

## Lecciones Aprendidas

1. **Transacciones en SQLite**: Usar `db.transaction()` para atomicidad
2. **Concurrencia WAL**: Permite múltiples lectores simultáneos
3. **Backoff exponencial**: Para code 440 (device logout)
4. **15 segundos delay**: Suficiente para que Baileys estabilice estado
5. **Outbox pattern**: Garantiza entrega confiable de mensajes
6. **env-loader antes de imports**: Crítico para variables de entorno

## Limitaciones Intencionales (v1)

- No hay WebSockets en tiempo real (polling en lugar)
- Sin Redis (SQLite es suficiente)
- Sin Prisma/Drizzle (SQL puro para control)
- Sin Twilio (solo Baileys)
- Sin archivos de media (solo texto)

## Roadmap Futuro

- [ ] Soporte para imágenes/multimedia
- [ ] Integración con human escalation
- [ ] Estadísticas y reportes
- [ ] Backup automático de BD
- [ ] Multi-instancia (horizontal scaling)

## Support

Para problemas:
1. Revisa los logs del bot: `npm run start:bot`
2. Verifica `.env.local` está configurado
3. Abre issue con output de logs

---

**Construido con ❤️ para la Universidad de Medellín**
