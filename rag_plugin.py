import os
import glob
from typing import Optional
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

# Configuration
DOCS_DIR = "docs"
DB_DIR = "vector_store"
COLLECTION_NAME = "university_knowledge"

# Use SentenceTransformers for local embeddings to avoid API costs for indexing
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def initialize_rag():
    """Carga los documentos de la carpeta docs/ y los indexa en ChromaDB."""
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )

    if collection.count() > 0:
        return collection

    print("[RAG] Indexando documentos desde la carpeta docs...")
    doc_paths = glob.glob(os.path.join(DOCS_DIR, "*.txt"))

    for path in doc_paths:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

            # Improved Chunking: Overlapping window to preserve context
            chunk_size = 500
            chunk_overlap = 100
            chunks = []

            for i in range(0, len(content), chunk_size - chunk_overlap):
                chunk = content[i:i + chunk_size]
                chunks.append(chunk)

            ids = [f"{os.path.basename(path)}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": os.path.basename(path)} for _ in range(len(chunks))]

            collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )

    print(f"[RAG] Indexación completada. {collection.count()} fragmentos almacenados.")
    return collection

def rag_handler(prompt: str) -> Optional[str]:
    """
    Busca información relevante en la base de datos vectorial y genera una respuesta.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None # Requiere LLM para sintetizar la respuesta

    try:
        collection = initialize_rag()
    except Exception as e:
        print(f"[RAG Error] No se pudo inicializar el almacenamiento vectorial: {e}")
        return None

    # 1. Recuperar los fragmentos más similares (Top 3)
    results = collection.query(
        query_texts=[prompt],
        n_results=3
    )

    # Si no hay resultados significativos, devolvemos None para que otros handlers actúen
    if not results.get("documents") or not results["documents"][0]:
        return None

    context = "\n---\n".join(results["documents"][0])

    # 2. Augmentar el prompt y generar respuesta con OpenAI
    client = OpenAI(api_key=api_key)

    system_prompt = (
        "Eres un asistente de la universidad. Utiliza la siguiente información la "
        "cuya fuente es oficial para responder la pregunta del usuario. "
        "Si la información no está en el contexto, di que no lo sabes y sugiere "
        "contactar a secretaría. Mantén una respuesta concisa y amable.\n\n"
        f"CONTEXTO:\n{context}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def register(bot) -> None:
    """Registra el manejador RAG en el chatbot."""
    bot.register_handler(rag_handler)
