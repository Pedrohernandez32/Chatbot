import json
from server import app


def test_chat_endpoint():
    client = app.test_client()
    resp = client.post('/api/chat', json={'message': '¿Cuál es el horario de la biblioteca?'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'response' in data
    assert isinstance(data['response'], str)

