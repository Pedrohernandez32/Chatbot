from flask import Flask, request, jsonify, send_from_directory, session, Response, stream_with_context
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import timedelta, datetime
from collections import defaultdict
import html

from database import (
    get_db, init_db,
    save_conversation, vote_conversation, flag_for_review,
    get_learned_response, increment_learned_usage,
    get_unknown_questions, save_learned_response,
    get_all_learned_responses, delete_learned_response,
    get_user_by_email, get_user_by_id, create_user
)
from info_plugin import register as register_info_plugin
from ai_plugin import register as register_ai_plugin
from openai_plugin import register as register_openai_plugin
from ollama_plugin import register as register_ollama_plugin

app = Flask(__name__)
CORS(app)

# Load secret key from environment
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Rate limiting - simple in-memory implementation
class RateLimiter:
    def __init__(self, max_requests=30, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_id):
        now = datetime.now()
        # Limpiar requests antiguos
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if (now - req_time).seconds < self.window_seconds
        ]

        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False

chat_limiter = RateLimiter(max_requests=30, window_seconds=60)  # 30 requests per minute

def get_client_id():
    return request.remote_addr or 'unknown'

# Configure session settings for persistent login
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id, username, email, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(int(user_id))
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'], user_data['is_admin'])
    return None


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        user_data = get_user_by_id(current_user.id)
        if not user_data or not user_data.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# Auth routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields required'}), 400

    user_data = get_user_by_email(email)
    if user_data:
        return jsonify({'error': 'User already exists'}), 400

    password_hash = generate_password_hash(password)
    user_id = create_user(username, email, password_hash)

    return jsonify({'ok': True})


@app.route('/login')
def login_page():
    return send_from_directory('static', 'login.html')


@app.route('/register')
def register_page():
    return send_from_directory('static', 'register.html')


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', True)  # Remember by default
    adminKey = data.get('adminKey')
    isAdmin = data.get('isAdmin')

    user_data = get_user_by_email(email)
    if not user_data:
        return jsonify({'error': 'Invalid credentials'}), 401

    if check_password_hash(user_data['password_hash'], password):
        # If admin tab selected, verify the admin key matches the user's email domain or admin flag
        if isAdmin and adminKey:
            # Simple admin key check (in production, use proper secrets management)
            admin_key = os.environ.get('ADMIN_KEY', 'admin-secret-key')
            if adminKey != admin_key:
                return jsonify({'error': 'Clave de administrador incorrecta'}), 401
            # Force is_admin to True for this session
            user_data['is_admin'] = True

        user = User(user_data['id'], user_data['username'], user_data['email'], user_data['is_admin'])
        # Mark session as permanent so it persists across browser sessions
        session.permanent = True
        login_user(user, remember=remember)
        return jsonify({'user': {'id': user_data['id'], 'username': user_data['username'], 'email': user_data['email'], 'is_admin': user_data['is_admin']}})

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'ok': True})


@app.route('/api/auth/me', methods=['GET'])
def me():
    if current_user.is_authenticated:
        return jsonify({'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': current_user.is_admin
        }})
    return jsonify({'user': None})


# Admin routes
@app.route('/api/admin/unknown', methods=['GET'])
@admin_required
def unknown_questions():
    questions = get_unknown_questions(20)
    return jsonify({'questions': questions})


@app.route('/api/admin/learn', methods=['POST'])
@admin_required
def create_learned_response():
    data = request.get_json()
    question = data.get('question', '')
    answer = data.get('answer', '')
    keywords = data.get('keywords', question.lower())

    if not question or not answer:
        return jsonify({'error': 'question and answer required'}), 400

    save_learned_response(keywords, answer)
    return jsonify({'ok': True})


@app.route('/api/admin/learn', methods=['GET'])
@admin_required
def list_learned_responses():
    responses = get_all_learned_responses()
    return jsonify({'responses': responses})


@app.route('/api/admin/learn/<int:id>', methods=['DELETE'])
@admin_required
def delete_learned(id):
    delete_learned_response(id)
    return jsonify({'ok': True})


# Chat routes
class Bot:
    def __init__(self):
        self.handlers = []

    def register_handler(self, handler):
        self.handlers.append(handler)

    def process(self, prompt):
        for handler in self.handlers:
            response = handler(prompt)
            if response:
                return response
        return "No tengo información sobre eso. ¿Puedes reformular tu pregunta?"


bot = Bot()
# Register plugins: institutional info first, then FAQ, then local LLM, then cloud fallback
register_info_plugin(bot)
register_ai_plugin(bot)
register_ollama_plugin(bot)
register_openai_plugin(bot)


@app.route('/')
def index():
    """Interfaz principal: nuevo diseño React"""
    return send_from_directory('.', 'Asistente Virtual UdeMedellin.html')

@app.route('/asistente')
def asistente():
    """Alias para compatibilidad - redirige a la página principal"""
    return index()

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/assets/<path:filename>')
def assets_files(filename):
    """Sirve imágenes y assets"""
    return send_from_directory('assets', filename)

@app.route('/<path:filename>')
def serve_root_files(filename):
    """Sirve archivos JSX y CSS desde la raíz"""
    if filename.endswith(('.jsx', '.js', '.css', '.html')):
        return send_from_directory('.', filename)
    return send_from_directory('static', filename)


@app.route('/api/chat', methods=['POST'])
def chat():
    # 🔒 Rate limiting
    client_id = get_client_id()
    if not chat_limiter.is_allowed(client_id):
        return jsonify({'error': 'Demasiadas solicitudes. Intenta de nuevo en unos momentos.'}), 429

    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message or len(message) > 1000:
            return jsonify({'error': 'Mensaje inválido'}), 400

        user_id = current_user.id if current_user.is_authenticated else None

        # Process message and get response (with fallback)
        default_response = "No tengo información específica sobre eso. ¿Puedes reformular tu pregunta? Puedo ayudarte con información sobre carreras, horarios, ubicación, contacto, becas e inscripciones."

        try:
            bot_response = bot.process(message)
        except Exception as e:
            print(f"Bot error: {str(e)}")
            bot_response = None

        # If a plugin returned a streaming generator (e.g. Ollama), stream it as SSE
        if bot_response and not isinstance(bot_response, (str, bytes)):
            def generate():
                full_text = ""
                try:
                    for chunk in bot_response:
                        if not chunk:
                            continue
                        full_text += chunk
                        yield f"data: {jsonify({'chunk': chunk}).get_data(as_text=True)}\n\n"
                except Exception as e:
                    yield f"data: {jsonify({'error': str(e)}).get_data(as_text=True)}\n\n"
                finally:
                    try:
                        save_conversation(message, full_text, user_id=user_id)
                    except Exception:
                        pass
                    yield f"data: {jsonify({'done': True}).get_data(as_text=True)}\n\n"

            return Response(stream_with_context(generate()), mimetype='text/event-stream')

        # Standard (non-stream) response handling
        response = default_response
        if bot_response:
            response = bot_response

        # Save conversation with user_id to get real conv_id
        try:
            conv_id = save_conversation(message, response, user_id=user_id)
        except Exception:
            conv_id = None

        return jsonify({
            'response': response,
            'conv_id': conv_id,
            'ai': True
        })

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': 'Error procesando el mensaje', 'details': str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    conv_id = data.get('conv_id')
    vote = data.get('vote', 'down')

    if conv_id:
        vote_conversation(conv_id, vote)
        if vote == 'down':
            flag_for_review(conv_id)

    return jsonify({'ok': True})


if __name__ == '__main__':
    init_db()
    print("Servidor iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)