"""
Sistema de Sugerencias Inteligentes para Asesores
Usa IA para sugerir respuestas contextuales basadas en preguntas comunes
"""

from typing import List, Dict, Optional
import json

class AdvisorAISuggestions:
    """Genera sugerencias inteligentes para asesores basadas en la conversación"""

    # Base de conocimiento de preguntas frecuentes y respuestas
    KNOWLEDGE_BASE = {
        "becas": {
            "keywords": ["beca", "ayuda económica", "financiamiento", "subsidio"],
            "responses": [
                "Tenemos varios tipos de becas disponibles: Excelencia, Meritoria, Socioeconómica y Permanencia. ¿Cuál tipo de beca te interesa?",
                "¿Ya aplicaste a alguna beca? Puedo ayudarte con el proceso de solicitud.",
                "Las becas varían según tu desempeño académico y situación económica. ¿Cuál es tu contexto?",
                "Nuestras becas tienen un proceso de evaluación específico. ¿Necesitas información sobre requisitos?"
            ]
        },
        "admisiones": {
            "keywords": ["admisión", "inscripción", "ingreso", "aplicar", "proceso selectivo"],
            "responses": [
                "El proceso de admisión depende del programa que desees. ¿Cuál carrera te interesa?",
                "Tenemos diferentes opciones de ingreso: prueba de admisión, análisis de antecedentes, o equivalencias.",
                "¿Eres estudiante de colegio o ya tienes educación superior? Esto determina el proceso.",
                "Los documentos requeridos varían. ¿De cuál programa quieres información específica?"
            ]
        },
        "campus": {
            "keywords": ["campus", "ubicación", "sedes", "dónde", "localización"],
            "responses": [
                "Tenemos varios campus: Sabaneta (Principal), Medellín, Envigado y Bello. ¿Cuál te interesa visitar?",
                "¿Deseas conocer la infraestructura de algún campus específico?",
                "Podemos agendar una visita guiada a nuestras instalaciones. ¿Cuándo te vendría bien?",
                "Cada campus tiene servicios especializados. ¿Qué servicios buscas?"
            ]
        },
        "horarios": {
            "keywords": ["horario", "clase", "sesión", "calendario académico"],
            "responses": [
                "Los horarios dependen del programa que curse. ¿Cuál es tu carrera?",
                "Ofrecemos jornadas diurna y nocturna. ¿Cuál prefieres?",
                "El calendario académico se organiza en semestres. ¿Necesitas fechas específicas?",
                "¿Buscas horarios para un semestre específico o información general?"
            ]
        },
        "contacto": {
            "keywords": ["contacto", "teléfono", "email", "llamar", "contactar", "cómo comunicarse"],
            "responses": [
                "Puedes contactarnos al +57 4 3309500 en horario de oficina de 8am a 5pm.",
                "Nuestro email principal es info@udemedellín.edu.co para consultas generales.",
                "Hay líneas directas para cada facultad. ¿A cuál facultad necesitas contactar?",
                "También puedes visitarnos personalmente en cualquiera de nuestros campus."
            ]
        },
        "profesores": {
            "keywords": ["profesor", "docente", "instructor", "maestro"],
            "responses": [
                "¿Necesitas información sobre un docente específico de algún programa?",
                "Nuestros docentes tienen perfiles con especialidades y horarios de atención.",
                "¿Buscas un profesor para una clase o facultad particular?",
                "Puedo ayudarte a encontrar docentes especializados en cierto área."
            ]
        },
        "decanos": {
            "keywords": ["decano", "director", "facultad", "responsable"],
            "responses": [
                "Cada facultad tiene un decano responsable. ¿De cuál facultad?",
                "Los decanos supervisan los programas académicos de sus facultades.",
                "¿Necesitas contactar directamente con un decano?",
                "Los decanos tienen disponibilidad para asesorías académicas. ¿Tu consulta es académica?"
            ]
        }
    }

    @staticmethod
    def extract_intent(message: str) -> Optional[str]:
        """Detecta la intención del mensaje del usuario"""
        message_lower = message.lower()

        for intent, data in AdvisorAISuggestions.KNOWLEDGE_BASE.items():
            for keyword in data['keywords']:
                if keyword in message_lower:
                    return intent

        return None

    @staticmethod
    def get_suggestions(message: str, conversation_history: List[Dict] = None) -> List[str]:
        """
        Genera sugerencias de respuesta basadas en el mensaje del usuario
        Args:
            message: Mensaje del usuario
            conversation_history: Historial de la conversación
        Returns:
            Lista de sugerencias de respuesta
        """
        intent = AdvisorAISuggestions.extract_intent(message)

        if not intent:
            return AdvisorAISuggestions._get_generic_suggestions(message)

        suggestions = AdvisorAISuggestions.KNOWLEDGE_BASE[intent]['responses']

        # Priorizar sugerencias basadas en contexto
        return sorted(
            suggestions,
            key=lambda s: AdvisorAISuggestions._calculate_relevance(s, message),
            reverse=True
        )[:3]  # Retornar top 3

    @staticmethod
    def _calculate_relevance(suggestion: str, user_message: str) -> float:
        """Calcula relevancia de una sugerencia basada en similitud"""
        user_words = set(user_message.lower().split())
        suggestion_words = set(suggestion.lower().split())

        # Jaccard similarity
        intersection = len(user_words & suggestion_words)
        union = len(user_words | suggestion_words)

        return intersection / union if union > 0 else 0

    @staticmethod
    def _get_generic_suggestions(message: str) -> List[str]:
        """Sugerencias genéricas cuando no se detecta intención"""
        return [
            "¿Podrías proporcionar más detalles sobre tu consulta?",
            "Entiendo. ¿Hay algo específico que necesites saber?",
            "Claro, estoy aquí para ayudarte. ¿Cuál es tu pregunta exacta?"
        ]

    @staticmethod
    def get_quick_actions(intent: str) -> List[Dict[str, str]]:
        """Retorna acciones rápidas contextuales"""
        quick_actions = {
            "becas": [
                {"label": "Ver tipos de becas", "action": "show_becas"},
                {"label": "Requisitos de solicitud", "action": "requirements"},
                {"label": "Agendar asesoría", "action": "schedule"}
            ],
            "admisiones": [
                {"label": "Ver programas", "action": "programs"},
                {"label": "Proceso de admisión", "action": "process"},
                {"label": "Agendar visita", "action": "visit"}
            ],
            "campus": [
                {"label": "Ver fotos", "action": "gallery"},
                {"label": "Ubicación en mapa", "action": "map"},
                {"label": "Agendar tour", "action": "tour"}
            ],
            "horarios": [
                {"label": "Horarios diurnos", "action": "day_schedule"},
                {"label": "Horarios nocturnos", "action": "night_schedule"},
                {"label": "Calendario académico", "action": "calendar"}
            ]
        }

        return quick_actions.get(intent, [])

    @staticmethod
    def analyze_sentiment(message: str) -> Dict[str, any]:
        """Analiza el sentimiento del mensaje del usuario"""
        # Palabras clave positivas y negativas simples
        positive_words = ["gracias", "excelente", "perfecto", "muy bien", "claro"]
        negative_words = ["problema", "error", "no entiendo", "confundido", "ayuda"]

        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "confidence": max(positive_count, negative_count) / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
        }

    @staticmethod
    def generate_followup_questions(intent: str, message: str) -> List[str]:
        """Genera preguntas de seguimiento inteligentes"""
        followup_map = {
            "becas": [
                "¿Ya tienes un semestre de promedio académico?",
                "¿Necesitas becas para todo el programa o solo este semestre?",
                "¿Has aplicado a becas antes?"
            ],
            "admisiones": [
                "¿Cuál es tu nivel actual de educación?",
                "¿Ya sabes qué carrera deseas estudiar?",
                "¿Prefieres jornada diurna o nocturna?"
            ],
            "campus": [
                "¿Prefieres conocer el campus en persona o virtualmente?",
                "¿Te interesa una facultad específica?",
                "¿Tienes alguna necesidad de accesibilidad especial?"
            ],
            "horarios": [
                "¿Para qué semestre necesitas los horarios?",
                "¿Alguna preferencia de horario?",
                "¿Necesitas información de un programa específico?"
            ]
        }

        return followup_map.get(intent, [
            "¿Hay algo más en lo que pueda ayudarte?",
            "¿Tienes otra pregunta relacionada?"
        ])[:2]

    @staticmethod
    def get_contextualized_response(
        message: str,
        previous_messages: List[str] = None
    ) -> Dict[str, any]:
        """
        Genera una respuesta completamente contextualizada
        Returns: {suggestions, quick_actions, followup_questions, sentiment}
        """
        intent = AdvisorAISuggestions.extract_intent(message)
        sentiment = AdvisorAISuggestions.analyze_sentiment(message)

        return {
            "intent": intent,
            "suggestions": AdvisorAISuggestions.get_suggestions(message, previous_messages),
            "quick_actions": AdvisorAISuggestions.get_quick_actions(intent) if intent else [],
            "followup_questions": AdvisorAISuggestions.generate_followup_questions(intent, message) if intent else [],
            "sentiment": sentiment,
            "confidence": sentiment["confidence"]
        }
