from __future__ import annotations

import re
import unicodedata
from typing import Optional

FAQ = {
    "horario": "⏰ Lunes a viernes de 8:00 a.m. a 12:00 m. y de 2:00 p.m. a 6:00 p.m.",
    "ubicación": "📍 Sede principal: Cra. 87 #30-65, Medellín, Belén | Sede Bogotá: Calle 57 # 9-52, Chapinero",
    "carrera": "Ofrecemos 20+ carreras: Ingeniería, Administración, Derecho, Psicología, Diseño, Comunicación y más.",
    "inscripcion": "✍️ Inscripción online en www.udemedellin.edu.co o llama a +57 (604) 590 45 00",
    "contacto": "📞 +57 (604) 590 45 00 / 590 6999 | 📧 info@udemedellin.edu.co",
    "titulo": "Ofrecemos títulos de grado universitario acreditados.",
    "aulas": "Contamos con aulas modernas en campus Medellín y Bogotá.",
    "biblioteca": "📚 Lunes a viernes 7:00 a.m. a 8:00 p.m. | Sábados 8:00 a.m. a 5:00 p.m.",
    "piscina": "🏊 Lunes-viernes 6:00-8:00 a.m. y 6:00-9:00 p.m. | Sábados 8:00 a.m.-12:00 m. Solo con matrícula vigente.",
    "becas": "💰 Becas sociales, de honor, excelencia y estímulos para monitorías, deportes y cultura.",
    "profesores": "Docentes especializados disponibles en horarios de asesoría académica.",
    "materias": "Plan de estudios flexible con materias de especialización según el programa.",
    "admision": "📋 Requerimientos: diploma de bachiller + prueba de admisión. Consulta carreras específicas.",
}

SYNONYMS = {
    "horario": [
        "horario", "cuando abre", "cuando cierra", "a que hora", "que hora",
        "jornada", "horas", "en que horario", "funcionamiento", "atienden"
    ],
    "ubicación": [
        "donde", "ubicacion", "ubicación", "direccion", "dirección", "localizacion",
        "sitio", "direccion exacta", "donde queda", "sede"
    ],
    "carrera": [
        "carrera", "carreras", "programa", "oferta academica", "especialidad",
        "estudio", "grado", "ingenieria", "derecho", "psicologia", "administracion"
    ],
    "inscripcion": [
        "inscripcion", "inscripción", "matricula", "registro", "inscribirme",
        "preinscripcion", "inscribirse", "plazo", "como inscribo", "como me inscribo"
    ],
    "contacto": [
        "contacto", "telefono", "teléfono", "email", "correo", "llamar",
        "telefonos", "whatsapp", "como contacto"
    ],
    "titulo": [
        "titulo", "grado", "certificado", "diploma", "titulo que dan"
    ],
    "aulas": [
        "aula", "salon", "edificio", "clase", "sala", "donde toman clases"
    ],
    "biblioteca": [
        "biblioteca", "libros", "sala de lectura", "prestamo", "horario biblioteca"
    ],
    "piscina": [
        "piscina", "natacion", "nadar", "natatorio", "piscina universidad",
        "cuando abre la piscina"
    ],
    "becas": [
        "becas", "beca", "ayuda economica", "subsidio", "financiacion",
        "descuento", "como saco beca"
    ],
    "profesores": [
        "profesores", "docentes", "catedraticos", "maestros", "jefes de catedra",
        "profesores disponibles"
    ],
    "materias": [
        "materias", "asignaturas", "curso", "cursos", "clases", "que materias dan"
    ],
    "admision": [
        "admision", "admisión", "ingreso", "examen", "prueba", "requisitos",
        "como entro", "como puedo estudiar"
    ],
}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> set[str]:
    return set(normalize_text(text).split())


def best_topic_for_prompt(prompt: str) -> Optional[str]:
    prompt_norm = normalize_text(prompt)
    prompt_tokens = tokenize(prompt_norm)

    # coincidencia directa de frases/sinónimos
    for topic, phrases in SYNONYMS.items():
        for phrase in phrases:
            if normalize_text(phrase) in prompt_norm:
                return topic

    # coincidencia por palabras relacionadas
    best_topic: Optional[str] = None
    best_score = 0.0
    for topic, phrases in SYNONYMS.items():
        keyword_tokens = set()
        for phrase in phrases:
            keyword_tokens.update(tokenize(phrase))

        common = prompt_tokens & keyword_tokens
        if not common:
            continue

        score = len(common) / max(1, len(keyword_tokens))
        if score > best_score:
            best_score = score
            best_topic = topic

    if best_score >= 0.2:
        return best_topic

    return None


def semantic_handler(prompt: str) -> Optional[str]:
    """Responder preguntas de universidad con un matcher flexible."""
    topic = best_topic_for_prompt(prompt)
    if topic is not None:
        return FAQ[topic]

    prompt_norm = normalize_text(prompt)
    if any(word in prompt_norm for word in {"universidad", "pregunta", "informacion", "profesor", "campus"}):
        return "Sobre la universidad puedo decirte horarios, ubicación, inscripciones y carreras. Prueba con una pregunta concreta."

    return None


def register(bot) -> None:
    """Registrar el manejador externo de IA en el chatbot."""
    bot.register_handler(semantic_handler)
