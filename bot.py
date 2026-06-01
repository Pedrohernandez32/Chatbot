from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    msg = (request.json or {}).get('message', '').lower()
    responses = {
        'sistemas': '**INGENIERIA DE SISTEMAS** - Software, Cloud, IA. 98% empleabilidad. Salario: $3M-$4.5M',
        'civil': '**INGENIERIA CIVIL** - Infraestructuras. 96% empleabilidad. Salario: $2.5M-$3.5M',
        'derecho': '**DERECHO** - 96% aprobación estado. Salario: $3.5M-$6M',
        'beca': '**BECAS**: 1)Merito 100% 2)Socio 80% 3)Deporte 75%'
    }
    for k, v in responses.items():
        if k in msg:
            return jsonify({'response': v})
    return jsonify({'response': 'Hola soy Vivi. Pregunta sobre: sistemas, civil, derecho, becas'})

@app.route('/')
def home():
    return send_from_directory('.', 'interfaz.html')

@app.route('/<path:f>')
def files(f):
    try:
        return send_from_directory('.', f)
    except:
        return '', 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999, debug=False)
