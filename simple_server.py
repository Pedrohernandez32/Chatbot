from flask import Flask, send_from_directory, request, jsonify
import os
import json

app = Flask(__name__, static_folder='static')

# Respuestas de Vivi basadas en palabras clave
VIVI_RESPONSES = {
    'inscr': "Para inscribirte a un pregrado, debes: 1) Tener diploma de bachiller, 2) Presentar las pruebas de admisión, 3) Diligenciar el formulario en www.udemedellin.edu.co, 4) Esperar resultado. ¿Necesitas más información?",
    'beca': "Ofrecemos varios tipos de becas: Mérito académico (hasta 100%), Socioeconómica, Deportiva y de Convenios. El monto depende de tu situación. Contáctanos en +57 604 5904500",
    'programa': "Tenemos 27 pregrados en 7 facultades: Derecho, Ingenierías, Administración, Comunicación, Diseño, Ciencias y Humanidades. ¿Cuál te interesa?",
    'campus': "Nuestro campus principal está en Carrera 87 N° 30-65, Medellín. Tenemos Teatro, Biblioteca, Laboratorios, Coliseo y zonas verdes. ¿Quieres ver fotos?",
    'idioma': "Contamos con Centro de Idiomas que ofrece inglés, francés, alemán y más. Consulta horarios y costos en la página.",
    'contact': "Teléfono: +57 (604) 590 4500 | Email: info@udemedellin.edu.co | Horario: Lunes-Viernes 8am-12pm y 2pm-6pm",
}

def get_vivi_response(message):
    message_lower = message.lower()

    # Búsqueda de palabras clave
    for key, response in VIVI_RESPONSES.items():
        if key in message_lower:
            return response

    # Respuesta por defecto
    return "Entiendo tu pregunta. Para más información específica sobre admisiones, programas, becas o campus, puedo ayudarte con detalles. ¿Hay algo en particular que quieras saber?"

@app.route('/')
def index():
    return send_from_directory('.', 'interfaz.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API para responder con Vivi"""
    try:
        data = request.get_json()
        message = data.get('message', '')

        if not message:
            return jsonify({'response': json.dumps({'text': 'Por favor, escribe una pregunta.'})})

        response_text = get_vivi_response(message)

        return jsonify({'response': json.dumps({'text': response_text})})
    except Exception as e:
        return jsonify({'response': json.dumps({'text': f'Error: {str(e)}'})})

@app.route('/<path:path>', methods=['GET'])
def serve(path):
    # Primero intenta en la raíz (para JSX, CSS, etc)
    if os.path.exists(path):
        return send_from_directory('.', path)
    # Luego intenta en static
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("Servidor simple corriendo en http://localhost:8888")
    app.run(debug=False, host='127.0.0.1', port=8888, use_reloader=False)
