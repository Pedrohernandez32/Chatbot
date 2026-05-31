from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, render_template, Response, stream_with_context
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from dotenv import load_dotenv
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import database as db
import inspect
from typing import Optional
from urllib.parse import quote_plus
import re
import logging

# Plugins
import info_plugin
import portal_plugin
import ai_plugin
import rag_plugin
import ollama_plugin
import openai_plugin
import tool_plugin

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return len(email) <= 120 and re.match(pattern, email) is not None

def validate_username(username: str) -> bool:
    return 3 <= len(username) <= 50 and re.match(r'^[a-zA-Z0-9_-]+$', username) is not None

app = Flask(__name__)
CORS(app)
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError('SECRET_KEY environment variable must be set')
app.secret_key = secret_key

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
            # If ai_plugin gives a generic hint message, treat as no-answer and continue
            try:
                mod_name = handler.__module__
            except Exception:
                mod_name = ""

            if response:
                if mod_name == 'ai_plugin' and isinstance(response, str) and response.startswith("Sobre la universidad puedo decirte"):
                    # Not a specific answer; continue to next handler or fallback to LLMs
                    response = None

            if response:
                return response, True if "plugin" in mod_name else False

        # No plugin returned a concrete answer — attempt AI fallbacks (local Ollama, then OpenAI)
        try:
            # Prefer Ollama (may return a generator for streaming)
            ollama_resp = None
            try:
                ollama_resp = ollama_plugin.ollama_handler(augmented_prompt)
            except Exception:
                ollama_resp = None

            if ollama_resp:
                return ollama_resp, True

            # Next try OpenAI (synchronous string response)
            try:
                openai_resp = openai_plugin.openai_handler(augmented_prompt)
            except Exception:
                openai_resp = None

            if openai_resp:
                return openai_resp, True
        except Exception:
            pass

        return "Lo siento, no tengo información específica sobre eso. ¿Podrías preguntar de otra forma?", False

bot = Bot()

# Register Plugins in order of priority
# 1. Institutional info (from app.py SYSTEM_PROMPT)
info_plugin.register(bot)
# 1.5 Portal scraper (fetch official site)
portal_plugin.register(bot)
# 2. Semantic FAQ
ai_plugin.register(bot)
# 3. Knowledge Base (Official docs)
rag_plugin.register(bot)
# 4. Local LLM
ollama_plugin.register(bot)
# 5. Cloud LLM (Fallback)
openai_plugin.register(bot)
# 6. Utilities
tool_plugin.register(bot)

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
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not validate_email(email):
        return render_template('login.html', error='Email inválido')

    user_data = db.get_user_by_email(email)
    if user_data and check_password_hash(user_data['password_hash'], password):
        user = User(user_data['id'], user_data['username'], user_data['email'], user_data.get('is_admin', False))
        login_user(user)
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
    return render_template('login.html', error='Credenciales incorrectas')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not validate_username(username):
        return render_template('register.html', error='Username debe tener 3-50 caracteres alfanuméricos')
    if not validate_email(email):
        return render_template('register.html', error='Email inválido')
    if len(password) < 8:
        return render_template('register.html', error='Contraseña debe tener al menos 8 caracteres')

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
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        phone = (data.get('phone') or '').strip()
        message = (data.get('message') or '').strip()

        if not name or not email or not message:
            return jsonify({'error': 'Faltan campos obligatorios'}), 400
        if len(name) > 100 or not re.match(r'^[a-zA-Z\s\-\.\'áéíóúñ]+$', name):
            return jsonify({'error': 'Nombre inválido'}), 400
        if not validate_email(email):
            return jsonify({'error': 'Email inválido'}), 400
        if phone and not re.match(r'^[\d\s\-\+()]+$', phone):
            return jsonify({'error': 'Teléfono inválido'}), 400
        if len(message) > 1000:
            return jsonify({'error': 'Mensaje muy largo'}), 400

        request_id = db.create_advisor_request(name, email, phone, message)
        return jsonify({'success': True, 'id': request_id})
    except Exception as e:
        logger.error(f"Advisor request error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error procesando solicitud'}), 500


@app.route('/api/advisor/connect', methods=['POST'])
def advisor_connect():
    """Solicita conexión inmediata con un asesor. Crea una solicitud y marca
    su estado como 'live_requested'. Devuelve datos de contacto del asesor si
    están configurados en variables de entorno.
    """
    try:
        data = request.get_json(silent=True) or {}
        if current_user.is_authenticated:
            name = getattr(current_user, 'username', 'Usuario')
            email = getattr(current_user, 'email', '')
            phone = data.get('phone') or None
        else:
            name = data.get('name') or data.get('full_name') or 'Usuario'
            email = data.get('email') or ''
            phone = data.get('phone') or None

        message = data.get('message') or 'Solicita conexión inmediata con un asesor.'

        req_id = db.create_advisor_request(name, email, phone, message)
        db.update_advisor_request_status(req_id, 'live_requested')

        contact = {}
        advisor_chat = os.environ.get('ADVISOR_CHAT_URL')
        advisor_phone = os.environ.get('ADVISOR_PHONE')
        advisor_email = os.environ.get('ADVISOR_EMAIL')
        advisor_whatsapp = os.environ.get('ADVISOR_WHATSAPP_NUMBER')

        if advisor_chat:
            contact['chat_url'] = advisor_chat
        if not advisor_chat and advisor_whatsapp:
            num = re.sub(r"\D", "", advisor_whatsapp)
            prefill = f"Hola, solicité conexión (ID: {req_id}). Mi nombre: {name}."
            wa_link = f"https://wa.me/{num}?text={quote_plus(prefill)}"
            contact['chat_url'] = wa_link
            # also provide phone for display
            contact['phone'] = advisor_whatsapp

        if advisor_phone and 'phone' not in contact:
            contact['phone'] = advisor_phone
        if advisor_email:
            contact['email'] = advisor_email

        return jsonify({'success': True, 'id': req_id, 'status': 'live_requested', 'contact': contact})
    except Exception as e:
        logger.error(f"Advisor connect error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error procesando solicitud'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Mensaje vacío'}), 400

        user_id = current_user.id if current_user.is_authenticated else None

        result = bot.handle(user_message, user_id=user_id)
        response_content, is_ai = result

        if not isinstance(response_content, (str, bytes)):
            def generate():
                full_response = ""
                try:
                    for chunk in response_content:
                        full_response += chunk
                        yield f"data: {jsonify({'chunk': chunk}).get_data(as_text=True)}\n\n"
                except Exception as e:
                    logger.error(f"Stream error: {str(e)}", exc_info=True)
                    yield f"data: {jsonify({'error': 'Error procesando respuesta'}).get_data(as_text=True)}\n\n"
                finally:
                    db.save_conversation(user_message, full_response, user_id=user_id)
                    yield f"data: {jsonify({'done': True}).get_data(as_text=True)}\n\n"

            return Response(stream_with_context(generate()), mimetype='text/event-stream')
        else:
            # Standard string response
            db.save_conversation(user_message, response_content, user_id=user_id)
            return jsonify({'response': response_content, 'ai': is_ai})

    except Exception as e:
        import logging
        logging.error(f"Chat error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error procesando tu mensaje. Intenta de nuevo.'}), 500

if __name__ == '__main__':
    try:
        db.init_db()
    except Exception as e:
        print('DB init error:', e)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, port=int(os.environ.get('PORT', 5000)))
