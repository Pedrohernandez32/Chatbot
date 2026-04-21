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
Eres un asistente virtual amigable y profesional de la Universidad de Medellín ubicada en Cra. 87 #30-65, Medellín, Belén, Antioquia.

Información importante que debes conocer:
- Horarios: Lunes a sabado de 6 a.m a 10 p.m
- Carreras: Ingeniería, Administración y Psicología
- Inscripciones: Comienzan en marzo para el próximo cuatrimestre
- Contacto: info@facultad.edu o (011) 1234-5678
- Biblioteca: Lunes a viernes 8-20 hs, sábados 9-14 hs
- Becas: Se gestionan en Secretaría Estudiantil
- Admisión: Examen de ingreso, consultar fechas en sitio oficial
- Piscina: Lunes a viernes 6:00-8:00 y 18:00-21:00. Sábados 8:00-12:00

Responde de forma clara, cortés y útil. Si no conoces algo, indícalo honestamente.
"""

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
MAX_HISTORY = 15

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chatbot.js')
def chatbot_js():
    return send_from_directory('.', 'chatbot.js')

@app.route('/styles.css')
def styles_css():
    return send_from_directory('.', 'styles.css')

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
        'horario': 'La universidad atiende de lunes a viernes de 9 a 18 hs.',
        'hora': 'La universidad atiende de lunes a viernes de 9 a 18 hs.',
        'ubicacion': 'La universidad se encuentra en Cra. 87 #30-65, Medellín, Belén, Antioquia.',
        'donde': 'La universidad se encuentra en Cra. 87 #30-65, Medellín, Belén, Antioquia.',
        'direccion': 'La universidad se encuentra en Cra. 87 #30-65, Medellín, Belén, Antioquia.',
        'carrera': 'Ofrecemos Ingeniería, Administración y Psicología.',
        'ingenieria': 'Sí, ofrecemos Ingeniería como una de nuestras carreras.',
        'administracion': 'Sí, ofrecemos Administración como una de nuestras carreras.',
        'psicologia': 'Sí, ofrecemos Psicología como una de nuestras carreras.',
        'inscripcion': 'La inscripción para el próximo cuatrimestre comienza en marzo.',
        'matricula': 'La inscripción para el próximo cuatrimestre comienza en marzo.',
        'contacto': 'Puedes escribir a info@udem.edu.co o llamar al (011) 1234-5678.',
        'telefono': 'Puedes llamarnos al (011) 1234-5678.',
        'email': 'Puedes escribirnos a info@udem.edu.co',
        'biblioteca': 'La biblioteca abre de lunes a viernes de 8 a 20 hs y sábados de 9 a 14 hs.',
        'libros': 'La biblioteca abre de lunes a viernes de 8 a 20 hs y sábados de 9 a 14 hs.',
        'beca': 'Las becas y ayudas económicas se gestionan en Secretaría Estudiantil.',
        'becas': 'Las becas y ayudas económicas se gestionan en Secretaría Estudiantil.',
        'admision': 'La admisión se realiza con un examen de ingreso. Consulta fechas en el sitio oficial.',
        'examen': 'El examen de admisión es requisito para ingresar. Consulta fechas en el sitio oficial.',
    }

    for keyword, answer in faq.items():
        if keyword in prompt_lower:
            return answer

    if any(word in prompt_lower for word in ['hola', 'buenas', 'saludos']):
        return '¡Hola! Soy el asistente virtual de la universidad. ¿En qué puedo ayudarte?'

    if any(word in prompt_lower for word in ['gracias', 'muchas gracias']):
        return '¡De nada! Si tienes más preguntas, estaré aquí para ayudarte.'

    return 'Lo siento, no tengo información sobre eso. Te recomiendo contactar directamente a la universidad al (011) 1234-5678 o escribir a info@udem.edu.co'

if __name__ == '__main__':
    app.run(debug=True, port=5000)