from __future__ import annotations

import re
import unicodedata
from typing import Optional

FAQ = {
    "horario": "La universidad atiende de lunes a viernes de 9 a 18 hs.",
    "ubicación": "La universidad se encuentra en Cra. 87 #30-65, Medellín, Belén, Medellín, Antioquia.",
    "carrera": "Ofrecemos Ingeniería, Administración y Psicología.",
    "inscripcion": "La inscripción para el próximo cuatrimestre comienza en marzo.",
    "contacto": "Puedes escribir a info@udem.edu.co o llamar al (011) 1234-5678.",
    "titulo": "El título que entregamos es de grado universitario.",
    "aulas": "Las clases se dictan en el edificio principal y en el anexo de Ciencias Sociales.",
    "biblioteca": "La biblioteca abre de lunes a viernes de 8 a 20 hs y sábados de 9 a 14 hs.",
    "piscina": "La piscina está disponible de lunes a viernes de 6:00 a 8:00 y de 18:00 a 21:00. Los sábados de 8:00 a 12:00. Domingos y festivos permanece cerrada. Solo alumnos con matrícula vigente pueden usar la piscina.",
    "becas": "Las becas y ayudas económicas se gestionan en Secretaría Estudiantil.",
    "profesores": "Los datos de los profesores se publican en la plataforma académica y el sitio web de la universidad.",
    "materias": "Las materias disponibles están en el plan de estudios y en la oferta académica del cuatrimestre.",
    "admision": "La admisión se realiza con un examen de ingreso; consulta fechas y requisitos en el sitio oficial.",
}

SYNONYMS = {
    "horario": [
        "horario",
        "cuando abre",
        "cuando cierra",
        "a que hora",
        "que hora",
        "jornada",
        "horas",
    ],
    "ubicación": [
        "donde",
        "ubicacion",
        "direccion",
        "localizacion",
        "sitio",
        "direccion exacta",
    ],
    "carrera": [
        "carrera",
        "programa",
        "oferta academica",
        "especialidad",
        "estudio",
        "grado",
    ],
    "inscripcion": [
        "inscripcion",
        "matricula",
        "registro",
        "inscribirme",
        "preinscripcion",
        "inscribirse",
        "plazo",
    ],
    "contacto": [
        "contacto",
        "telefono",
        "email",
        "correo",
        "llamar",
        "telefonos",
    ],
    "titulo": [
        "titulo",
        "grado",
        "certificado",
        "diploma",
    ],
    "aulas": [
        "aula",
        "salon",
        "edificio",
        "clase",
        "sala",
    ],
    "biblioteca": [
        "biblioteca",
        "libros",
        "sala de lectura",
        "prestamo",
    ],
    "piscina": [
        "piscina",
        "natacion",
        "nadar",
        "natatorio",
        "piscina universidad",
    ],
    "becas": [
        "becas",
        "ayuda economica",
        "subsidio",
        "financiacion",
    ],
    "profesores": [
        "profesores",
        "docentes",
        "catedraticos",
        "maestros",
        "jefes de catedra",
    ],
    "materias": [
        "materias",
        "asignaturas",
        "curso",
        "cursos",
        "clases",
    ],
    "admision": [
        "admision",
        "ingreso",
        "examen",
        "prueba",
        "requisitos",
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
