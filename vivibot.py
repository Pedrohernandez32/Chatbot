from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    msg = (request.json or {}).get('message', '').lower()
    if 'sistemas' in msg:
        return jsonify({'response': '**INGENIERIA DE SISTEMAS** - Desarrollo software, Cloud, IA. 98% empleabilidad. Salario: $3M-$4.5M'})
    elif 'civil' in msg:
        return jsonify({'response': '**INGENIERIA CIVIL** - Infraestructuras, construcción. 96% empleabilidad. Salario: $2.5M-$3.5M'})
    elif 'derecho' in msg:
        return jsonify({'response': '**DERECHO** - 96% aprobación examen estado. Salario: $3.5M-$6M'})
    elif 'beca' in msg:
        return jsonify({'response': '**BECAS**: 1)Merito 100% 2)Socio 80% 3)Deporte 75% 4)Convenio 30-100% 5)Desempenio 50%'})
    return jsonify({'response': 'Hola soy Vivi. Pregunta: sistemas, civil, derecho o becas'})

@app.route('/')
def home():
    return send_from_directory('.', 'interfaz.html')

@app.route('/<path:f>')
def files(f):
    return send_from_directory('.', f) if os.path.exists(f) else ('',404)

if __name__=='__main__':
    print('SERVIDOR EN http://localhost:8080')
    app.run(host='127.0.0.1',port=8080,debug=False,threaded=True)
