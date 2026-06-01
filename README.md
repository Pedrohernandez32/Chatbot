# 🎓 Universidad de Medellín - Asistente Virtual Inteligente

Un chatbot inteligente y hermoso basado en React + Flask que proporciona información completa sobre la Universidad de Medellín.

## ✨ Características Principales

### 🤖 **Bot Inteligente y Contextual**
- Respuestas granulares según lo que preguntas
- Detecta búsquedas específicas: ingenierías, profesores, decanos, calidad
- Fallback a Claude AI/OpenAI para preguntas generales
- Historial de chat persistente con localStorage
- Sugerencias inteligentes

### 📚 **Base de Conocimiento Completa**
- **20+ carreras** con duración, perfil, campo laboral
- **7 facultades** con decano, contacto, acreditaciones
- **8 becas** con requisitos y cómo solicitarlas
- **320+ profesores** organizados por carrera
- Información de campus, horarios, admisiones
- Estadísticas de empleabilidad y calidad

### 👥 **Dashboard Admin Profesional**
- 6 tabs: Dashboard, Usuarios, Conversaciones, Preguntas desconocidas, Respuestas aprendidas, Editor
- Gestión de roles y permisos
- Análisis de conversaciones
- Sistema de aprendizaje automático

### 🎨 **Diseño Moderno y Responsivo**
- Interface hermosa con animaciones suaves
- Testimonios de estudiantes (carrusel)
- Noticias y eventos actualizados
- Secciones de vida estudiantil
- Galería de campus interactiva
- FAQ con respuestas expandibles
- Footer con redes sociales

## 🚀 Inicio Rápido

### Requisitos
- Python 3.11+
- Git

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/udemedellin-chatbot.git
cd udemedellin-chatbot

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (opcional)
cp .env.example .env
# Edita .env con tus API keys (OpenAI, Claude, etc.)

# 5. Inicializar base de datos
python -c "from database import init_db; init_db()"

# 6. Iniciar servidor
python server.py
```

Abre **http://localhost:5000** en tu navegador.

## 📁 Estructura del Proyecto

```
.
├── server.py                           # Servidor Flask (rutas, autenticación, chat)
├── database.py                         # BD (usuarios, conversaciones, feedback)
├── info_plugin.py                      # Base de conocimiento (carreras, becas, etc)
├── info_enriquecida.py                # Datos adicionales (facultades, decanos)
├── ai_plugin.py                       # Orquestador de AI (fallback a Claude/OpenAI)
├── openai_plugin.py                   # Integración OpenAI
├── Asistente Virtual UdeMedellin.html # Entrada principal (React)
├── app.jsx                            # Componente App (orquestación)
├── chat.jsx                           # Interfaz de chat
├── login.jsx                          # Autenticación
├── admin.jsx                          # Dashboard admin
├── sections.jsx                       # Hero, Nav, Servicios, Stats
├── sections2.jsx                      # Campus, FAQ, Footer
├── sections3.jsx                      # Testimonios, Noticias, Vida Estudiantil
├── icons.jsx                          # Librería de iconos SVG
├── styles.css                         # Design tokens, colores, tipografía
├── chat.css                           # Estilos chat bubble y animaciones
├── sections.css                       # Layout secciones
├── sections3.css                      # Testimonios, noticias, carrusel
├── login.css                          # Formas de autenticación
├── admin.css                          # Dashboard grid y tablas
├── assets/                            # Imágenes y recursos
├── DEPLOYMENT.md                      # Guía deployment en producción
└── README.md                          # Este archivo
```

## 💬 Ejemplos de Conversación

```
Usuario: "¿Qué ingenierías hay?"
Bot: ✅ Muestra 5 ingenierías con emoji, descripción, 
     acreditación, tasa empleo, convenios

Usuario: "Ingeniería de Sistemas"
Bot: ✅ Detalles completos: duración, modalidad, descripción,
     perfil, campo laboral, requisitos, facultad, decano

Usuario: "profesores"
Bot: ✅ 320+ docentes, experiencia 10+ años, 
     doctores/maestros por carrera, programas desarrollo

Usuario: "decanos"
Bot: ✅ 6 decanos con facultad, teléfono, email

