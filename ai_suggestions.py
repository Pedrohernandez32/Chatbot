"""
Sistema Avanzado de Sugerencias Inteligentes para Asesores
Usa NLU para sugerir respuestas contextuales basadas en preguntas comunes
Específicamente diseñado para Universidad de Medellín
"""

from typing import List, Dict, Optional
import json
import re

class AdvisorAISuggestions:
    """Genera sugerencias inteligentes para asesores basadas en la conversación"""

    # Base de conocimiento extendida de preguntas frecuentes y respuestas
    KNOWLEDGE_BASE = {
        "becas": {
            "keywords": ["beca", "ayuda económica", "financiamiento", "subsidio", "crédito educativo", "descuento"],
            "category": "💰 Financiamiento",
            "responses": [
                "Tenemos 4 tipos principales de becas: Excelencia (por mérito), Meritoria (desempeño), Socioeconómica y Permanencia. ¿Cuál tipo te interesa?",
                "Las becas de Excelencia cubren hasta 100% de matrícula para estudiantes con promedio 4.5+. ¿Tu promedio es así?",
                "La beca Socioeconómica ayuda estudiantes con dificultades financieras. ¿Necesitas información del proceso?",
                "Puedo ayudarte con el paso a paso para solicitar beca. ¿Ya tienes los documentos preparados?",
                "Las becas varían según tu desempeño académico y situación económica. Cuéntame tu contexto.",
                "¿Buscas beca para primer semestre o estudiante de continuidad? El proceso es diferente."
            ]
        },
        "admisiones": {
            "keywords": ["admisión", "inscripción", "ingreso", "aplicar", "proceso selectivo", "requisitos", "matricular"],
            "category": "📝 Admisiones",
            "responses": [
                "El proceso varía según si vienes de colegio o tienes educación superior. ¿Cuál es tu caso?",
                "Para estudiantes de colegio: prueba de admisión + documentos. Para profesionales: análisis de antecedentes.",
                "Tienes 3 opciones: Prueba de Admisión, Análisis de Antecedentes, o Equivalencia de Carrera Completa.",
                "¿Tienes documento de identidad válido? Ese es el primer requisito para iniciar inscripción.",
                "El próximo período de inscripción abre en...[verificar calendario]. ¿Quieres que agende tu cita?",
                "Podemos hacer tu inscripción 100% en línea. ¿Prefieres ir a campus o hacerlo desde casa?"
            ]
        },
        "campus": {
            "keywords": ["campus", "ubicación", "sedes", "dónde", "localización", "infraestructura", "edificio", "biblioteca"],
            "category": "🏫 Campus",
            "responses": [
                "Campus Principal en Sabaneta: La más completa con biblioteca, gimnasio, cafetería, laboratorios.",
                "Campus Medellín Centro: Perfecto para estudiantes de ciudad, zona comercial de Junín.",
                "Campus Envigado: Especializado en ingeniería, con laboratorios de última generación.",
                "Campus Bello: Dedicado a programas de educación continua y especialización.",
                "¿Quieres agendar una visita guiada? Tenemos tours todas las semanas.",
                "Cada campus tiene servicios de bienestar estudiantil (psicología, salud, deportes)."
            ]
        },
        "horarios": {
            "keywords": ["horario", "clase", "sesión", "calendario académico", "jornada", "turno", "noche", "día"],
            "category": "⏰ Horarios",
            "responses": [
                "Ofrecemos jornada Diurna (7am-2pm) y Nocturna (6pm-10pm). ¿Cuál se adapta a tu tiempo?",
                "El calendario académico está dividido en 2 semestres: Enero-Mayo y Julio-Noviembre.",
                "Cada carrera tiene horarios específicos. ¿Cuál programa te interesa?",
                "Clases presenciales lunes a viernes. Los horarios se entregan en inscripción.",
                "Los semestres tienen 16 semanas de clase + evaluaciones finales.",
                "¿Necesitas flexibilidad? Algunos programas tienen componentes virtuales."
            ]
        },
        "contacto": {
            "keywords": ["contacto", "teléfono", "email", "llamar", "contactar", "comunicarse", "dirección", "whatsapp"],
            "category": "📞 Contacto",
            "responses": [
                "Teléfono general: +57 4 3309500 | Email: info@udemedellín.edu.co | 8am-5pm (lunes-viernes)",
                "WhatsApp: +57 320 XXXXXXX para consultas rápidas (respuesta en 24 horas)",
                "Campus Principal Sabaneta: Cra 85 No 49A-65, Medellín",
                "¿Necesitas hablar con un departamento específico? Te doy números directos.",
                "También puedes venir personalmente a cualquier campus. Asesorías sin cita.",
                "Para emergencias (estudiante): Línea de Bienestar +57 4 XXXXXXX disponible 24/7"
            ]
        },
        "profesores": {
            "keywords": ["profesor", "docente", "instructor", "maestro", "enseña", "académico"],
            "category": "👨‍🏫 Docentes",
            "responses": [
                "Nuestros docentes tienen especialización de maestría mínimo. ¿De qué programa?",
                "Puedo darte info de un docente específico. ¿Sabes su nombre?",
                "Los docentes tienen horarios de atención (tutoría) fuera de clase. ¿Necesitas contactar uno?",
                "¿Buscas información de calificaciones o proceso académico de un docente?",
                "Cada facultad tiene coordinadores académicos que pueden ayudarte con temas de profesores.",
                "Si tienes problema académico con un docente, contacta al coordinador de tu programa."
            ]
        },
        "decanos": {
            "keywords": ["decano", "director", "facultad", "responsable", "encargado", "coordinador", "jefe"],
            "category": "📋 Administración",
            "responses": [
                "Tenemos 6 facultades: Ingeniería, Ciencias Exactas, Ciencias Sociales, Administración, Diseño, Derecho.",
                "Cada facultad tiene un Decano y equipo coordinador. ¿Cuál facultad buscas?",
                "Los Decanos tienen disponibilidad para asesorías académicas. Podemos agendar cita.",
                "¿Necesitas contactar administración por tema de calificaciones, cambios de programa, etc?",
                "La Rectoría está disponible para temas académicos escalados. ¿Es urgente?",
                "Para cambios de programa o apelaciones, contacta directamente al Decano de tu facultad."
            ]
        },
        "carreras": {
            "keywords": ["carrera", "programa", "pregrado", "licenciatura", "ingeniería", "derecho", "diseño", "comunicación", "administración", "enfermería"],
            "category": "🎓 Programas",
            "responses": [
                "Tenemos 20+ programas de pregrado acreditados. ¿Qué área te interesa: Ingeniería, Salud, Derecho, Diseño?",
                "Ingeniería en Sistemas: 10 semestres, acreditación ABET, prácticas desde 5to semestre.",
                "Ingeniería Civil: Énfasis en sostenibilidad, laboratorios de estructuras y materiales.",
                "Derecho: Con énfasis en derechos humanos, mediación y resolución de conflictos.",
                "Diseño Gráfico: Carrera de 8 semestres con énfasis en diseño digital y UX.",
                "Comunicación Social: Formación en periodismo digital, audiovisuales, gestión de marca."
            ]
        },
        "financiamiento": {
            "keywords": ["pago", "matrícula", "valor", "precio", "cuota", "crédito", "plan", "cuotas"],
            "category": "💳 Costos",
            "responses": [
                "El valor de matrícula varía por programa. ¿Cuál carrera te interesa?",
                "Ofrecemos planes de pago en cuotas (2, 4, 6 o 12 cuotas sin interés).",
                "Con Beca de Excelencia puedes tener 50% o 100% de descuento en matrícula.",
                "Hay descuento por hermanos (10%) y empleados empresas aliadas.",
                "¿Buscas crédito educativo? Trabajamos con bancos e instituciones financieras.",
                "El costo total varía. ¿De qué programa quieres saber el valor exacto?"
            ]
        },
        "bienestar": {
            "keywords": ["bienestar", "salud", "psicología", "deporte", "actividades", "eventos", "vida estudiantil"],
            "category": "💪 Bienestar",
            "responses": [
                "Tenemos servicios de psicología gratis para estudiantes. ¿Necesitas cita?",
                "Actividades deportivas: Fútbol, vóleybol, natación, gimnasia, atletismo.",
                "Clubs estudiantiles: Programación, emprendimiento, artes, voluntariado, etc.",
                "Cada semestre hay festivales de integración y actividades culturales.",
                "Enfermería en campus para atención básica de salud.",
                "¿Tienes discapacidad? Tenemos programa de inclusión y apoyos especiales."
            ]
        },
        "graduados": {
            "keywords": ["egresado", "graduado", "egreso", "diploma", "certificado", "titulación"],
            "category": "🎖️ Graduación",
            "responses": [
                "Una vez termines 160 créditos y cumplas requisitos, puedes solicitar egreso.",
                "El trabajo de grado puede ser: Tesis, Proyecto Aplicado o Seminario.",
                "El diploma se entrega en ceremonia oficial. Hay varias por año.",
                "Para egresados hay ofertas de educación continua y especializaciones.",
                "¿Necesitas constancia de estudiante o transcripto? Está disponible online.",
                "Los egresados mantienen acceso a servicios como biblioteca y educación continua."
            ]
        },
        "inscripcion": {
            "keywords": ["inscripción", "matricular", "registrar", "enroll", "inscribir", "proceso"],
            "category": "📝 Registro",
            "responses": [
                "La inscripción tiene varios pasos: Prueba de admisión → Asignación de horario → Pago de matrícula.",
                "Puedes empezar el proceso online en nuestro portal: portal.udemedellin.edu.co",
                "Necesitas documento de identidad, ICFES (si vienes de colegio), y referencia de pago.",
                "¿Primera vez en universidad? Te guiamos paso a paso en inscripción.",
                "El período de inscripción abre cada semestre. ¿Cuándo planeas ingresar?",
                "Ofrecemos inscripción en línea 100% o presencial en campus."
            ]
        },
        "tecnologia": {
            "keywords": ["plataforma virtual", "moodle", "aula virtual", "zoom", "Teams", "tecnología", "online"],
            "category": "💻 Tecnología",
            "responses": [
                "Nuestra plataforma es Moodle. Todas las clases, tareas y calificaciones están allí.",
                "Para clase virtual usamos Zoom o Microsoft Teams según el docente.",
                "Tienes email institucional: tu_usuario@estudiante.udemedellin.edu.co",
                "El portal estudiantil te permite ver calificaciones, horarios y documentos.",
                "¿Necesitas ayuda técnica? El Departamento de TI está disponible 8am-5pm.",
                "Hay capacitaciones gratis sobre uso de plataforma el primer mes de semestre."
            ]
        },
        "becarios": {
            "keywords": ["becario", "asistente", "monitor", "auxiliar", "práctica", "experiencia"],
            "category": "👨‍💼 Oportunidades",
            "responses": [
                "Como becario puedes asistir a profesores o departamentos (10-15 horas/semana).",
                "Las prácticas pueden ser laborales (empresa) o académicas (universidad).",
                "Desde 5to semestre de ingeniería, es obligatorio hacer práctica profesional (6 meses).",
                "Hay convenios con +500 empresas para prácticas remuneradas.",
                "¿Te interesa ser monitor o monitor? Se abre convocatoria cada semestre.",
                "El programa de pasantías internacionales también está disponible para 8vo semestre+."
            ]
        },
        "cambios": {
            "keywords": ["cambio de programa", "traslado", "cambiar carrera", "retirar materia", "cambiar horario"],
            "category": "♻️ Cambios",
            "responses": [
                "Puedes cambiar de programa hasta 3er semestre sin trámites complejos.",
                "Las solicitudes de cambio se hacen en coordinación académica de tu facultad.",
                "Algunos créditos pueden convalidarse si cambias a carrera similar.",
                "¿Tienes 2+ semestres? Necesitarás reunión con Decano para aprobar cambio.",
                "El cambio de horario se solicita antes del inicio del semestre.",
                "Retiro de materias: Tienes hasta la semana 4 sin penalización académica."
            ]
        }
    }

    @staticmethod
    def extract_intent(message: str) -> Optional[str]:
        """Detecta la intención del mensaje del usuario con múltiples niveles"""
        message_lower = message.lower()
        message_clean = re.sub(r'[^\w\s]', ' ', message_lower)  # Limpiar puntuación

        best_intent = None
        best_score = 0

        for intent, data in AdvisorAISuggestions.KNOWLEDGE_BASE.items():
            score = 0

            # Búsqueda de palabras clave exactas
            for keyword in data['keywords']:
                if keyword in message_clean:
                    score += 10

            # Búsqueda de palabras clave como parte de palabras
            for keyword in data['keywords']:
                words = message_clean.split()
                for word in words:
                    if len(keyword) > 3 and keyword in word:
                        score += 5

            # Penalización si hay demasiadas palabras (pregunta no relacionada)
            word_count = len(message_clean.split())
            if word_count > 20:
                score *= 0.9

            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent if best_score > 0 else None

    @staticmethod
    def get_suggestions(message: str, conversation_history: List[Dict] = None) -> List[str]:
        """
        Genera sugerencias de respuesta basadas en el mensaje del usuario
        Considera contexto de conversación anterior y especificidad de preguntas
        """
        intent = AdvisorAISuggestions.extract_intent(message)

        if not intent:
            # Intenta inferir intent de la historia de conversación
            if conversation_history and len(conversation_history) > 0:
                last_intent = AdvisorAISuggestions.extract_intent(
                    conversation_history[-1].get('content', '')
                )
                if last_intent:
                    intent = last_intent

        if not intent:
            return AdvisorAISuggestions._get_generic_suggestions(message)

        suggestions = AdvisorAISuggestions.KNOWLEDGE_BASE[intent]['responses']

        # Priorizar sugerencias basadas en relevancia al mensaje
        ranked = sorted(
            suggestions,
            key=lambda s: AdvisorAISuggestions._calculate_relevance(s, message),
            reverse=True
        )

        # Retornar top 4 (expandido de 3)
        return ranked[:4]

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
        # Analizar la pregunta para dar sugerencias más específicas
        question_words = ["qué", "quién", "dónde", "cuándo", "cómo", "cuál", "cuánto"]
        is_question = any(word in message.lower() for word in question_words) or message.lower().endswith("?")

        if is_question:
            return [
                "Esa es buena pregunta. ¿Puedes darme más contexto para ayudarte mejor?",
                "Entiendo tu pregunta. ¿Es sobre un programa, proceso administrativo, o tema académico específico?",
                "Claro, voy a ayudarte. ¿Hay algún aspecto específico en el que pueda profundizar?"
            ]
        else:
            return [
                "Entiendo lo que dices. ¿Hay algo específico con lo que pueda ayudarte?",
                "Gracias por la información. ¿Cuál es tu principal consulta ahora?",
                "¿Hay algo específico sobre Universidad de Medellín en lo que pueda asistirte?"
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
        """Analiza el sentimiento del mensaje del usuario con mayor precisión"""
        message_lower = message.lower()

        # Diccionarios expandidos de palabras clave
        positive_words = [
            "gracias", "excelente", "perfecto", "muy bien", "claro", "entendido",
            "magnífico", "fantástico", "amor", "feliz", "alegre", "bravo",
            "increíble", "maravilloso", "genial", "buen", "bien", "positivo",
            "eficiente", "rápido", "fácil"
        ]

        negative_words = [
            "problema", "error", "no entiendo", "confundido", "ayuda", "difícil",
            "malo", "terrible", "horrible", "frustrado", "triste", "enojado",
            "dificultad", "complicado", "lento", "tardanza", "demora",
            "insatisfecho", "decepcionado", "incómodo"
        ]

        # Amplificadores de sentimiento
        amplifiers = {"muy": 1.5, "demasiado": 1.5, "realmente": 1.3, "bastante": 1.3}

        positive_score = 0
        negative_score = 0

        words = message_lower.split()

        for i, word in enumerate(words):
            word_clean = re.sub(r'[^\w]', '', word)

            # Buscar palabras con amplificadores
            amplifier = 1.0
            if i > 0:
                prev_word = re.sub(r'[^\w]', '', words[i-1])
                amplifier = amplifiers.get(prev_word, 1.0)

            if word_clean in positive_words or any(pos in word_clean for pos in positive_words):
                positive_score += amplifier

            if word_clean in negative_words or any(neg in word_clean for neg in negative_words):
                negative_score += amplifier

        # Determinar sentimiento
        if positive_score > negative_score:
            sentiment = "positive"
            confidence = min(1.0, positive_score / (positive_score + negative_score + 1))
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = min(1.0, negative_score / (positive_score + negative_score + 1))
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "score": round(positive_score - negative_score, 2)
        }

    @staticmethod
    def generate_followup_questions(intent: str, message: str) -> List[str]:
        """Genera preguntas de seguimiento contextuales e inteligentes"""
        followup_map = {
            "becas": [
                "¿Tu promedio actual es superior a 4.5 (para Beca de Excelencia)?",
                "¿Necesitas cobertura para todo el programa o solo este semestre?",
                "¿Ya has participado en otros programas de becas?"
            ],
            "admisiones": [
                "¿Vienes directamente de colegio o ya tienes educación superior?",
                "¿Cuál es tu carrera de interés y área de concentración?",
                "¿Te funcionaría mejor jornada diurna (7am-2pm) o nocturna (6pm-10pm)?"
            ],
            "campus": [
                "¿Prefieres visita presencial con tour guiado o virtual por video?",
                "¿Hay algún programa o facultad que quieras conocer específicamente?",
                "¿Tienes necesidades especiales de accesibilidad o movilidad?"
            ],
            "horarios": [
                "¿Ingresas en el próximo semestre o necesitas info para después?",
                "¿Hay algún horario específico que no te funcione por trabajo o compromisos?",
                "¿Quieres horario concentrado (lunes-viernes) o distribuido?"
            ],
            "carreras": [
                "¿Tienes afinidad por áreas técnicas, sociales, artísticas, o legales?",
                "¿Buscas una carrera corta (8 sem) o larga (10+ sem)?",
                "¿Te interesa un programa con énfasis en algo específico?"
            ],
            "financiamiento": [
                "¿Cuentas con apoyo económico total o necesitas cobertura parcial?",
                "¿Prefieres pagar mensual (12 cuotas) o semestral (2 cuotas)?",
                "¿Eres elegible para alguna beca o beneficio especial?"
            ],
            "bienestar": [
                "¿Es tu primera vez en educación superior?",
                "¿Te interesa actividades deportivas, culturales, o ambas?",
                "¿Tienes alguna condición de salud que debamos considerar?"
            ]
        }

        questions = followup_map.get(intent, [
            "¿Hay algo más específico en lo que pueda ayudarte?",
            "¿Tienes otra pregunta relacionada con tu consulta?"
        ])

        return questions[:3]  # Retornar máximo 3 preguntas

    @staticmethod
    def extract_entities(message: str) -> Dict[str, List[str]]:
        """Extrae entidades/información del mensaje (nombres, palabras clave, etc)"""
        entities = {
            "programs": [],
            "campuses": [],
            "time_periods": [],
            "financial_keywords": [],
            "urgency": "normal"
        }

        message_lower = message.lower()

        # Carrera/programas
        programs = ["ingeniería", "sistemas", "civil", "derecho", "diseño", "comunicación",
                    "administración", "enfermería", "contabilidad", "psicología", "licenciatura"]
        for prog in programs:
            if prog in message_lower:
                entities["programs"].append(prog)

        # Ubicaciones/campus
        campuses = ["sabaneta", "medellín", "envigado", "bello", "centro"]
        for campus in campuses:
            if campus in message_lower:
                entities["campuses"].append(campus)

        # Períodos de tiempo
        if any(word in message_lower for word in ["ahora", "ya", "inmediato", "urgente", "rápido"]):
            entities["urgency"] = "urgent"
        elif any(word in message_lower for word in ["próximo", "siguiente", "futuro", "después"]):
            entities["urgency"] = "future"

        # Palabras financieras
        financial = ["beca", "precio", "costo", "valor", "matrícula", "pago", "crédito"]
        for word in financial:
            if word in message_lower:
                entities["financial_keywords"].append(word)

        return entities

    @staticmethod
    def get_contextualized_response(
        message: str,
        previous_messages: List[str] = None
    ) -> Dict[str, any]:
        """
        Genera una respuesta completamente contextualizada con análisis profundo
        Returns: {intent, suggestions, quick_actions, followup_questions, sentiment, entities, category}
        """
        intent = AdvisorAISuggestions.extract_intent(message)
        sentiment = AdvisorAISuggestions.analyze_sentiment(message)
        entities = AdvisorAISuggestions.extract_entities(message)

        # Obtener categoría
        category = "❓ Consulta General"
        if intent:
            category = AdvisorAISuggestions.KNOWLEDGE_BASE[intent].get('category', category)

        response = {
            "intent": intent,
            "category": category,
            "suggestions": AdvisorAISuggestions.get_suggestions(message, previous_messages),
            "quick_actions": AdvisorAISuggestions.get_quick_actions(intent) if intent else [],
            "followup_questions": AdvisorAISuggestions.generate_followup_questions(intent, message) if intent else [],
            "sentiment": sentiment,
            "confidence": sentiment["confidence"],
            "entities": entities,
            "is_urgent": entities["urgency"] == "urgent",
            "is_specific": len(entities["programs"]) > 0 or len(entities["campuses"]) > 0
        }

        return response
