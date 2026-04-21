from __future__ import annotations

import argparse
import os
from typing import Callable, List, Optional

from ai_plugin import register as register_ai_plugin
from openai_plugin import register as register_openai_plugin

Handler = Callable[[str], Optional[str]]


class Chatbot:
    """Estructura básica para un chatbot extensible."""

    def __init__(self, name: str = "Chatbot") -> None:
        self.name = name
        self.handlers: List[Handler] = []

    def register_handler(self, handler: Handler) -> None:
        """Registrar una función que responda a una entrada de usuario."""
        self.handlers.append(handler)

    def respond(self, prompt: str) -> str:
        """Generar respuesta usando el primer manejador que devuelva texto."""
        prompt = prompt.strip()
        if not prompt:
            return "Por favor escribe algo para continuar."

        for handler in self.handlers:
            result = handler(prompt)
            if result is not None:
                return result

        return f"No tengo una respuesta preparada para: {prompt}"


def faculty_handler(prompt: str) -> Optional[str]:
    """Responder preguntas básicas sobre una universidad."""
    prompt_lower = prompt.lower()

    faq = {
        "horario": "La universidad atiende de lunes a viernes de 9 a 18 hs.",
        "ubicación": "La universidad se encuentra en  Cra. 87 #30-65, Medellín, Belén, Medellín, Antioquia ",
        "carrera": "Ofrecemos Ingeniería, Administración y Psicología.",
        "inscripcion": "La inscripción para el próximo cuatrimestre comienza en marzo.",
        "contacto": "Puedes escribir a info@udem.edu.co o llamar al (011) 1234-5678.",
        "titulo": "El título que entregamos es de grado universitario.",
        "aulas": "Las clases se dictan en el edificio principal y en el anexo de Ciencias Sociales.",
    }

    for keyword, answer in faq.items():
        if keyword in prompt_lower:
            return answer

    if any(word in prompt_lower for word in {"universidad", "pregunta", "información", "profesor", "campus"}):
        return "Sobre la universidad puedo decirte horarios, ubicación, inscripciones y carreras. Prueba con una pregunta concreta."

    return None


def default_handler(prompt: str) -> Optional[str]:
    """Manejador de ejemplo para comenzar a probar el chatbot."""
    return f"Entiendo: {prompt}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot de universidad con modo de prueba.")
    parser.add_argument(
        "--one-shot",
        action="store_true",
        help="Ejecutar solo una pregunta y salir.",
    )
    args = parser.parse_args()

    bot = Chatbot("MiChatbot")
    register_openai_plugin(bot)
    register_ai_plugin(bot)
    bot.register_handler(faculty_handler)
    bot.register_handler(default_handler)

    if not os.environ.get("OPENAI_API_KEY"):
        print("=== Advertencia: no se encontró OPENAI_API_KEY; se usará IA local o reglas si está disponible. ===")

    print("=== Chatbot inicializado ===")
    if args.one_shot:
        print("Modo de prueba: una sola pregunta.")
        prompt = input("Tú: ").strip()
        if prompt:
            print("Chatbot:", bot.respond(prompt))
        return

    print("Escribe 'salir' para terminar.")
    while True:
        prompt = input("Tú: ").strip()
        if prompt.lower() in {"salir", "exit", "quit"}:
            print("Chatbot: Hasta luego.")
            break
        print("Chatbot:", bot.respond(prompt))


if __name__ == "__main__":
    main()
