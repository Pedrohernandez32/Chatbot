"""Plugin que expone la información institucional definida en app.py.
Responde preguntas sobre contactos, horario, carreras y becas.
"""
from typing import Optional

SYSTEM_INFO = {
    'contactos': (
        "CONTACTOS:\n"
        "- Teléfono: +57 (604) 590 45 00 – +57 (604) 590 6999\n"
        "- Sede principal: Cra. 87 #30-65, Medellín, Belén – Colombia\n"
        "- Sede Bogotá: Calle 57 # 9-52, Chapinero\n"
        "- Notificaciones judiciales: corresrec@udemedellin.edu.co"
    ),
    'horario': (
        "HORARIO DE ATENCIÓN:\n"
        "- Lunes a viernes de 8:00 a.m. a 12:00 m. y de 2:00 p.m. a 6:00 p.m."
    ),
    'carreras': (
        "CARRERAS DISPONIBLES:\n"
        "- Administración de Empresas (SNIES: 1514)\n"
        "- Ciencia Política (SNIES: 105770)\n"
        "- Computación Científica (SNIES: 103268)\n"
        "- Comunicación Gráfica Publicitaria (SNIES: 11128)\n"
        "- Comunicación y Entretenimiento Digital (SNIES: 103763)\n"
        "- Comunicación y Lenguajes Audiovisuales (SNIES: 14880)\n"
        "- Comunicación y Relaciones Corporativas (SNIES: 3136)\n"
        "- Derecho (SNIES: 1512)\n"
        "- Diseño y Gestión de Espacios (SNIES: 105470)\n"
        "- Diseño y Gestión de la Moda y el Textil (SNIES: 105469)\n"
        "- Diseño y Gestión del Producto (SNIES: 105468)\n"
        "- Economía (SNIES: 1513)\n"
        "- Ingeniería Ambiental (SNIES: 3193)\n"
        "- Ingeniería Civil (SNIES: 1516)\n"
        "- Ingeniería de Sistemas (SNIES: 3134)\n"
        "- Ingeniería Financiera (SNIES: 7255)\n"
        "- Ingeniería Industrial (SNIES: 103149)\n"
        "- Investigación Criminal (SNIES: 90781)\n"
        "- Mercadeo (SNIES: 52403)\n"
        "- Negocios Internacionales (SNIES: 15243)\n"
        "- Psicología"
    ),
    'becas': (
        "BECAS Y ESTÍMULOS:\n"
        "- BECA SOCIAL\n"
        "- BECA DE HONOR\n"
        "- BECA DE EXCELENCIA\n"
        "- BECA MEJORES SABER PRO\n"
        "- ESTÍMULOS MONITORÍAS ACADÉMICAS\n"
        "- ESTÍMULOS ACTIVIDADES DEPORTIVAS\n"
        "- ESTÍMULOS ACTIVIDADES CULTURALES Y ARTÍSTICAS\n"
        "- ESTÍMULO PARA PARTICIPACIONES DESTACADAS EN EVENTOS ACADÉMICOS EXTRACURRICULARES DE RECONOCIDO PRESTIGIO NACIONAL E INTERNACIONAL\n"
        "- ESTÍMULO MULTILINGÜISMO"
    )
}

KEYWORDS = {
    'contacto': ['contacto', 'teléfono', 'telefono', 'email', 'correo', 'llamar'],
    'horario': ['horario', 'cuando abre', 'cuando cierra', 'a que hora', 'que hora'],
    'carreras': ['carrera', 'carreras', 'programa', 'ingenieria', 'administracion', 'psicologia'],
    'becas': ['beca', 'becas', 'estímulo', 'estimul', 'ayuda economica']
}


def info_handler(prompt: str) -> Optional[str]:
    p = prompt.lower()
    for topic, kws in KEYWORDS.items():
        for kw in kws:
            if kw in p:
                return SYSTEM_INFO.get(topic, None)

    # If user asks a generic question about the institution, return a short summary
    if any(w in p for w in ('universidad', 'información', 'informacion', 'institución', 'institucion')):
        # Build a concise summary
        summary = (
            SYSTEM_INFO['contactos'] + '\n\n' + SYSTEM_INFO['horario'] + '\n\n' +
            'Para carreras y becas puedes preguntar específicamente.'
        )
        return summary

    return None


def register(bot) -> None:
    bot.register_handler(info_handler)
