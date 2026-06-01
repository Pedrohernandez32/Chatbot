from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    if request.method == 'OPTIONS':
        return '', 200
    msg = (request.json or {}).get('message', '').lower()
    if 'sistemas' in msg:
        return jsonify({'response': '**INGENIERIA DE SISTEMAS** - Software, Cloud Computing. 98% empleabilidad. Salario inicial: $3M a $4.5M'})
    elif 'civil' in msg:
        return jsonify({'response': '**INGENIERIA CIVIL** - Infraestructuras, construcción. 96% empleabilidad. Salario: $2.5M a $3.5M'})
    elif 'derecho' in msg:
        return jsonify({'response': '**DERECHO** - 96% aprobacion examen estado. Salario: $3.5M a $6M'})
    elif 'beca' in msg:
        return jsonify({'response': '**BECAS**: 1)Merito 100% 2)Socioeconomica 80% 3)Deportiva 75% 4)Convenio 30-100% 5)Desempenio 50%. Info: becas@udemedellin.edu.co'})
    return jsonify({'response': 'Hola soy Vivi. Pregunta sobre: sistemas, civil, derecho o becas'})

@app.route('/')
def home():
    return send_from_directory('.', 'interfaz.html')

@app.route('/<path:p>')
def static_files(p):
    return send_from_directory('.', p) if os.path.exists(p) else ('', 404)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999, debug=False, threaded=True)
