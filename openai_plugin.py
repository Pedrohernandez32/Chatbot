from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from database import save_conversation, get_learned_response, increment_learned_usage

load_dotenv()

# Configurar cliente OpenRouter o OpenAI
openrouter_key = os.environ.get("OPENROUTER_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")

if openrouter_key and openrouter_key.startswith("sk-or-"):
    # Usar OpenRouter
    client = OpenAI(
        api_key=openrouter_key,
        base_url="https://openrouter.ai/api/v1"
    )
    default_model = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
else:
    # Fallback a OpenAI
    client = OpenAI(api_key=openai_key if openai_key else None)
    default_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

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
    """Usar OpenRouter/OpenAI para generar la respuesta si la clave está configurada."""
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    # Ignore placeholder keys or obvious dummy values
    if not api_key or api_key.lower().startswith("tu_") or api_key.lower() in {"tu_api_key", "tu_api_key-aqui", "your_api_key_here"}:
        return None

    # IMPORTANTE: Si es pregunta sobre carreras/programas, dejar que info_plugin responda
    # porque tiene información estructurada y completa
    institutional_keywords = [
        'carrera', 'programa', 'pregrado', 'postgrado', 'maestría', 'especialización',
        'doctorado', 'beca', 'estímulo', 'facultad', 'ingeniería', 'derecho', 'diseño',
        'comunicación', 'psicología', 'administración', 'economía', 'derecho penal',
        'requisito', 'admisión', 'inscripción', 'matricula', 'duración', 'modalidad',
        'perfil profesional', 'campo laboral', 'campus', 'biblioteca', 'horario',
        'contacto', 'teléfono', 'email', 'instalación', 'laboratorio',
        'idioma', 'idiomas', 'centro de idiomas', 'inglés', 'ingles', 'francés', 'frances',
        'italiano', 'portugués', 'portugues', 'español', 'espanol', 'bilingüismo', 'multilingüismo',
        'certificación lingüística', 'toefl', 'ielts', 'cambridge', 'delf', 'ecct', 'lengua', 'lenguas extranjeras',
        'tramite', 'tramites', 'certificado', 'certificados', 'solicitud', 'petición', 'pqrsf',
        'prematricula', 'grado', 'diploma', 'practica', 'practicas', 'pse', 'servicios en linea',
        'plataforma', 'portal', 'carné', 'cancelacion', 'evaluacion', 'titulo', 'egreso'
    ]
    p_lower = prompt.lower()
    if any(kw in p_lower for kw in institutional_keywords):
        # Dejar que info_plugin responda sobre temas institucionales
        return None

    # Check learned responses FIRST - return immediately if found
    learned = get_learned_response(prompt.lower())
    if learned:
        increment_learned_usage(prompt.lower())
        return learned

    model = default_model

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
