#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='.')
CORS(app)

SECRET_KEY = 'udemedellin-super-secreto-2024'
DB_PATH = 'udem.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL UNIQUE,
        carrera TEXT,
        semestre INTEGER,
        promedio REAL,
        matricula TEXT UNIQUE,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS consultas_vivi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        mensaje TEXT,
        respuesta TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )''')
    try:
        admin_pass = generate_password_hash('admin123')
        c.execute('''INSERT INTO usuarios (email, username, password, is_admin)
                   VALUES (?, ?, ?, ?)''',
                 ('admin@udemedellin.edu.co', 'Administrador', admin_pass, 1))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def create_token(user_id, is_admin):
    payload = {'user_id': user_id, 'is_admin': is_admin, 'exp': datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except:
        return None

def get_current_user():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    payload = verify_token(token)
    if not payload:
        return None
    db = get_db()
    user = db.execute('SELECT * FROM usuarios WHERE id = ?', (payload['user_id'],)).fetchone()
    db.close()
    return user

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not all([email, username, password]) or len(password) < 6:
        return jsonify({'error': 'Datos invalidos'}), 400
    try:
        db = get_db()
        hashed_pass = generate_password_hash(password)
        db.execute('INSERT INTO usuarios (email, username, password, is_admin) VALUES (?, ?, ?, ?)',
                  (email, username, hashed_pass, 0))
        user_id = db.lastrowid
        db.execute('INSERT INTO estudiantes (usuario_id, carrera, semestre, promedio) VALUES (?, ?, ?, ?)',
                  (user_id, 'Por definir', 1, 0.0))
        db.commit()
        db.close()
        return jsonify({'message': 'Cuenta creada', 'user': {'id': user_id, 'email': email, 'username': username}}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email ya registrado'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    admin_key = data.get('adminKey', '')
    is_admin_attempt = data.get('isAdmin', False)
    if not email or not password:
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    if is_admin_attempt and admin_key != 'ADMIN2024':
        return jsonify({'error': 'Código de administrador incorrecto'}), 401
    try:
        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        db.close()
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        if is_admin_attempt and not user['is_admin']:
            return jsonify({'error': 'No tienes permisos de administrador'}), 403
        db = get_db()
        db.execute('UPDATE usuarios SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
        db.commit()
        db.close()
        token = create_token(user['id'], user['is_admin'])
        return jsonify({'token': token, 'user': {'id': user['id'], 'email': user['email'], 'username': user['username'], 'is_admin': bool(user['is_admin'])}}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    db = get_db()
    estudiante = db.execute('SELECT * FROM estudiantes WHERE usuario_id = ?', (user['id'],)).fetchone()
    db.close()
    return jsonify({'user': {'id': user['id'], 'email': user['email'], 'username': user['username'], 'is_admin': bool(user['is_admin']), 'estudiante': dict(estudiante) if estudiante else None}}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower().strip()
    user = get_current_user()

    response = None

    if 'sistemas' in message or 'software' in message or 'programacion' in message:
        response = '''**INGENIERÍA DE SISTEMAS** - Transforma con tecnología

Crea soluciones digitales que revolucionan industrias.

PERFIL: Especializado en desarrollo de software, análisis de datos, transformación digital.

CAMPOS LABORALES:
• Desarrollo de aplicaciones móviles y web
• Cloud Computing (AWS, Azure, Google Cloud)
• Ciberseguridad e infraestructura TI
• Big Data y Ciencia de Datos
• Startup tecnológicas y fintech

DIFERENCIALES:
• Certificaciones Cloud: AWS, Azure
• Convenios con Google, Microsoft, AWS
• Prácticas pagadas en empresas tech
• 98% de empleabilidad
• Salario inicial: $3,000,000 - $4,500,000'''

    elif 'civil' in message or 'construcción' in message:
        response = '''**INGENIERÍA CIVIL** - Construye el futuro

Diseña, construye y mantiene infraestructuras.

PERFIL: Profesional capacitado para diseñar estructuras sostenibles.

