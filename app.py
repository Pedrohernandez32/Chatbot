from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración
SYSTEM_PROMPT = """
Eres un asistente virtual amigable y profesional de la Universidad de Medellín.

Información importante que debes conocer:

CONTACTOS:
- Teléfono: +57 (604) 590 45 00 – +57 (604) 590 6999
- Sede principal: Carrera 87 N° 30 – 65, Medellín – Colombia
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

La institución es de educación superior sujeta a la inspección y vigilancia del Ministerio de Educación Nacional.

Responde de forma clara, cortés y útil usando esta información. Si no conoces algo, indícalo honestamente.
"""

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
MAX_HISTORY = 15

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

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
        'ubicacion': 'Sede principal: Carrera 87 N° 30 – 65, Medellín – Colombia. Sede Bogotá: Calle 57 # 9-52, Chapinero.',
        'donde': 'Sede principal: Carrera 87 N° 30 – 65, Medellín – Colombia. Sede Bogotá: Calle 57 # 9-52, Chapinero.',
        'direccion': 'Sede principal: Carrera 87 N° 30 – 65, Medellín – Colombia. Sede Bogotá: Calle 57 # 9-52, Chapinero.',
        'medellin': 'La sede principal está en Carrera 87 N° 30 – 65, Medellín – Colombia.',
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
        'admision': 'La institución es de educación superior sujeta a la inspección y vigilancia del Ministerio de Educación Nacional. Para más información contacta a la universidad directamente.',
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
