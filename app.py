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
import whatsapp_handler

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
# 1. Cloud LLM (OpenRouter - IA primero)
openai_plugin.register(bot)
# 2. Institutional info (respuestas predefinidas si IA no sabe)
info_plugin.register(bot)
# 3. Semantic FAQ
ai_plugin.register(bot)
# 4. Local LLM (Ollama)
ollama_plugin.register(bot)
# 5. Utilities
tool_plugin.register(bot)

# DESACTIVADOS:
# - portal_plugin: Information cruda del sitio
# - rag_plugin: Knowledge base con respuestas desestructuradas

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

INSTRUCCIONES IMPORTANTES PARA RESPONDER SOBRE CARRERAS:
- Cuando el usuario pregunte por carreras, SIEMPRE:
  1. Presenta la lista COMPLETA de facultades y sus carreras
  2. Si pregunta por una carrera ESPECÍFICA, da TODOS estos detalles:
     - Nombre completo
     - Facultad a la que pertenece
     - Duración (semestres)
     - Modalidad (Presencial)
     - Descripción detallada de qué forma
     - Perfil profesional (habilidades y competencias)
     - Campo laboral (donde pueden trabajar)
     - Requisitos de admisión
     - Decano responsable
     - Información de contacto de la facultad
  3. Si pregunta por UNA FACULTAD, lista todas sus carreras con un resumen de cada una
  4. Responde SIEMPRE en español
  5. Sé profesional pero amigable

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
    return send_from_directory('.', 'Asistente Virtual UdeMedellin.html')

