"""Plugin con respuestas concretas de la Universidad de Medellín.
Prioriza respuestas cortas y relevantes sobre texto largo."""

from typing import Optional, Tuple
import re
import json

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
    'contacto': {
        'corto': "📞 **Teléfono:** +57 (604) 590 45 00 / 590 6999\n📍 **Medellín:** Cra. 87 #30-65, Belén\n📍 **Bogotá:** Calle 57 # 9-52, Chapinero",
        'expandido': "**CONTACTOS UNIVERSIDAD DE MEDELLÍN**\n\n**SEDE MEDELLÍN**\n- Dirección: Carrera 87 #30-65, Medellín, Belén, Antioquia\n- Teléfono: +57 (604) 590 45 00\n- Teléfono: +57 (604) 590 6999\n\n**SEDE BOGOTÁ**\n- Dirección: Calle 57 # 9-52, Chapinero, Bogotá D.C.\n\n**CONTACTO LEGAL**\n- Notificaciones judiciales: corresrec@udemedellin.edu.co\n\n**HORARIO DE ATENCIÓN**\n- Lunes a viernes: 8:00 a.m. a 12:00 m. y 2:00 p.m. a 6:00 p.m."
    },
    'horario': {
        'corto': "⏰ **Lunes a viernes:** 8:00 a.m. a 12:00 m. y 2:00 p.m. a 6:00 p.m.",
        'expandido': "**HORARIO DE ATENCIÓN UNIVERSIDAD**\n\n**HORARIO GENERAL**\n- Lunes a viernes: 8:00 a.m. a 12:00 m. y 2:00 p.m. a 6:00 p.m.\n\n**BIBLIOTECA**\n- Lunes a viernes: 7:00 a.m. a 8:00 p.m.\n- Sábados: 8:00 a.m. a 5:00 p.m.\n\n**PISCINA**\n- Lunes-viernes: 6:00-8:00 a.m. y 6:00-9:00 p.m.\n- Sábados: 8:00 a.m. a 12:00 m.\n- Domingos y festivos: Cerrada\n\n*Para contactar en horarios especiales, usa WhatsApp o email.*"
    },
    'becas': {
        'corto': "💰 Tenemos becas sociales, de honor, excelencia y estímulos para monitorías, deportes y cultura.",
        'expandido': "**BECAS Y ESTÍMULOS ECONÓMICOS**\n\n**BECAS**\n- Beca Social (necesidad económica)\n- Beca de Honor (excelencia académica)\n- Beca de Excelencia (desempeño sobresaliente)\n- Beca Mejores SABER PRO (resultado de prueba)\n\n**ESTÍMULOS**\n- Monitorías Académicas\n- Actividades Deportivas\n- Actividades Culturales y Artísticas\n- Participaciones en Eventos Académicos Externos\n- Multilingüismo\n\n**GESTIÓN**\nContacta a Secretaría Estudiantil en horarios de atención o escribe a info@udemedellin.edu.co"
    },
    'biblioteca': {
        'corto': "📚 **Biblioteca UdeM:** Lunes a viernes 7:00 a.m. a 8:00 p.m. | Sábados 8:00 a.m. a 5:00 p.m.",
        'expandido': "**BIBLIOTECA UNIVERSIDAD DE MEDELLÍN**\n\n**HORARIO**\n- Lunes a viernes: 7:00 a.m. a 8:00 p.m.\n- Sábados: 8:00 a.m. a 5:00 p.m.\n- Domingos: Cerrada\n\n**SERVICIOS**\n- Consulta de libros físicos\n- Acceso a bases de datos digitales\n- Computadoras para investigación\n- Salas de estudio grupal\n- Préstamo a domicilio\n\n**REQUISITOS**\n- Carné de estudiante vigente\n- Máximo 5 libros simultáneamente\n- Plazo de devolución: 14 días"
    },
    'inscripcion': {
        'corto': "✍️ Puedes inscribirte online en www.udemedellin.edu.co o llamando a +57 (604) 590 45 00",
        'expandido': "**PROCESO DE INSCRIPCIÓN**\n\n**OPCIÓN 1: ONLINE**\n- Ingresa a www.udemedellin.edu.co\n- Selecciona tu carrera\n- Completa el formulario\n- Realiza prueba de admisión\n\n**OPCIÓN 2: PRESENCIAL**\n- Visita nuestras sedes en Medellín o Bogotá\n- Horario: Lunes a viernes 8:00 a.m. a 12:00 m. y 2:00-6:00 p.m.\n- Lleva: Documento de identidad y diploma de bachiller\n\n**OPCIÓN 3: TELÉFONO**\n- +57 (604) 590 45 00 / 590 6999\n- Solicita información sin compromiso\n\n**PRÓXIMAS FECHAS DE ADMISIÓN**\nConsulta en www.udemedellin.edu.co/admisiones"
    },
    'admisiones': {
        'corto': "📋 Requerimos diploma de bachiller y prueba de admisión. Consulta carreras específicas para requisitos adicionales.",
        'expandido': "**REQUISITOS DE ADMISIÓN**\n\n**REQUISITOS GENERALES**\n- Diploma de Bachiller acreditado\n- Cédula de Ciudadanía o Pasaporte\n- Prueba de Admisión (sedes UdeM)\n\n**DOCUMENTOS A PRESENTAR**\n- Fotocopia del diploma de bachiller\n- Fotocopia del documento de identidad\n- 2 fotos 3x4 a color\n- Formulario de solicitud (se proporciona)\n\n**REQUISITOS POR PROGRAMA**\n- Algunos programas requieren entrevista\n- Ingeniería: Énfasis en matemáticas\n- Diseño: Portafolio de trabajo\n- Psicología: Entrevista personal\n\n**FECHAS**\nProceso continuo. Consulta www.udemedellin.edu.co para próximas cohortes"
    },
}

