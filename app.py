from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, render_template_string
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from dotenv import load_dotenv
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import database as db

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, email, is_admin=False):
        self.id = user_id
        self.username = username
        self.email = email
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(int(user_id))
    if user_data:
        return User(
            user_data['id'],
            user_data['username'],
            user_data['email'],
            user_data.get('is_admin', False)
        )
    return None

# Configuración
SYSTEM_PROMPT = """
Eres un asistente virtual amigable y profesional de la Universidad de Medellín.

Información importante que debes conocer:

CONTACTOS:
- Teléfono: +57 (604) 590 45 00 – +57 (604) 590 6999
- Sede principal: Cra. 87 #30-65, Medellín, Belén – Colombia
- Sede Bogotá: Calle 57 # 9-52, Chapinero
- Notificaciones judiciales: corresrec@udemedellin.edu.co

HORARIO DE ATENCIÓN:
- Lunes a viernes de 8:00 a.m. a 12:00 m. y de 2:00 p.m. a 6:00 p.m.

CARRERAS DISPONIBLES:
- Administración de Empresas (SNIES: 1514)
- Ciencia Política (SNIES: 105770)
- Computación Científica (SNIES: 103268)
- Comunicación Gráfica Publicitaria (SNIES: 11128)
- Comunicación y Entretenimiento Digital (SNIES: 103763)
- Comunicación y Lenguajes Audiovisuales (SNIES: 14880)
- Comunicación y Relaciones Corporativas (SNIES: 3136)
- Derecho (SNIES: 1512)
- Diseño y Gestión de Espacios (SNIES: 105470)
- Diseño y Gestión de la Moda y el Textil (SNIES: 105469)
- Diseño y Gestión del Producto (SNIES: 105468)
- Economía (SNIES: 1513)
- Ingeniería Ambiental (SNIES: 3193)
- Ingeniería Civil (SNIES: 1516)
- Ingeniería de Sistemas (SNIES: 3134)
- Ingeniería Financiera (SNIES: 7255)
- Ingeniería Industrial (SNIES: 103149)
- Investigación Criminal (SNIES: 90781)
- Mercadeo (SNIES: 52403)
- Negocios Internacionales (SNIES: 15243)
- Psicología

BECAS Y ESTÍMULOS:
- BECA SOCIAL
- BECA DE HONOR
- BECA DE EXCELENCIA
- BECA MEJORES SABER PRO
- ESTÍMULOS MONITORÍAS ACADÉMICAS
- ESTÍMULOS ACTIVIDADES DEPORTIVAS
- ESTÍMULOS ACTIVIDADES CULTURALES Y ARTÍSTICAS
- ESTÍMULO PARA PARTICIPACIONES DESTACADAS EN EVENTOS ACADÉMICOS EXTRACURRICULARES DE RECONOCIDO PRESTIGIO NACIONAL E INTERNACIONAL
- ESTÍMULO MULTILINGÜISMO

La institución es de educación superior sujeta a la inspección y vigilancia del Ministerio de Educación Nacional. Ofrece programas de Pregrado y Postgrado.

Responde de forma clara, cortés y útil usando esta información. Cuando pregunten por admisiones, pregúntale si le interesa Pregrado o Postgrado. Si no conoces algo, indícalo honestamente.
"""

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
MAX_HISTORY = 15

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index') if not current_user.is_admin else url_for('admin_dashboard'))

    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Iniciar Sesión - Universidad de Medellín</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #d32f2f, #8b0000); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .login-container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
            .logo { text-align: center; margin-bottom: 30px; }
            .logo-icon { width: 60px; height: 70px; margin: 0 auto; background: #d32f2f; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px; }
            h1 { color: #333; font-size: 24px; margin-bottom: 10px; }
            p.subtitle { color: #666; font-size: 14px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; color: #333; font-weight: 500; margin-bottom: 8px; }
            input { width: 100%; padding: 12px 15px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; transition: border-color 0.3s; }
            input:focus { outline: none; border-color: #d32f2f; }
            button { width: 100%; padding: 14px; background: #d32f2f; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.3s; }
            button:hover { background: #b71c1c; }
            .links { text-align: center; margin-top: 20px; }
            .links a { color: #d32f2f; text-decoration: none; font-size: 14px; }
            .links a:hover { text-decoration: underline; }
            .error { background: #ffebee; color: #c62828; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
            .success { background: #e8f5e9; color: #2e7d32; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">
                <div class="logo-icon">UDM</div>
                <h1>Universidad de Medellín</h1>
                <p class="subtitle">Asistente Virtual</p>
            </div>
            {% if error %}<div class="error">{{ error }}</div>{% endif %}
            {% if success %}<div class="success">{{ success }}</div>{% endif %}
            <form method="POST">
                <div class="form-group">
                    <label for="email">Correo electrónico</label>
                    <input type="email" id="email" name="email" placeholder="tu@correo.com" required>
                </div>
                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <input type="password" id="password" name="password" placeholder="Tu contraseña" required>
                </div>
                <button type="submit">Iniciar Sesión</button>
            </form>
            <div class="links">
                <p>¿No tienes cuenta? <a href="/register">Regístrate aquí</a></p>
                <p style="margin-top: 10px;"><a href="/">Volver al chat</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Registrarse - Universidad de Medellín</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #d32f2f, #8b0000); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .register-container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
            .logo { text-align: center; margin-bottom: 30px; }
            .logo-icon { width: 60px; height: 70px; margin: 0 auto; background: #d32f2f; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px; }
            h1 { color: #333; font-size: 24px; margin-bottom: 10px; }
            p.subtitle { color: #666; font-size: 14px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; color: #333; font-weight: 500; margin-bottom: 8px; }
            input { width: 100%; padding: 12px 15px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; transition: border-color 0.3s; }
            input:focus { outline: none; border-color: #d32f2f; }
            button { width: 100%; padding: 14px; background: #d32f2f; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.3s; }
            button:hover { background: #b71c1c; }
            .links { text-align: center; margin-top: 20px; }
            .links a { color: #d32f2f; text-decoration: none; font-size: 14px; }
            .links a:hover { text-decoration: underline; }
            .error { background: #ffebee; color: #c62828; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="register-container">
            <div class="logo">
                <div class="logo-icon">UDM</div>
                <h1>Universidad de Medellín</h1>
                <p class="subtitle">Asistente Virtual</p>
            </div>
            {% if error %}<div class="error">{{ error }}</div>{% endif %}
            <form method="POST">
                <div class="form-group">
                    <label for="username">Nombre completo</label>
                    <input type="text" id="username" name="username" placeholder="Tu nombre" required>
                </div>
                <div class="form-group">
                    <label for="email">Correo electrónico</label>
                    <input type="email" id="email" name="email" placeholder="tu@correo.com" required>
                </div>
                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <input type="password" id="password" name="password" placeholder="Mínimo 6 caracteres" required>
                </div>
                <button type="submit">Crear Cuenta</button>
            </form>
            <div class="links">
                <p>¿Ya tienes cuenta? <a href="/login">Inicia sesión</a></p>
                <p style="margin-top: 10px;"><a href="/">Volver al chat</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user_data = db.get_user_by_email(email)
    if user_data and check_password_hash(user_data['password_hash'], password):
        user = User(user_data['id'], user_data['username'], user_data['email'], user_data.get('is_admin', False))
        login_user(user)

        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))

    return render_template_string('''
    {% set error = "Credenciales incorrectas" %}
    ''' + login.__html__().replace('{% if error %}', '{% if True %}').replace('{{ error }}', error), error="Credenciales incorrectas")

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if len(password) < 6:
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="es">
        <head><meta charset="UTF-8"><title>Error</title></head>
        <body>
            <script>alert('La contraseña debe tener al menos 6 caracteres'); window.location='/register';</script>
        </body>
        </html>
        ''')

    existing = db.get_user_by_email(email)
    if existing:
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="es">
        <head><meta charset="UTF-8"><title>Error</title></head>
        <body>
            <script>alert('Este correo ya está registrado'); window.location='/register';</script>
        </body>
        </html>
        ''')

    password_hash = generate_password_hash(password)
    db.create_user(username, email, password_hash)

    return redirect(url_for('login', success='Cuenta creada exitosamente. Por favor inicia sesión.'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    html = '''
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Administración - Universidad de Medellín</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
            .header { background: #d32f2f; color: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
            .header h1 { font-size: 24px; }
            .header a { color: white; text-decoration: none; }
            .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .stat-card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat-card h3 { color: #666; font-size: 14px; text-transform: uppercase; }
            .stat-card .value { color: #d32f2f; font-size: 36px; font-weight: bold; margin-top: 10px; }
            .section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
            .section h2 { color: #333; margin-bottom: 20px; border-bottom: 2px solid #d32f2f; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { text-align: left; padding: 15px; border-bottom: 1px solid #eee; }
            th { color: #666; font-weight: 600; }
            .badge { padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
            .badge-admin { background: #d32f2f; color: white; }
            .badge-user { background: #4caf50; color: white; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Panel de Administración</h1>
            <div>
                <span>Bienvenido, {{ current_user.username }}</span> |
                <a href="/logout">Cerrar sesión</a>
            </div>
        </div>
        <div class="container">
            <div class="stats">
                <div class="stat-card">
                    <h3>Usuarios</h3>
                    <div class="value" id="statUsers">-</div>
                </div>
                <div class="stat-card">
                    <h3>Conversaciones</h3>
                    <div class="value" id="statConversations">-</div>
                </div>
                <div class="stat-card">
                    <h3>Respuestas Aprendidas</h3>
                    <div class="value" id="statLearned">-</div>
                </div>
            </div>
            <div class="section">
                <h2>Gestión de Usuarios</h2>
                <div id="usersList">Cargando...</div>
            </div>
            <div class="section">
                <h2>Preguntas para Revisión</h2>
                <div id="reviewList">Cargando...</div>
            </div>
        </div>
        <script>
            async function loadStats() {
                try {
                    const [users, convs, learned] = await Promise.all([
                        fetch('/api/admin/users').then(r => r.json()),
                        fetch('/api/admin/conversations').then(r => r.json()),
                        fetch('/api/admin/learned').then(r => r.json())
                    ]);
                    document.getElementById('statUsers').textContent = users.length || 0;
                    document.getElementById('statConversations').textContent = convs.length || 0;
                    document.getElementById('statLearned').textContent = learned.length || 0;
                } catch (e) { console.error(e); }
            }
            async function loadUsers() {
                const users = await fetch('/api/admin/users').then(r => r.json());
                document.getElementById('usersList').innerHTML = `
                    <table>
                        <tr><th>Usuario</th><th>Email</th><th>Tipo</th><th>Fecha</th></tr>
                        ${users.map(u => `<tr><td>${u.username}</td><td>${u.email}</td><td><span class="badge ${u.is_admin ? 'badge-admin' : 'badge-user'}">${u.is_admin ? 'Admin' : 'Usuario'}</span></td><td>${new Date(u.created_at).toLocaleDateString()}</td></tr>`).join('')}
                    </table>`;
            }
            async function loadReview() {
                const convs = await fetch('/api/admin/review').then(r => r.json());
                document.getElementById('reviewList').innerHTML = convs.length ? `
                    <table>
                        <tr><th>Pregunta</th><th>Respuesta</th><th>Votos</th></tr>
                        ${convs.map(c => `<tr><td>${c.question}</td><td>${c.answer}</td><td>↓${c.downvotes}</td></tr>`).join('')}
                    </table>` : '<p>No hay preguntas pendientes.</p>';
            }
            loadStats(); loadUsers(); loadReview();
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/api/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    conn = db.get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC")
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/admin/conversations')
@login_required
def admin_conversations():
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    conn = db.get_db()
    c = conn.cursor()
    c.execute("SELECT id, question, answer, topic, upvotes, downvotes, created_at FROM conversations ORDER BY created_at DESC LIMIT 100")
    convs = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(convs)

@app.route('/api/admin/learned')
@login_required
def admin_learned():
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    learned = db.get_all_learned_responses()
    return jsonify(learned)

@app.route('/api/admin/review')
@login_required
def admin_review():
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    questions = db.get_unknown_questions()
    return jsonify(questions)

@app.route('/chatbot.js')
def chatbot_js():
    return send_from_directory('static', 'chatbot.js')

@app.route('/styles.css')
def styles_css():
    return send_from_directory('static', 'styles.css')

def try_ollama(prompt: str):
    """Usar Ollama para generar respuesta."""
    model = os.environ.get('OLLAMA_MODEL', DEFAULT_MODEL)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300,
                }
            },
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
    except Exception as e:
        print(f"Ollama error: {e}")

    return None

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Mensaje vacío'}), 400

        # Usar Ollama como IA principal
        ollama_response = try_ollama(user_message)
        if ollama_response:
            return jsonify({'response': ollama_response, 'ai': True})

        # Fallback a respuestas locales si Ollama no está disponible
        fallback_response = get_fallback_response(user_message)
        return jsonify({'response': fallback_response, 'ai': False})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_fallback_response(prompt):
    """Respuestas de respaldo si Ollama no está disponible."""
    prompt_lower = prompt.lower()

    faq = {
        'horario': 'Horario de atención: Lunes a viernes de 8:00 a.m. a 12:00 m. y de 2:00 p.m. a 6:00 p.m.',
        'hora': 'Horario de atención: Lunes a viernes de 8:00 a.m. a 12:00 m. y de 2:00 p.m. a 6:00 p.m.',
        'atencion': 'Horario de atención: Lunes a viernes de 8:00 a.m. a 12:00 m. y de 2:00 p.m. a 6:00 p.m.',
        'ubicacion': 'Sede principal: Cra. 87 #30-65, Medellín, Belén – Colombia. Sede Bogotá: Calle 57 # 9-52, Chapinero.',
        'donde': 'Sede principal: Cra. 87 #30-65, Medellín, Belén – Colombia. Sede Bogotá: Calle 57 # 9-52, Chapinero.',
        'direccion': 'Sede principal: Cra. 87 #30-65, Medellín, Belén – Colombia. Sede Bogotá: Calle 57 # 9-52, Chapinero.',
        'medellin': 'La sede principal está en Cra. 87 #30-65, Medellín, Belén – Colombia.',
        'bogota': 'La sede de Bogotá está en Calle 57 # 9-52, Chapinero.',
        'carrera': 'Tenemos 22 carreras disponibles: Administración de Empresas, Ciencia Política, Computación Científica, Comunicación Gráfica Publicitaria, Comunicación y Entretenimiento Digital, Comunicación y Lenguajes Audiovisuales, Comunicación y Relaciones Corporativas, Derecho, Diseño y Gestión de Espacios, Diseño y Gestión de la Moda y el Textil, Diseño y Gestión del Producto, Economía, Ingeniería Ambiental, Ingeniería Civil, Ingeniería de Sistemas, Ingeniería Financiera, Ingeniería Industrial, Investigación Criminal, Mercadeo, Negocios Internacionales y Psicología.',
        'carreras': 'Tenemos 22 carreras disponibles: Administración de Empresas, Ciencia Política, Computación Científica, Comunicación Gráfica Publicitaria, Comunicación y Entretenimiento Digital, Comunicación y Lenguajes Audiovisuales, Comunicación y Relaciones Corporativas, Derecho, Diseño y Gestión de Espacios, Diseño y Gestión de la Moda y el Textil, Diseño y Gestión del Producto, Economía, Ingeniería Ambiental, Ingeniería Civil, Ingeniería de Sistemas, Ingeniería Financiera, Ingeniería Industrial, Investigación Criminal, Mercadeo, Negocios Internacionales y Psicología.',
        'ingenieria': 'Sí, ofrecemos Ingeniería Ambiental, Ingeniería Civil, Ingeniería de Sistemas, Ingeniería Financiera e Ingeniería Industrial.',
        'comunicacion': 'Sí, ofrecemos Comunicación Gráfica Publicitaria, Comunicación y Entretenimiento Digital, Comunicación y Lenguajes Audiovisuales y Comunicación y Relaciones Corporativas.',
        'administracion': 'Sí, ofrecemos Administración de Empresas.',
        'psicologia': 'Sí, ofrecemos Psicología.',
        'derecho': 'Sí, ofrecemos Derecho.',
        'contacto': 'Teléfono: +57 (604) 590 45 00 – +57 (604) 590 6999. Notificaciones judiciales: corresrec@udemedellin.edu.co',
        'telefono': 'Teléfono: +57 (604) 590 45 00 – +57 (604) 590 6999',
        'email': 'Notificaciones judiciales: corresrec@udemedellin.edu.co',
        'correo': 'Notificaciones judiciales: corresrec@udemedellin.edu.co',
        'beca': 'Becas disponibles: BECA SOCIAL, BECA DE HONOR, BECA DE EXCELENCIA, BECA MEJORES SABER PRO, ESTÍMULOS MONITORÍAS ACADÉMICAS, ESTÍMULOS ACTIVIDADES DEPORTIVAS, ESTÍMULOS ACTIVIDADES CULTURALES Y ARTÍSTICAS, ESTÍMULO PARA PARTICIPACIONES DESTACADAS EN EVENTOS ACADÉMICOS EXTRACURRICULARES, ESTÍMULO MULTILINGÜISMO.',
        'becas': 'Becas disponibles: BECA SOCIAL, BECA DE HONOR, BECA DE EXCELENCIA, BECA MEJORES SABER PRO, ESTÍMULOS MONITORÍAS ACADÉMICAS, ESTÍMULOS ACTIVIDADES DEPORTIVAS, ESTÍMULOS ACTIVIDADES CULTURALES Y ARTÍSTICAS, ESTÍMULO PARA PARTICIPACIONES DESTACADAS EN EVENTOS ACADÉMICOS EXTRACURRICULARES, ESTÍMULO MULTILINGÜISMO.',
        'estímulos': 'Tenemos varios estímulos: Monitorías Académicas, Actividades Deportivas, Actividades Culturales y Artísticas, Participaciones Destacadas en Eventos Académicos Extracurriculares y Multilingüismo.',
        'admision': 'La Universidad de Medellín ofrece programas de Pregrado y Postgrado. ¿Te interesa información sobre cuál de los dos? (Indícame si deseas explorar programas de Pregrado o Postgrado)',
        'ministerio': 'La institución es de educación superior sujeta a la inspección y vigilancia del Ministerio de Educación Nacional.',
    }

    for keyword, answer in faq.items():
        if keyword in prompt_lower:
            return answer

    if any(word in prompt_lower for word in ['hola', 'buenas', 'saludos']):
        return '¡Hola! Soy el asistente virtual de la Universidad de Medellín. ¿En qué puedo ayudarte?'

    if any(word in prompt_lower for word in ['gracias', 'muchas gracias']):
        return '¡De nada! Si tienes más preguntas, estaré aquí para ayudarte.'

    return 'Lo siento, no tengo información específica sobre eso. Puedo ayudarte con información sobre carreras, contacto, horarios y becas. ¿Podrías preguntar algo más específico?'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