CAMPOS LABORALES:
• Empresas constructoras
• Infraestructura vial y transporte
• Obras hidráulicas y sanitarias
• Consultoría técnica
• Entidades gubernamentales

DIFERENCIALES:
• Laboratorio de Mecánica de Suelos
• Convenios con empresas constructoras
• Prácticas en obras reales
• 96% de empleabilidad
• Salario inicial: $2,500,000 - $3,500,000'''

    elif 'derecho' in message or 'abogado' in message:
        response = '''**DERECHO** - Defiende la justicia

Programa estrella con 96% de aprobación en examen de Estado.

PERFIL: Abogado profesional capaz de defender derechos.

CAMPOS LABORALES:
• Ejercicio profesional independiente
• Despachos de abogados Top 10
• Asesoría legal corporativa
• Justicia y entidades públicas
• Derecho internacional

DIFERENCIALES:
• 96% DE APROBACIÓN EN EXAMEN DE ESTADO
• Convenios con firmas de abogados Top 10
• Clínica jurídica con casos reales
• Salario inicial: $3,500,000 - $6,000,000'''

    elif 'beca' in message or 'financiación' in message or 'financiacion' in message:
        response = '''**BECAS Y FINANCIACIÓN - 5 Opciones**

1. **Beca de Mérito Académico** - Hasta 100%
   Para estudiantes con desempeño sobresaliente
   Requisito: ICFES 90 percentil+

2. **Beca Socioeconómica** - Hasta 80%
   Para estudiantes de recursos limitados
   Requisito: Análisis socioeconómico

3. **Beca Deportiva** - Hasta 75%
   Para atletas de nivel nacional/internacional

4. **Becas por Convenio** - 30%-100%
   Acuerdos con empresas

5. **Beca por Desempeño** - Hasta 50%
   Reconoce excelencia durante tus estudios
   Requisito: Promedio 4.2+

Contacto: becas@udemedellin.edu.co
Tel: +57 (604) 590-4500 ext. 1234'''

    else:
        response = '''¡Hola! Soy Vivi, asistente de UdeMedellin.

Puedo ayudarte con:
• **Carreras**: Ingeniería (Civil, Sistemas, etc), Derecho, Administración
• **Becas**: Mérito, Socioeconómica, Deportiva, Convenios
• **Admisiones**: Inscripción, requisitos, proceso
• **Campus**: Ubicación, instalaciones, infraestructura

¿Sobre qué te gustaría saber? Escribe una carrera o tema.'''

    # Guardar consulta
    if user:
        db = get_db()
        db.execute('INSERT INTO consultas_vivi (usuario_id, mensaje, respuesta) VALUES (?, ?, ?)',
                  (user['id'], message, response))
        db.commit()
        db.close()

    return jsonify({'response': response}), 200

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    user = get_current_user()
    if not user or not user['is_admin']:
        return jsonify({'error': 'No autorizado'}), 401
    db = get_db()
    users = db.execute('SELECT id, email, username, is_admin, created_at FROM usuarios').fetchall()
    db.close()
    return jsonify({'users': [dict(u) for u in users]}), 200

@app.route('/api/admin/analytics', methods=['GET'])
def get_analytics():
    user = get_current_user()
    if not user or not user['is_admin']:
        return jsonify({'error': 'No autorizado'}), 401
    db = get_db()
    total_users = db.execute('SELECT COUNT(*) as count FROM usuarios').fetchone()['count']
    total_consultas = db.execute('SELECT COUNT(*) as count FROM consultas_vivi').fetchone()['count']
    db.close()
    return jsonify({'total_users': total_users, 'total_consultas': total_consultas}), 200

@app.route('/')
def index():
    return send_from_directory('.', 'interfaz.html')

@app.route('/<path:filename>')
def static_file(filename):
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return send_from_directory('static', filename), 404

if __name__ == '__main__':
    init_db()
    print("[INIT] Servidor en http://localhost:9999")
    print("[ADMIN] Admin: admin@udemedellin.edu.co / admin123")
    print("[KEY] Código: ADMIN2024")
    app.run(debug=False, host='127.0.0.1', port=9999, threaded=True)
