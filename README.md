# Vivi - Asistente Virtual Universidad de Medellín

Chatbot inteligente para responder preguntas sobre carreras, matrículas, trámites, becas y servicios de la Universidad de Medellín.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso Local](#uso-local)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Información Disponible](#información-disponible)
- [Despliegue](#despliegue)
- [Tecnologías](#tecnologías)

## ✨ Características

### Chatbot Web
- 🎓 Información sobre carreras, facultades y programas
- 💰 Costos de matrícula 2026 por programa y escala
- 📄 Información sobre certificados (automáticos y manuales)
- 🎓 Proceso de grado y ceremonias
- 📋 Trámites y servicios académicos
- 💳 Becas y estímulos económicos
- 🌍 Centro de Idiomas
- 📞 Contactos e información de horarios
- 🏢 Detalles del campus

### Tecnología Inteligente
- **OpenRouter API** (GPT-4o-mini) para respuestas generales
- **Plugin de información institucional** con datos estructurados
- **Detección automática de contexto** - diferencia entre preguntas de costos vs carreras
- **Prioridad inteligente** - muestra información específica primero
- **Base de datos SQLite** para historial de conversaciones

## 📦 Requisitos

```
Python 3.11+
pip (gestor de paquetes Python)
```

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd C:\Users\[tu-usuario]\Documents\Vsproyects\Chatbot
```

### 2. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- Flask 3.1.3
- Flask-Login 0.6.3
- OpenAI (para OpenRouter)
- python-dotenv

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
PORT=9999
OPENROUTER_API_KEY=sk-or-v1-[tu-api-key]
OPENROUTER_MODEL=openai/gpt-4o-mini
SECRET_KEY=chatbot-dev-secret-key-12345-production-safe
FLASK_DEBUG=False
```

### Obtener API Key de OpenRouter

1. Ir a https://openrouter.ai
2. Crear cuenta
3. Generar API key
4. Copiar en `.env`

## 💻 Uso Local

### Iniciar el servidor

```bash
python app.py
```

**Acceder:**
```
http://localhost:9999
```

## 💰 Información de Matrículas 2026

### Por Facultad (Semestre)

| Facultad | Mínimo | Máximo |
|----------|--------|--------|
| Ciencias Económicas y Administrativas | $3.472.000 | $11.842.000 |
| Comunicación | $3.718.000 | $12.085.000 |
| Ingenierías | $3.718.000 | $12.085.000 |
| Derecho | $3.502.000 | $11.950.000 |
| Diseño | $3.718.000 | $12.085.000 |

**La escala (1-6) se asigna al ingresar y se MANTIENE durante toda la carrera.**

### Simulador: app.udem.edu.co/SimuladorArancel

## 📋 Información de Certificados 2026

### Automáticos (24-48 horas)
- Admisión: $24.000
- Matrícula vigente: $24.000
- Calificaciones concluidas: $92.000

### Manuales (3 días)
- Programa/asignaturas: $19.000
- Diploma duplicado: $295.000

## 🎓 Información de Grados 2026

- Ceremonia colectiva: $1.075.000
- Ceremonia privada: $2.029.000
- Sin ceremonia: $537.000

## 🌐 Opciones de Despliegue

### Heroku (Recomendado)

```bash
heroku create mi-vivi
heroku config:set OPENROUTER_API_KEY=sk-or-...
git push heroku main
```

### Railway.app

Conectar repositorio GitHub y deploy automático.

### Servidor Propio

```bash
git clone [repo]
pip install -r requirements.txt
python app.py
```

### Docker

```bash
docker build -t vivi .
docker run -p 5000:5000 -e OPENROUTER_API_KEY=sk-or-... vivi
```

## 📁 Estructura del Proyecto

```
Chatbot/
├── app.py                    # Servidor Flask
├── info_plugin.py            # Base de datos institucional
├── openai_plugin.py          # Integración OpenRouter
├── database.py               # SQLite
├── requirements.txt          # Dependencias
├── .env                      # Variables de entorno
├── chatbot.db               # Base de datos
└── static/                  # Archivos HTML/CSS/JS
```

## 🔧 Tecnologías

- **Flask 3.1.3** - Backend
- **SQLite 3** - Base de datos
- **OpenRouter API** - IA (GPT-4o-mini)
- **Python 3.11** - Lenguaje
- **HTML5/CSS3/JavaScript** - Frontend

## 📞 Contacto

**Email:** arion7754@gmail.com
**Universidad:** Universidad de Medellín

---

Última actualización: Junio 4, 2026