@app.route('/asistente')
def asistente():
    """Sirve el nuevo diseño React del asistente"""
    return send_from_directory('.', 'Asistente Virtual UdeMedellin.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Sirve archivos de la carpeta assets"""
    return send_from_directory('assets', filename)

@app.route('/<path:filename>')
def serve_root_files(filename):
    """Sirve archivos JSX y CSS desde la raíz"""
    if filename.endswith(('.jsx', '.js', '.css', '.html')):
        return send_from_directory('.', filename)
    return send_from_directory('static', filename)

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


@app.route('/api/response/expanded/<category>', methods=['GET'])
def get_expanded_response(category):
    expanded = db.get_expanded_response(category)
    if expanded:
        return jsonify({'expanded': expanded})
    return jsonify({'error': 'No hay información expandida disponible'}), 404


@app.route('/api/response/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json() or {}
        conversation_id = data.get('conversation_id')
        response_text = data.get('response_text', '').strip()
        helpful = data.get('helpful')
        feedback_text = (data.get('feedback', '') or '').strip()[:500]
        user_id = current_user.id if current_user.is_authenticated else None

        if not response_text or helpful is None:
            return jsonify({'error': 'Datos incompletos'}), 400

        feedback_id = db.save_response_feedback(
            conversation_id, response_text, helpful, feedback_text, user_id
        )
        logger.info(f"Feedback #{feedback_id}: helpful={helpful}, category={response_text[:50]}")
        return jsonify({'success': True, 'id': feedback_id})

    except Exception as e:
        logger.error(f"Feedback error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error guardando feedback'}), 500


@app.route('/api/admin/feedback-stats', methods=['GET'])
@login_required
def feedback_stats():
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    stats = db.get_feedback_stats(limit=20)
    return jsonify(stats)


@app.route('/api/push/subscribe', methods=['POST'])
def subscribe_push():
    try:
        data = request.get_json() or {}
        endpoint = data.get('endpoint', '').strip()
        auth = data.get('keys', {}).get('auth', '').strip()
        p256dh = data.get('keys', {}).get('p256dh', '').strip()
        user_agent = request.headers.get('User-Agent', '')[:200]

        if not endpoint or not auth or not p256dh:
            return jsonify({'error': 'Datos incompletos'}), 400

        user_id = current_user.id if current_user.is_authenticated else None
        sub_id = db.save_push_subscription(user_id, endpoint, auth, p256dh, user_agent)
        logger.info(f"Push subscription #{sub_id} registered")
        return jsonify({'success': True, 'id': sub_id})

    except Exception as e:
        logger.error(f"Push subscribe error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error registrando notificación'}), 500


@app.route('/api/push/unsubscribe', methods=['POST'])
def unsubscribe_push():
    try:
        data = request.get_json() or {}
        endpoint = data.get('endpoint', '').strip()

        if not endpoint:
            return jsonify({'error': 'Endpoint requerido'}), 400

        db.delete_push_subscription(endpoint)
        logger.info(f"Push unsubscribed: {endpoint[:50]}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Push unsubscribe error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error desuscribiendo'}), 500


@app.route('/api/admin/push/notify', methods=['POST'])
@login_required
def send_push_notification():
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403

    try:
        data = request.get_json() or {}
        title = data.get('title', 'Notificación').strip()[:100]
        message = data.get('message', '').strip()[:200]
        icon = data.get('icon', '/static/logo.png')

        if not message:
            return jsonify({'error': 'Mensaje requerido'}), 400

        subscriptions = db.get_all_push_subscriptions()
        sent = 0
        failed = 0

        for sub in subscriptions:
            try:
                # Aquí iría la lógica real de envío con web-push library
                # Por ahora solo registramos que se envió
                logger.info(f"Push sent to {sub['endpoint'][:50]}: {title}")
                sent += 1
            except Exception as e:
                logger.warning(f"Failed to push: {str(e)}")
                failed += 1

        return jsonify({
            'success': True,
            'sent': sent,
            'failed': failed,
            'total': len(subscriptions)
        })

    except Exception as e:
        logger.error(f"Push notify error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error enviando notificaciones'}), 500


# ── WhatsApp Integration ──
@app.route('/api/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """WhatsApp webhook endpoint"""
    if request.method == 'GET':
        # Verificación de webhook
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'udem-chatbot-verify')

        result = whatsapp_handler.verify_whatsapp_webhook(token, challenge, verify_token)
        if result:
            return result, 200
        return 'Invalid token', 403

    elif request.method == 'POST':
        # Recibir mensaje de WhatsApp
        try:
            data = request.get_json() or {}
            msg_data = whatsapp_handler.parse_whatsapp_webhook(data)

            if msg_data:
                phone = msg_data['from']
                text = msg_data['text']

                # Guardar en BD
                db.save_whatsapp_conversation(phone, text, is_incoming=True)

                # Procesar mensaje con el bot
                response = bot.handle(text)
                response_text, is_ai = response

                # Enviar respuesta por WhatsApp
                try:
                    parsed = json.loads(response_text) if isinstance(response_text, str) else {'text': response_text}
                    reply = parsed.get('text', response_text)
                except:
                    reply = response_text

                whatsapp_handler.send_whatsapp_message(phone, reply[:1024])
                db.save_whatsapp_conversation(phone, reply[:1024], is_incoming=False)

                logger.info(f"WhatsApp message processed: {phone}")

            return jsonify({'success': True}), 200

        except Exception as e:
            logger.error(f"WhatsApp webhook error: {str(e)}", exc_info=True)
            return jsonify({'error': str(e)}), 400


@app.route('/api/whatsapp/chat', methods=['POST'])
def whatsapp_chat():
    """Enviar mensaje vía WhatsApp desde el usuario"""
    try:
        data = request.get_json() or {}
        phone_number = data.get('phone', '').strip()
        message = data.get('message', '').strip()

        if not phone_number or not message:
            return jsonify({'error': 'Teléfono y mensaje requeridos'}), 400

        if len(message) > 1000:
            return jsonify({'error': 'Mensaje muy largo'}), 400

        # Guardar en BD
        db.save_whatsapp_conversation(phone_number, message, is_incoming=True, conversation_type='ai')

        # Procesar con bot
        response = bot.handle(message)
        response_text, is_ai = response

        try:
            parsed = json.loads(response_text) if isinstance(response_text, str) else {'text': response_text}
            reply = parsed.get('text', response_text)
        except:
            reply = response_text

        # Enviar por WhatsApp
        success = whatsapp_handler.send_whatsapp_message(phone_number, reply[:1024])

        if success:
            db.save_whatsapp_conversation(phone_number, reply[:1024], is_incoming=False, conversation_type='ai')

        return jsonify({
            'success': success,
            'response': reply[:100],
            'message': 'Mensaje enviado por WhatsApp' if success else 'Error enviando mensaje'
        })

    except Exception as e:
        logger.error(f"WhatsApp chat error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error procesando mensaje'}), 500


@app.route('/api/whatsapp/advisor', methods=['POST'])
def whatsapp_advisor():
    """Solicitar asesor vía WhatsApp"""
    try:
        data = request.get_json() or {}
        phone_number = data.get('phone', '').strip()
        name = data.get('name', 'Usuario').strip()

        if not phone_number:
            return jsonify({'error': 'Teléfono requerido'}), 400

        # Crear solicitud de asesor
        request_id = db.create_advisor_request(name, '', phone_number, 'Solicitud desde WhatsApp')
        db.update_advisor_request_status(request_id, 'live_requested')

        # Notificar al asesor
        whatsapp_handler.notify_advisor_whatsapp(phone_number, name, request_id)

        # Enviar confirmación al usuario
        msg = f"Hola {name}, 👋\n\nTu solicitud ha sido recibida.\nUn asesor se pondrá en contacto pronto.\n\nID: {request_id}"
        whatsapp_handler.send_whatsapp_message(phone_number, msg)

        return jsonify({
            'success': True,
            'request_id': request_id,
            'message': 'Solicitud enviada. El asesor se contactará pronto.'
        })

    except Exception as e:
        logger.error(f"WhatsApp advisor error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error procesando solicitud'}), 500


if __name__ == '__main__':
    try:
        db.init_db()
    except Exception as e:
        print('DB init error:', e)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, port=int(os.environ.get('PORT', 5000)))