Usuario: "calidad acreditacion"
Bot: ✅ Acreditación vigente, certificaciones ISO,
     indicadores: empleabilidad, satisfacción, egreso

Usuario: "beca social"
Bot: ✅ Requisitos, beneficios, renovación, cómo solicitar
```

## 🔧 Tecnologías

### Backend
- **Flask** - Framework web ligero y poderoso
- **SQLite/PostgreSQL** - Base de datos (SQLite dev, PostgreSQL prod)
- **Flask-Login** - Autenticación segura
- **Flask-CORS** - Soporte cross-origin

### Frontend
- **React 18** - Componentes interactivos
- **Vanilla CSS** - Diseño moderno (sin Bootstrap)
- **Marked.js** - Renderización Markdown
- **DOMPurify** - Protección XSS
- **Intersection Observer** - Lazy reveal on scroll

### IA y Fallback
- **Claude API** - Respuestas generales inteligentes
- **OpenAI API** - Alternativa de fallback
- **Ollama** - LLM local opcional

## 🔒 Seguridad

✅ **Rate limiting** - 30 requests/minuto  
✅ **Validación** - Entrada sanitizada, límite 1000 caracteres  
✅ **XSS protection** - DOMPurify en todas las respuestas  
✅ **CSRF** - Token validation en formularios  
✅ **Autenticación** - Hashing Werkzeug, sessions seguras  
✅ **SQL injection** - Parametrized queries  
✅ **HTTPS ready** - Cookies secure/httponly/samesite  
✅ **Admin protection** - Roles y permisos granulares

## ⚡ Optimizaciones

✅ Lazy loading de imágenes  
✅ Meta tags SEO (og:, description, keywords)  
✅ Schema.org structured data  
✅ Cache headers configurados  
✅ Respuestas inteligentes y contextuales  
✅ Historial persistente (localStorage)  
✅ Animaciones CSS3 optimizadas  
✅ Colores y tipografía profesionales

## 🚀 Deployment

Para instrucciones completas de producción, ver **[DEPLOYMENT.md](DEPLOYMENT.md)**:

- Configuración variables de entorno
- HTTPS/SSL con Let's Encrypt
- PostgreSQL en producción
- Gunicorn/Nginx setup
- Docker deployment
- Monitoreo y logging
- Backup automático

### Deploy rápido:
- **Heroku**: `git push heroku main`
- **Render**: Conecta GitHub, deploy automático
- **DigitalOcean**: VPS + Docker
- **Local**: `python server.py` (desarrollo)

## 📊 API Endpoints

### Chat
```
POST /api/chat
- Input: {"message": "tu pregunta"}
- Output: {"response": "...", "category": "...", "ai": true/false}
```

### Autenticación
```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/logout
```

### Admin (requiere autenticación)
```
GET  /api/admin/users
GET  /api/admin/conversations
GET  /api/admin/unknown-questions
POST /api/admin/learn-response
```

## 🤝 Contribuir

Las contribuciones son bienvenidas:

```bash
# 1. Fork el repo
# 2. Rama nueva: git checkout -b feature/NuevaCaracteristica
# 3. Commit: git commit -m "Add NuevaCaracteristica"
# 4. Push: git push origin feature/NuevaCaracteristica
# 5. Pull Request
```

## 📞 Soporte

- Email: soporte@udemedellin.edu.co
- Teléfono: +57 (604) 590 4500
- Sitio: www.udemedellin.edu.co

## 📄 Licencia

Propietario de la Universidad de Medellín © 2026

---

**Desarrollado con ❤️ por el equipo de tecnología UdeM**  
**Última actualización:** 31 de mayo de 2026
heroku create
git push heroku main
heroku config:set SECRET_KEY="<tu_secret>"
```

Notas
- El servidor ahora maneja respuestas streaming (SSE) si un plugin devuelve un generador.
- Se añadieron validaciones para evitar llamadas a OpenAI con claves placeholder.
- Se añadió una migración ligera para la columna `user_id` en la tabla `conversations`.

Si quieres, puedo agregar pruebas más completas o configurar CI (GitHub Actions).