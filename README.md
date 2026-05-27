# Chatbot — Universidad

Proyecto de chatbot para preguntas sobre la universidad.

Requisitos
- Python 3.11
- Crear y activar el entorno virtual (se incluye .venv local en este repo)
- Instalar dependencias:

```bash
pip install -r requirements.txt
```

Variables de entorno (opcional)
- `SECRET_KEY` — secreto de Flask.
- `OPENAI_API_KEY` — si quieres usar OpenAI, pon aquí tu clave. Si no está definida, el servidor funcionará con los handlers locales (`ai_plugin`, RAG y Ollama serán saltados si no están disponibles).
- `OLLAMA` — si usas Ollama local, verifica que esté corriendo en `http://localhost:11434`.
 - RAG fallback: si no se configura `OPENAI_API_KEY`, el `rag_plugin` devuelve un extracto de los documentos indexados como respuesta local.

Arrancar el servidor

```bash
python server.py
# o
python app.py
```

Probar el endpoint `/api/chat` (ejemplo con `curl` en Windows PowerShell usa `curl.exe`):

```bash
curl.exe -X POST -H "Content-Type: application/json" -d "{\"message\":\"hola\"}" http://127.0.0.1:5000/api/chat
```

Test rápido en Python

```bash
python tests/test_chat.py
```

Test con Flask test client (unit):

```bash
pytest -q
```

Despliegue (Heroku/Gunicorn ejemplo)

```bash
pip install gunicorn
# Procfile incluido en el repo
heroku create
git push heroku main
heroku config:set SECRET_KEY="<tu_secret>"
```

Notas
- El servidor ahora maneja respuestas streaming (SSE) si un plugin devuelve un generador.
- Se añadieron validaciones para evitar llamadas a OpenAI con claves placeholder.
- Se añadió una migración ligera para la columna `user_id` en la tabla `conversations`.

Si quieres, puedo agregar pruebas más completas o configurar CI (GitHub Actions).