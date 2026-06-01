from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = (data.get('message') or '').lower()
    
    if 'sistemas' in message:
        return jsonify({'response': 'INGENIERIA DE SISTEMAS - Desarrollo de software, Cloud, IA. 98% empleabilidad. Salario: $3M - $4.5M'})
    elif 'civil' in message:
        return jsonify({'response': 'INGENIERIA CIVIL - Infraestructuras, construccion. 96% empleabilidad. Salario: $2.5M - $3.5M'})
    elif 'derecho' in message:
        return jsonify({'response': 'DERECHO - 96% aprobacion examen estado. Salario: $3.5M - $6M'})
    elif 'beca' in message:
        return jsonify({'response': 'BECAS: 1)Merito 100% 2)Socioeconomica 80% 3)Deportiva 75% 4)Convenio 30-100% 5)Desempenio 50%'})
    return jsonify({'response': 'Hola soy Vivi. Pregunta sobre Sistemas, Civil, Derecho o Becas'})

@app.route('/')
def index():
    return send_from_directory('.', 'interfaz.html')

@app.route('/<path:filename>')
def files(filename):
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return '', 404

if __name__ == '__main__':
    print('Servidor en http://localhost:9999')
    app.run(host='127.0.0.1', port=9999, debug=False)
