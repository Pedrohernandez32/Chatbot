"""Script opcional para indexar el portal en Chroma (RAG).

Uso: desde el proyecto ejecutar:

    .venv\Scripts\python portal_index.py

Configurar env vars:
- UNIVERSITY_PORTAL_URL o UNIVERSITY_PORTAL_URLS
- VECTOR_STORE_DIR (opcional)

Esto extrae páginas usando `portal_plugin._crawl_portal` y las añade a la colección
`university_knowledge` usada por `rag_plugin`.
"""
from chromadb.utils import embedding_functions
import chromadb
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from portal_plugin import _crawl_portal

DB_DIR = os.environ.get('VECTOR_STORE_DIR', 'vector_store')
COLLECTION_NAME = os.environ.get('RAG_COLLECTION', 'university_knowledge')
EMBED_MODEL = os.environ.get('EMBED_MODEL', 'all-MiniLM-L6-v2')

if __name__ == '__main__':
    start = os.environ.get('UNIVERSITY_PORTAL_URL', 'https://www.udem.edu.co')
    print('Crawling portal:', start)
    pages = _crawl_portal(start, max_pages=int(os.environ.get('PORTAL_CRAWL_MAX_PAGES', '50')))
    print('Pages fetched:', len(pages))

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    client = chromadb.PersistentClient(path=DB_DIR)
    coll = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)

    docs = []
    ids = []
    metadatas = []
    for i, (url, text) in enumerate(pages.items()):
        docs.append(text)
        ids.append(f"portal_{i}")
        metadatas.append({'source': url})

    if docs:
        print('Adding documents to Chroma...')
        coll.add(documents=docs, ids=ids, metadatas=metadatas)
        print('Indexing complete. Count:', coll.count())
    else:
        print('No documents to index.')
