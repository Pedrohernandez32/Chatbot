from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import requests
from dotenv import load_dotenv

from database import save_conversation, get_learned_response, increment_learned_usage

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = (
    "Eres un asistente personal experto en preguntas sobre una facultad. "
    "Responde de forma clara, cortés y breve, con información útil. "
    "Si no conoces la respuesta, dilo honestamente.\n\n"
    "INFORMACIÓN DE INSTALACIONES:\n"
    "BIBLIOTECA: Lunes a viernes de 8 a 20 hs. Sábados de 9 a 14 hs.\n"
    "PISCINA: Lunes a viernes: 6:00-8:00 y 18:00-21:00. Sábados: 8:00-12:00.\n"
    "Domingos y festivos: Cerrado.\n"
    "Solo pueden usar la piscina alumnos con matrícula vigente."
)

conversation_history: list[dict[str, str]] = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

MAX_HISTORY_SIZE = 10
DEFAULT_MODEL = "llama3.2"


def _trim_history() -> None:
    global conversation_history
    if len(conversation_history) <= MAX_HISTORY_SIZE + 1:
        return
    conversation_history = [conversation_history[0]] + conversation_history[-MAX_HISTORY_SIZE:]


def ollama_check() -> bool:
    """Verificar si Ollama está corriendo."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def ollama_handler(prompt: str) -> Optional[str | Generator]:
    """Usar Ollama para generar la respuesta. Soporta streaming si se configura en la petición."""
    # Check learned responses FIRST
    learned = get_learned_response(prompt.lower())
    if learned:
        increment_learned_usage(prompt.lower())
        return learned

    if not ollama_check():
        return None

    model = os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    user_message = {"role": "user", "content": prompt}

    try:
        # We use a generator for streaming
        def generate():
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": SYSTEM_PROMPT,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 250,
                    }
                },
                timeout=60,
                stream=True
            )
            for line in response.iter_lines():
                if line:
                    import json
                    chunk = json.loads(line.decode('utf-8'))
                    yield chunk.get("response", "")

        return generate()
    except Exception as e:
        print(f"Ollama stream error: {e}")
        return None


def _detect_topic(prompt: str) -> Optional[str]:
    prompt_lower = prompt.lower()
    topics = {
        "biblioteca": ["biblioteca", "libros", "sala de lectura", "prestamo"],
        "piscina": ["piscina", "natacion", "nadar", "natatorio"],
        "horario": ["horario", "cuando abre", "cuando cierra", "jornada"],
        "ubicacion": ["ubicacion", "direccion", "donde esta"],
        "carrera": ["carrera", "programa", "ingenieria", "administracion"],
        "inscripcion": ["inscripcion", "matricula", "registro"],
        "contacto": ["contacto", "telefono", "email", "correo"],
    }
    for topic, keywords in topics.items():
        if any(kw in prompt_lower for kw in keywords):
            return topic
    return None


def register(bot) -> None:
    """Registrar el handler de Ollama en el chatbot."""
    bot.register_handler(ollama_handler)
