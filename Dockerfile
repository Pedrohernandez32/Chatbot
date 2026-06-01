# Multi-stage build para optimizar tamaño de imagen

# ==================== STAGE 1: Builder ====================
FROM python:3.9-slim as builder

WORKDIR /app

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ==================== STAGE 2: Runtime ====================
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    redis-server \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar Python packages de builder
COPY --from=builder /root/.local /root/.local

# Copiar aplicación
COPY . .

# Variables de entorno
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=server.py
ENV FLASK_ENV=production

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/data /app/tmp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Exponer puerto
EXPOSE 5000

# Iniciar aplicación
CMD ["python", "server.py"]
