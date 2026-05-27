import requests
import sys

try:
    r = requests.post('http://127.0.0.1:5000/api/chat', json={'message':'¿Cuál es el horario de la biblioteca?'}, timeout=10)
    print('STATUS', r.status_code)
    print(r.text)
    if r.status_code != 200:
        print('Test failed')
        sys.exit(2)
    print('Test passed')
except Exception as e:
    print('Exception during test:', e)
    sys.exit(1)
