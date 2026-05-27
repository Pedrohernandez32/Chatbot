from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from database import save_conversation, get_learned_response, increment_learned_usage

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = (
    "Eres un asistente personal experto en preguntas sobre una universidad. "
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


def _trim_history() -> None:
    global conversation_history
    if len(conversation_history) <= MAX_HISTORY_SIZE + 1:
        return
    conversation_history = [conversation_history[0]] + conversation_history[-MAX_HISTORY_SIZE:]


def openai_handler(prompt: str) -> Optional[str]:
    """Usar OpenAI para generar la respuesta si la clave está configurada."""
    api_key = os.environ.get("OPENAI_API_KEY")
    # Ignore placeholder keys or obvious dummy values
    if not api_key or api_key.lower().startswith("tu_") or api_key.lower() in {"tu_api_key", "tu_api_key-aqui", "your_api_key_here"}:
        return None

    # Check learned responses FIRST - return immediately if found
    learned = get_learned_response(prompt.lower())
    if learned:
        increment_learned_usage(prompt.lower())
        return learned

    client.api_key = api_key
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    user_message = {"role": "user", "content": prompt}
    messages = conversation_history + [user_message]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=250,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        conversation_history.append(user_message)
        conversation_history.append({"role": "assistant", "content": answer})
        _trim_history()

        # Guardar conversación en la base de datos
        topic = _detect_topic(prompt)
        save_conversation(prompt, answer, topic)
        return answer
    except Exception as e:
        print(f"OpenAI error: {e}")
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
    """Registrar el handler de OpenAI en el chatbot."""
    bot.register_handler(openai_handler)