KEYWORDS_MAP = {
    'contacto': ['contacto', 'teléfono', 'telefono', 'email', 'correo', 'llamar', 'direccion', 'dirección', 'ubicación', 'ubicacion'],
    'horario': ['horario', 'cuando abre', 'cuando cierra', 'a que hora', 'que hora', 'funcionamiento'],
    'becas': ['beca', 'becas', 'estímulo', 'estimul', 'ayuda economica', 'economia', 'descuento', 'financier'],
    'biblioteca': ['biblioteca', 'libreria', 'libro', 'material', 'aula'],
    'inscripcion': ['inscrip', 'registr', 'matricul', 'inscribir', 'registro'],
    'admisiones': ['admision', 'admisión', 'requisito', 'titulo', 'diploma'],
}

def buscar_carrera(prompt: str) -> Optional[dict]:
    p = prompt.lower()
    for carrera in CARRERAS:
        if carrera.lower() in p:
            return {
                'text': f"✅ **{carrera}** está disponible en UdeM. ¿Quieres información sobre proceso de admisión o contactos?",
                'category': 'carrera',
                'has_more': False
            }
    return None

def buscar_categoria(prompt: str) -> Optional[dict]:
    p = prompt.lower()
    for categoria, keywords in KEYWORDS_MAP.items():
        for kw in keywords:
            if kw in p:
                if categoria in RESPUESTAS:
                    return {
                        'text': RESPUESTAS[categoria]['corto'],
                        'category': categoria,
                        'has_more': True
                    }
    return None

def info_handler(prompt: str) -> Optional[str]:
    # Prioridad 1: Búsqueda de carrera específica
    carrera_resp = buscar_carrera(prompt)
    if carrera_resp:
        return json.dumps(carrera_resp, ensure_ascii=False)

    # Prioridad 2: Búsqueda por categoría
    categoria_resp = buscar_categoria(prompt)
    if categoria_resp:
        return json.dumps(categoria_resp, ensure_ascii=False)

    # Prioridad 3: Pregunta genérica
    if any(w in prompt.lower() for w in ('universidad', 'información', 'informacion', 'institución', 'institucion', 'help', 'ayuda')):
        response = {
            'text': "Soy el asistente virtual de **Universidad de Medellín**. Puedo ayudarte con:\n📞 Contactos | ⏰ Horarios | 📚 Carreras | 💰 Becas | 🏫 Admisiones\n\n¿Qué necesitas saber?",
            'category': 'general',
            'has_more': False
        }
        return json.dumps(response, ensure_ascii=False)

    return None

def register(bot) -> None:
    bot.register_handler(info_handler)
