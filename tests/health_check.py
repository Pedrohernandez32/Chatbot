import json
import requests
import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db

results = {}
BASE = 'http://127.0.0.1:5000'

# Server root
try:
    r = requests.get(BASE + '/', timeout=5)
    results['root_status'] = r.status_code
except Exception as e:
    results['root_error'] = str(e)

# Login page
try:
    r = requests.get(BASE + '/login', timeout=5)
    results['login_status'] = r.status_code
except Exception as e:
    results['login_error'] = str(e)

# Chat endpoint
try:
    r = requests.post(BASE + '/api/chat', json={'message': '¿Cuál es el horario de atención?'}, timeout=15)
    results['chat_status'] = r.status_code
    try:
        results['chat_json'] = r.json()
    except Exception as e:
        results['chat_text'] = r.text[:1000]
except Exception as e:
    results['chat_error'] = str(e)

# Database
try:
    conn = db.get_db()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in c.fetchall()]
    results['db_tables'] = tables
    if 'conversations' in tables:
        c.execute('SELECT COUNT(*) as cnt FROM conversations')
        results['conversations_count'] = c.fetchone()['cnt']
    conn.close()
except Exception as e:
    results['db_error'] = str(e)

# Chroma collection count
try:
    import chromadb
    from chromadb.utils import embedding_functions
    client = chromadb.PersistentClient(path='vector_store')
    coll = client.get_or_create_collection(name='university_knowledge', embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2'))
    results['chroma_count'] = coll.count()
except Exception as e:
    results['chroma_error'] = str(e)

# Ollama health
try:
    import ollama_plugin
    results['ollama'] = ollama_plugin.ollama_check()
except Exception as e:
    results['ollama_error'] = str(e)

print(json.dumps(results, ensure_ascii=False, indent=2))
