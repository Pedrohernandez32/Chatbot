from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, render_template, Response, stream_with_context
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from dotenv import load_dotenv
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import database as db

# Plugins
import ai_plugin
import ollama_plugin
import rag_plugin
import tool_plugin
import openai_plugin

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

# Bot Engine
class Bot:
    def __init__(self):
        self.handlers = []

    def register_handler(self, handler):
        self.handlers.append(handler)

    def handle(self, prompt: str, user_id: Optional[int] = None):
        # Add memory/context if user_id is provided
        context = ""
        if user_id:
            history = db.get_user_history(user_id)
            if history:
                context = "Contexto de la conversación actual:\n" + "\n".join([f"{h['role']}: {h['content']}" for h in history]) + "\n\n"

        augmented_prompt = context + prompt if context else prompt

        for handler in self.handlers:
            response = handler(augmented_prompt)
            if response:
                return response, True if "plugin" in handler.__module__ else False
        return "Lo siento, no tengo información específica sobre eso. ¿Podrías preguntar de otra forma?", False

bot = Bot()

# Register Plugins in order of priority
rag_plugin.register(bot)       # 1. Knowledge Base (Official docs)
ai_plugin.register(bot)        # 2. Semantic FAQ
ollama_plugin.register(bot)    # 3. Local LLM
openai_plugin.register(bot)   # 4. Cloud LLM (Fallback)
tool_plugin.register(bot)       # 5. Utilities

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

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index') if not current_user.is_admin else url_for('admin_dashboard'))
    return render_template('login.html')

@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('register.html')

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
    return render_template('login.html', error="Credenciales incorrectas")

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    if len(password) < 6:
        return render_template('register.html', error='La contraseña debe tener al menos 6 caracteres')
    existing = db.get_user_by_email(email)
    if existing:
        return render_template('register.html', error='Este correo ya está registrado')
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
    return render_template('admin.html')

# Admin API
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

@app.route('/api/admin/advisor_requests')
@login_required
def admin_advisor_requests():
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    requests = db.get_advisor_requests()
    return jsonify(requests)

@app.route('/api/admin/advisor_request/<int:request_id>/status', methods=['POST'])
@login_required
def update_advisor_status(request_id):
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    status = request.json.get('status', 'pending')
    db.update_advisor_request_status(request_id, status)
    return jsonify({'success': True})

@app.route('/chatbot.js')
def chatbot_js():
    return send_from_directory('static', 'chatbot.js')

@app.route('/styles.css')
def styles_css():
    return send_from_directory('static', 'styles.css')

@app.route('/api/advisor', methods=['POST'])
def advisor_request():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message')
        if not name or not email or not message:
            return jsonify({'error': 'Faltan campos obligatorios'}), 400
        request_id = db.create_advisor_request(name, email, phone, message)
        return jsonify({'success': True, 'id': request_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Mensaje vacío'}), 400

        user_id = current_user.id if current_user.is_authenticated else None

        # The bot handle now returns either a string or a generator
        result = bot.handle(user_message, user_id=user_id)
        response_content, is_ai = result

        if isinstance(response_content, (list, tuple)) or hasattr(response_content, '__iter__') and not isinstance(response_content, (str, bytes)):
            # It's a generator (streaming)
            def generate():
                full_response = ""
                for chunk in response_content:
                    full_response += chunk
                    yield f"data: {jsonify({'chunk': chunk}).get_data(as_text=True)}\n\n"

                # Save to DB after stream finishes
                db.save_conversation(user_message, full_response, user_id=user_id)
                yield f"data: {jsonify({'done': True}).get_data(as_text=True)}\n\n"

            return Response(stream_with_context(generate()), mimetype='text/event-stream')
        else:
            # Standard string response
            db.save_conversation(user_message, response_content, user_id=user_id)
            return jsonify({'response': response_content, 'ai': is_ai})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
