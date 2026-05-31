"""Plugin con respuestas concretas de la Universidad de Medellín.
Prioriza respuestas cortas y relevantes sobre texto largo."""

from typing import Optional
import re

CARRERAS = [
    'Administración de Empresas', 'Ciencia Política', 'Computación Científica',
    'Comunicación Gráfica Publicitaria', 'Comunicación y Entretenimiento Digital',
    'Comunicación y Lenguajes Audiovisuales', 'Comunicación y Relaciones Corporativas',
    'Derecho', 'Diseño y Gestión de Espacios', 'Diseño y Gestión de la Moda y el Textil',
    'Diseño y Gestión del Producto', 'Economía', 'Ingeniería Ambiental', 'Ingeniería Civil',
    'Ingeniería de Sistemas', 'Ingeniería Financiera', 'Ingeniería Industrial',
    'Investigación Criminal', 'Mercadeo', 'Negocios Internacionales', 'Psicología'
]

RESPUESTAS = {
    'contacto_corto': (
        "📞 **Teléfono:** +57 (604) 590 45 00 / 590 6999\n"
        "📍 **Medellín:** Cra. 87 #30-65, Belén\n"
        "📍 **Bogotá:** Calle 57 # 9-52, Chapinero"
    ),
    'horario_corto': (
        "⏰ **Lunes a viernes:** 8:00 a.m. a 12:00 m. y 2:00 p.m. a 6:00 p.m."
    ),
    'becas_corto': (
        "💰 Tenemos becas sociales, de honor, excelencia y estímulos para monitorías, deportes y cultura."
    ),
    'biblioteca_horario': (
        "📚 **Biblioteca UdeM:** Lunes a viernes 7:00 a.m. a 8:00 p.m. | Sábados 8:00 a.m. a 5:00 p.m."
    ),
    'inscripcion_corto': (
        "✍️ Puedes inscribirte online en www.udemedellin.edu.co o llamando a +57 (604) 590 45 00"
    ),
    'admisiones_corto': (
        "📋 Requerimos diploma de bachiller y prueba de admisión. Consulta carreras específicas para requisitos adicionales."
    ),
}

KEYWORDS_MAP = {
    'contacto': {
        'keywords': ['contacto', 'teléfono', 'telefono', 'email', 'correo', 'llamar', 'direccion', 'dirección', 'ubicación', 'ubicacion'],
        'response': 'contacto_corto'
    },
    'horario': {
        'keywords': ['horario', 'cuando abre', 'cuando cierra', 'a que hora', 'que hora', 'funcionamiento'],
        'response': 'horario_corto'
    },
    'becas': {
        'keywords': ['beca', 'becas', 'estímulo', 'estimul', 'ayuda economica', 'economia', 'descuento', 'financier'],
        'response': 'becas_corto'
    },
    'biblioteca': {
        'keywords': ['biblioteca', 'libreria', 'libro', 'material', 'aula'],
        'response': 'biblioteca_horario'
    },
    'inscripcion': {
        'keywords': ['inscrip', 'registr', 'matricul', 'inscribir', 'registro'],
        'response': 'inscripcion_corto'
    },
    'admisiones': {
        'keywords': ['admision', 'admisión', 'requisito', 'titulo', 'diploma'],
        'response': 'admisiones_corto'
    },
}

def buscar_carrera(prompt: str) -> Optional[str]:
    p = prompt.lower()
    for carrera in CARRERAS:
        if carrera.lower() in p:
            return f"✅ **{carrera}** está disponible en UdeM. ¿Quieres información sobre proceso de admisión o contactos?"
    return None

def buscar_categoria(prompt: str) -> Optional[str]:
    p = prompt.lower()
    for categoria, config in KEYWORDS_MAP.items():
        for kw in config['keywords']:
            if kw in p:
                return RESPUESTAS[config['response']]
    return None

def info_handler(prompt: str) -> Optional[str]:
    # Prioridad 1: Búsqueda de carrera específica
    carrera_resp = buscar_carrera(prompt)
    if carrera_resp:
        return carrera_resp

    # Prioridad 2: Búsqueda por categoría
    categoria_resp = buscar_categoria(prompt)
    if categoria_resp:
        return categoria_resp

    # Prioridad 3: Pregunta genérica sobre la universidad
    if any(w in prompt.lower() for w in ('universidad', 'información', 'informacion', 'institución', 'institucion', 'help', 'ayuda')):
        return (
            "Soy el asistente virtual de **Universidad de Medellín**. Puedo ayudarte con:\n"
            "📞 Contactos | ⏰ Horarios | 📚 Carreras | 💰 Becas | 🏫 Admisiones\n\n"
            "¿Qué necesitas saber?"
        )

    return None

def register(bot) -> None:
    bot.register_handler(info_handler)
