# 🚀 Guía de Deployment - Universidad de Medellín Chatbot

## Preparación para Producción

### 1. **Variables de Entorno**

Crea un archivo `.env` en la raíz del proyecto basado en `.env.example`:

```bash
cp .env.example .env
```

Configura las siguientes variables:

- `SECRET_KEY`: Genera una clave segura: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `OPENAI_API_KEY`: Tu API key de OpenAI (para fallback de preguntas generales)
- `DATABASE_URL`: Ruta de la base de datos (SQLite para desarrollo, PostgreSQL recomendado para producción)
- `ADMIN_CODE`: Código secreto para crear administradores

### 2. **Base de Datos**

Para producción, usa PostgreSQL en lugar de SQLite:

```bash
pip install psycopg2-binary
```

Actualiza `DATABASE_URL` en `.env`:
```
DATABASE_URL=postgresql://usuario:password@localhost:5432/udemedellin_chatbot
```

Inicializa la BD:
```bash
python -c "from database import init_db; init_db()"
```

### 3. **Servidor WSGI (Producción)**

Para producción, usa **Gunicorn** en lugar del servidor de desarrollo de Flask:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

**Parámetros recomendados:**
- `-w 4`: 4 workers (ajusta según CPU disponible)
- `-b 0.0.0.0:5000`: Escucha en todas las interfaces, puerto 5000
- `--access-logfile -`: Logs a stdout
- `--error-logfile -`: Logs de error a stderr

### 4. **HTTPS/SSL**

**Opción A: Let's Encrypt + Nginx**

```nginx
server {
    listen 443 ssl;
    server_name www.udemedellin.edu.co;
    
    ssl_certificate /etc/letsencrypt/live/www.udemedellin.edu.co/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.udemedellin.edu.co/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name www.udemedellin.edu.co;
    return 301 https://$server_name$request_uri;
}
```

### 5. **Seguridad**

Actualiza `server.py` para producción:

```python
# En settings de seguridad
app.config['SESSION_COOKIE_SECURE'] = True      # Solo HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True    # No accesible desde JS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # CSRF protection
```

### 6. **Optimización de Assets**

**CSS y JavaScript:**
- Minificación (usar herramientas como cssnano, terser)
- Bundling con Webpack o Rollup
- Compresión gzip en servidor

**Imágenes:**
- Usar formatos modernos (WebP con fallback)
- Lazy loading en elementos visibles
- Optimizar tamaño con TinyPNG o similar

### 7. **Caching**

Configura caching en Nginx:

```nginx
# Cache estático por 30 días
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Cache HTML por 1 hora
location ~* \.html$ {
    expires 1h;
    add_header Cache-Control "public";
}
```

### 8. **Monitoreo y Logging**

Configure logs para producción:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/chatbot.log', 
                                      maxBytes=10240000, 
                                      backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    app.logger.addHandler(file_handler)
```

### 9. **Docker (Opcional pero Recomendado)**

Crea un `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=server.py
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]
```

Crea `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/chatbot
      - FLASK_ENV=production
    depends_on:
      - db
    
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=chatbot
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 10. **Checklist Pre-Producción**

- [ ] Variables de entorno configuradas
- [ ] Base de datos migrada a PostgreSQL
- [ ] HTTPS habilitado
- [ ] Rate limiting activo
- [ ] Logs configurados
- [ ] Backups automáticos
- [ ] Tests ejecutados exitosamente
- [ ] Performance profiling completado
- [ ] SEO meta tags agregados
- [ ] Cache headers configurados
- [ ] CORS restricto a dominios permitidos
- [ ] Admin password cambiado
- [ ] Sensitive data no está en git

### 11. **Deployment en Producción**

**Opción 1: Heroku**
```bash
heroku create udemedellin-chatbot
git push heroku main
heroku config:set SECRET_KEY=tu-clave-secreta
heroku run python -c "from database import init_db; init_db()"
```

**Opción 2: DigitalOcean, Render, Railway**
- Conecta tu repositorio git
- Configura variables de entorno
- Deploy automático en cada push

**Opción 3: Servidor propio con PM2**
```bash
npm install -g pm2
pm2 start "gunicorn -w 4 -b 0.0.0.0:5000 server:app" --name chatbot
pm2 startup
pm2 save
```

---

**Última actualización:** 31 de mayo de 2026
