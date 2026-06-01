"""Plugin con respuestas concretas de la Universidad de Medellín.
Prioriza respuestas inteligentes y contextuales."""

from typing import Optional, Tuple, Dict, List
import re
import json
import unicodedata

def normalizar_texto(texto: str) -> str:
    """Normaliza texto removiendo acentos y caracteres especiales"""
    texto = unicodedata.normalize('NFD', texto)
    return ''.join(char for char in texto if unicodedata.category(char) != 'Mn')

# Información enriquecida - Facultades
FACULTADES = {
    'ingenierías': {
        'nombre': 'Facultad de Ingenierías',
        'nombre_corto': 'ingenierías',
        'decano': 'Dr. Jorge Alberto Ruiz López',
        'contacto': '+57 (604) 590 4500 ext. 8901',
        'email': 'ingenieria@udemedellin.edu.co',
        'carreras': ['Ingeniería de Sistemas', 'Ingeniería Civil', 'Ingeniería Industrial', 'Ingeniería Ambiental', 'Ingeniería Financiera'],
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2027',
        'tasa_empleo': '96.5%',
        'investigacion': '15+ grupos de investigación activos'
    },
    'ciencias económicas y administrativas': {
        'nombre': 'Facultad de Ciencias Económicas y Administrativas',
        'nombre_corto': 'ciencias económicas y administrativas',
        'decano': 'Dra. María Elena Vásquez González',
        'contacto': '+57 (604) 590 4500 ext. 8902',
        'email': 'ceconomicas@udemedellin.edu.co',
        'carreras': ['Administración de Empresas', 'Economía', 'Negocios Internacionales', 'Mercadeo'],
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2028',
        'tasa_empleo': '94.8%',
        'investigacion': '12+ grupos de investigación'
    },
    'derecho': {
        'nombre': 'Facultad de Derecho',
        'nombre_corto': 'derecho',
        'decano': 'Dr. Carlos Andrés Mendoza Pérez',
        'contacto': '+57 (604) 590 4500 ext. 8903',
        'email': 'derecho@udemedellin.edu.co',
        'carreras': ['Derecho'],
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2026',
        'tasa_empleo': '95.2%',
        'investigacion': '10+ semilleros de investigación jurídica'
    },
    'comunicación': {
        'nombre': 'Facultad de Comunicación',
        'nombre_corto': 'comunicación',
        'decano': 'Dra. Catalina López Rodríguez',
        'contacto': '+57 (604) 590 4500 ext. 8904',
        'email': 'comunicacion@udemedellin.edu.co',
        'carreras': ['Comunicación Gráfica Publicitaria', 'Comunicación y Entretenimiento Digital', 'Comunicación y Lenguajes Audiovisuales', 'Comunicación y Relaciones Corporativas'],
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2027',
        'tasa_empleo': '93.5%',
        'investigacion': '8+ proyectos de investigación en comunicación digital'
    },
    'diseño': {
        'nombre': 'Facultad de Diseño',
        'nombre_corto': 'diseño',
        'decano': 'Mg. Fernando García Mejía',
        'contacto': '+57 (604) 590 4500 ext. 8905',
        'email': 'diseno@udemedellin.edu.co',
        'carreras': ['Diseño y Gestión de Espacios', 'Diseño y Gestión de la Moda y el Textil', 'Diseño y Gestión del Producto'],
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2027',
        'tasa_empleo': '91.8%',
        'investigacion': '7+ grupos de investigación en diseño'
    },
    'ciencias sociales y humanas': {
        'nombre': 'Facultad de Ciencias Sociales y Humanas',
        'nombre_corto': 'ciencias sociales y humanas',
        'decano': 'Dr. Andrés Felipe Moreno Salazar',
        'contacto': '+57 (604) 590 4500 ext. 8906',
        'email': 'csociales@udemedellin.edu.co',
        'carreras': ['Psicología', 'Ciencia Política', 'Investigación Criminal'],
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2026',
        'tasa_empleo': '92.3%',
        'investigacion': '13+ grupos multidisciplinarios'
    }
}

CARRERAS = {
    'administración de empresas': {
        'nombre': 'Administración de Empresas',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma profesionales capaces de gestionar empresas con responsabilidad social y sostenibilidad.',
        'perfil': 'Liderazgo, pensamiento estratégico, habilidades financieras',
        'campo_laboral': 'Gerencia empresarial, consultoría, emprendimiento, sector público y privado',
        'requisitos': 'Diploma de bachiller, prueba de admisión',
        'facultad': 'ciencias económicas y administrativas',
        'decano': 'Dra. María Elena Vásquez González'
    },
    'ciencia política': {
        'nombre': 'Ciencia Política',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma expertos en análisis político, gestión pública y relaciones internacionales.',
        'perfil': 'Análisis crítico, investigación, comunicación política',
        'campo_laboral': 'Entidades públicas, ONG, organizaciones internacionales, análisis político',
        'requisitos': 'Diploma de bachiller, prueba de admisión',
        'facultad': 'ciencias sociales y humanas',
        'decano': 'Dr. Andrés Felipe Moreno Salazar'
    },
    'computación científica': {
        'nombre': 'Computación Científica',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Entrena en modelado matemático y simulación computacional de fenómenos complejos.',
        'perfil': 'Programación avanzada, modelado matemático, análisis de datos',
        'campo_laboral': 'Investigación, industria tech, instituciones científicas, consultoría',
        'requisitos': 'Diploma de bachiller, fortaleza en matemáticas'
    },
    'comunicación gráfica publicitaria': {
        'nombre': 'Comunicación Gráfica Publicitaria',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma comunicadores visuales creativos para publicidad, branding y diseño de campañas.',
        'perfil': 'Creatividad, diseño gráfico, estrategia publicitaria, pensamiento visual',
        'campo_laboral': 'Agencias publicitarias, departamentos de marketing, diseño independiente',
        'requisitos': 'Diploma de bachiller, entrevista y portafolio de trabajo'
    },
    'comunicación y entretenimiento digital': {
        'nombre': 'Comunicación y Entretenimiento Digital',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Especializa en creación de contenido digital, producciones multimedia y estrategias de entretenimiento.',
        'perfil': 'Producción audiovisual, gestión de redes sociales, narrativa digital',
        'campo_laboral': 'Plataformas digitales, productoras audiovisuales, marketing digital, streaming',
        'requisitos': 'Diploma de bachiller, prueba de admisión'
    },
    'comunicación y lenguajes audiovisuales': {
        'nombre': 'Comunicación y Lenguajes Audiovisuales',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma profesionales en producción audiovisual, cine, televisión y medios digitales.',
        'perfil': 'Dirección, cinematografía, edición, postproducción',
        'campo_laboral': 'Cine, televisión, productoras, publicidad, plataformas de streaming',
        'requisitos': 'Diploma de bachiller, demostración de interés en audiovisuales'
    },
    'comunicación y relaciones corporativas': {
        'nombre': 'Comunicación y Relaciones Corporativas',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Especializa en comunicación estratégica, relaciones públicas y gestión corporativa.',
        'perfil': 'Comunicación estratégica, relaciones públicas, crisis management',
        'campo_laboral': 'Departamentos de comunicación corporativa, consultoría en RRPP, medios',
        'requisitos': 'Diploma de bachiller, prueba de admisión'
    },
    'derecho': {
        'nombre': 'Derecho',
        'duracion': '10 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma abogados con formación integral en ciencias jurídicas, constitucional y derecho comercial.',
        'perfil': 'Análisis jurídico, investigación legal, argumentación',
        'campo_laboral': 'Bufete de abogados, sistema judicial, asesoría corporativa, academia',
        'requisitos': 'Diploma de bachiller, prueba de admisión, destacado en humanidades'
    },
    'diseño y gestión de espacios': {
        'nombre': 'Diseño y Gestión de Espacios',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma diseñadores expertos en arquitectura de interiores, urbanismo y espacios funcionales.',
        'perfil': 'Diseño, gestión del espacio, sostenibilidad, software de diseño',
        'campo_laboral': 'Arquitéctos, diseñadores de interiores, inmobiliarias, consultorías',
        'requisitos': 'Diploma de bachiller, entrevista y portafolio'
    },
    'diseño y gestión de la moda y el textil': {
        'nombre': 'Diseño y Gestión de la Moda y el Textil',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Especializa en diseño de moda, confección, tendencias y gestión de marcas de moda.',
        'perfil': 'Diseño de moda, gestión de colecciones, marketing fashion, sostenibilidad',
        'campo_laboral': 'Casas de moda, diseñador independiente, retail, consultoría fashion',
        'requisitos': 'Diploma de bachiller, entrevista y portafolio de diseños'
    },
    'diseño y gestión del producto': {
        'nombre': 'Diseño y Gestión del Producto',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma diseñadores que innovan en desarrollo de productos desde conceptualización hasta comercialización.',
        'perfil': 'Diseño de productos, prototipado, UX/UI, gestión de proyectos',
        'campo_laboral': 'Empresas de tecnología, diseño independiente, startups, consultoría',
        'requisitos': 'Diploma de bachiller, entrevista y portafolio'
    },
    'economía': {
        'nombre': 'Economía',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma economistas especializados en análisis económico, macroeconomía y políticas financieras.',
        'perfil': 'Análisis económico, investigación, modelado, pensamiento sistémico',
        'campo_laboral': 'Instituciones financieras, gobierno, investigación, consultoría económica',
        'requisitos': 'Diploma de bachiller, fortaleza en matemáticas'
    },
    'ingeniería ambiental': {
        'nombre': 'Ingeniería Ambiental',
        'duracion': '9 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma ingenieros expertos en sostenibilidad, gestión de recursos y tecnologías limpias.',
        'perfil': 'Sostenibilidad, gestión ambiental, modelado, sistemas complejos',
        'campo_laboral': 'Empresas de servicios, consultoría ambiental, gobierno, investigación',
        'requisitos': 'Diploma de bachiller, énfasis en matemáticas y ciencias'
    },
    'ingeniería civil': {
        'nombre': 'Ingeniería Civil',
        'duracion': '9 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma ingenieros en diseño, construcción y gestión de infraestructura civil.',
        'perfil': 'Cálculo estructural, modelado, gestión de proyectos, sostenibilidad',
        'campo_laboral': 'Empresas constructoras, consultoría, gobierno, proyectos de infraestructura',
        'requisitos': 'Diploma de bachiller, énfasis en matemáticas y física'
    },
    'ingeniería de sistemas': {
        'nombre': 'Ingeniería de Sistemas',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma ingenieros especializados en desarrollo de software, análisis de sistemas y ciberseguridad.',
        'perfil': 'Programación, análisis sistémico, ciberseguridad, cloud computing',
        'campo_laboral': 'Startups tech, grandes empresas, consultorías IT, desarrollo freelance',
        'requisitos': 'Diploma de bachiller, aptitud para programación'
    },
    'ingeniería financiera': {
        'nombre': 'Ingeniería Financiera',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma ingenieros financieros especializados en mercados, derivados e inversiones.',
        'perfil': 'Análisis financiero, modelado matemático, gestión de riesgo',
        'campo_laboral': 'Bancos, fondos de inversión, bolsa, fintech, consultoría financiera',
        'requisitos': 'Diploma de bachiller, fortaleza en matemáticas'
    },
    'ingeniería industrial': {
        'nombre': 'Ingeniería Industrial',
        'duracion': '9 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma ingenieros en optimización de procesos, gestión de producción y calidad.',
        'perfil': 'Optimización de procesos, gestión de proyectos, análisis de datos',
        'campo_laboral': 'Manufactura, logística, consultoría, gestión operativa, startups',
        'requisitos': 'Diploma de bachiller, énfasis en matemáticas'
    },
    'investigación criminal': {
        'nombre': 'Investigación Criminal',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma profesionales en criminalística, análisis forense y seguridad investigativa.',
        'perfil': 'Análisis de evidencia, investigación, criminalística, pensamiento deductivo',
        'campo_laboral': 'Fiscalía, policía, seguridad corporativa, pericia forense',
        'requisitos': 'Diploma de bachiller, prueba de admisión'
    },
    'mercadeo': {
        'nombre': 'Mercadeo',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma profesionales en estrategia comercial, marketing digital y gestión de marcas.',
        'perfil': 'Estrategia de marketing, análisis del consumidor, digital marketing',
        'campo_laboral': 'Departamentos de marketing, agencias, startups, ecommerce',
        'requisitos': 'Diploma de bachiller, prueba de admisión'
    },
    'negocios internacionales': {
        'nombre': 'Negocios Internacionales',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma profesionales en comercio exterior, relaciones comerciales y gestión global.',
        'perfil': 'Comercio internacional, idiomas, gestión de proyectos globales',
        'campo_laboral': 'Empresas exportadoras, organismos internacionales, consultoría comercial',
        'requisitos': 'Diploma de bachiller, dominio de inglés'
    },
    'psicología': {
        'nombre': 'Psicología',
        'duracion': '8 semestres',
        'modalidad': 'Presencial',
        'descripcion': 'Forma psicólogos especializados en bienestar, comportamiento humano y aplicaciones clínicas.',
        'perfil': 'Empatía, investigación, análisis del comportamiento, comunicación',
        'campo_laboral': 'Clínicas, recursos humanos, educación, investigación, psicología organizacional',
        'requisitos': 'Diploma de bachiller, entrevista personal'
    }
}

RESPUESTAS = {
    'contacto': {
        'corto': "📞 **Teléfono:** +57 (604) 590 45 00 / 590 6999\n📍 **Medellín:** Cra. 87 #30-65, Belén\n📍 **Bogotá:** Calle 57 # 9-52, Chapinero",
        'expandido': "**CONTACTOS UNIVERSIDAD DE MEDELLÍN**\n\n**SEDE MEDELLÍN** 🏢\n- Dirección: Carrera 87 #30-65, Medellín, Belén, Antioquia\n- Teléfono: +57 (604) 590 45 00\n- Teléfono: +57 (604) 590 6999\n- Email: info@udemedellin.edu.co\n- WhatsApp: +57 312 xxxxx\n\n**SEDE BOGOTÁ** 🏢\n- Dirección: Calle 57 # 9-52, Chapinero, Bogotá D.C.\n- Teléfono: +57 (601) 123 4567\n\n**CONTACTO LEGAL**\n- Notificaciones judiciales: corresrec@udemedellin.edu.co\n\n**HORARIO DE ATENCIÓN**\n- Lunes a viernes: 8:00 a.m. a 12:00 m. y 2:00 p.m. a 6:00 p.m.\n- Sábados: 9:00 a.m. a 1:00 p.m. (Sede Medellín)\n\n**NUESTRO CAMPUS** 🌳\n- Sede principal de 5.6 hectáreas\n- Moderna infraestructura con tecnología de punta\n- Biblioteca inteligente\n- Laboratorios especializados\n- Zonas deportivas y recreación"
    },
    'horario': {
        'corto': "⏰ **Lunes a viernes:** 8:00 a.m. a 12:00 m. y 2:00 p.m. a 6:00 p.m.",
        'expandido': "**HORARIO DE ATENCIÓN UNIVERSIDAD**\n\n**HORARIO GENERAL**\n- Lunes a viernes: 8:00 a.m. a 12:00 m. y 2:00 p.m. a 6:00 p.m.\n\n**BIBLIOTECA**\n- Lunes a viernes: 7:00 a.m. a 8:00 p.m.\n- Sábados: 8:00 a.m. a 5:00 p.m.\n\n**PISCINA**\n- Lunes-viernes: 6:00-8:00 a.m. y 6:00-9:00 p.m.\n- Sábados: 8:00 a.m. a 12:00 m.\n- Domingos y festivos: Cerrada\n\n*Para contactar en horarios especiales, usa WhatsApp o email.*"
    },
    'becas': {
        'corto': "💰 Tenemos becas sociales, de honor, excelencia y estímulos para monitorías, deportes y cultura.",
        'expandido': "**BECAS Y ESTÍMULOS ECONÓMICOS**\n\n**BECAS PRINCIPALES**\n\n📊 **Beca Social**\n- Para estudiantes con necesidad económica demostrada\n- Cubre hasta 100% de arancel\n- Requiere análisis socioeconómico\n- Renovación anual según desempeño académico\n\n🏆 **Beca de Honor**\n- Para estudiantes con excelencia académica (ICFES 85% o superior)\n- Cubre hasta 100% de arancel\n- Mantener GPA mínimo de 3.8\n- Válida durante toda la carrera\n\n⭐ **Beca de Excelencia**\n- Para desempeño sobresaliente en pruebas de admisión\n- Cubre hasta 80% de arancel\n- Acceso a oportunidades de investigación\n- Priorizante para pasantías internacionales\n\n📈 **Beca Mejores SABER PRO**\n- Para personas con resultados 85% en SABER PRO\n- Cubre hasta 50% de arancel\n- Dirigida a profesionales en actualización\n\n**ESTÍMULOS Y APOYOS**\n\n💼 **Monitorías Académicas**\n- $800,000 - $1,200,000 mensuales\n- 8-12 horas semanales\n- Refuerza tu formación mientras ganas\n\n🏃 **Estímulo Deportivo**\n- Para atletas con desempeño competitivo\n- Cubre hasta 60% de arancel\n- Acceso a entrenadores especializados\n- Participación en eventos nacionales e internacionales\n\n🎭 **Estímulo Cultural y Artístico**\n- Para artistas y creadores\n- Cubre hasta 40% de arancel\n- Apoyo en presentaciones y producciones\n\n🌍 **Estímulo de Multilingüismo**\n- Bono de $500,000 semestral\n- Requiere certificación en idiomas\n- Para estudiantes con 2+ idiomas certificados\n\n**CÓMO SOLICITAR**\n- Contacta Secretaría Estudiantil en atención al público\n- Horario: Lunes a viernes 8:00 a.m. - 12:00 m. y 2:00-6:00 p.m.\n- Email: becas@udemedellin.edu.co\n- Teléfono: +57 (604) 590 45 00\n\n**DOCUMENTACIÓN REQUERIDA**\n- Cédula de identidad\n- Últimas declaraciones de impuestos (para becas sociales)\n- Certificado de resultados académicos\n- Solicitud formal completada"
    },
    'biblioteca': {
        'corto': "📚 **Biblioteca UdeM:** Lunes a viernes 7:00 a.m. a 8:00 p.m. | Sábados 8:00 a.m. a 5:00 p.m.",
        'expandido': "**BIBLIOTECA INTELIGENTE UNIVERSIDAD DE MEDELLÍN** 📚\n\n**HORARIO**\n- Lunes a viernes: 7:00 a.m. a 8:00 p.m.\n- Sábados: 8:00 a.m. a 5:00 p.m.\n- Domingos: Cerrada\n\n**SERVICIOS MODERNOS**\n- 45,000+ libros en colección física\n- Acceso a 80+ bases de datos digitales\n- Computadoras con última tecnología\n- Salas de estudio grupal e individual\n- Préstamo a domicilio\n- WiFi de alta velocidad\n- Espacios de coworking\n\n**COLECCIONES ESPECIALES**\n- Revistas científicas internacionales\n- Tesis y trabajos de grado\n- Recursos audiovisuales\n- Libros en idiomas extranjeros\n\n**REQUISITOS**\n- Carné de estudiante vigente\n- Máximo 5 libros simultáneamente\n- Plazo de devolución: 14 días"
    },
    'campus': {
        'corto': "🏢 **Campus UdeM:** 5.6 hectáreas con infraestructura moderna, laboratorios, biblioteca inteligente, zonas deportivas y recreación.",
        'expandido': "**CAMPUS UNIVERSIDAD DE MEDELLÍN** 🏢\n\n**EXTENSIÓN Y UBICACIÓN**\n- 5.6 hectáreas en Belén, Medellín\n- Estratégicamente ubicado con fácil acceso\n- Amplio parqueadero para estudiantes\n- Transporte directo desde estaciones Metro\n\n**INFRAESTRUCTURA ACADÉMICA**\n- 12 bloques de aulas modernas\n- Laboratorios especializados:\n  * Informática y programación\n  * Ingeniería y tecnología\n  * Ciencias naturales\n  * Diseño y creatividad\n- Salas de videoconferencia\n- Aulas inteligentes con tecnología 4K\n\n**BIENESTAR Y RECREACIÓN**\n- Gimnasio completamente equipado\n- Cancha de microfútbol\n- Zona de descanso y convivencia\n- Cafetería y comida saludable\n- Zonas verdes y jardines\n- Piscina (próximamente)\n\n**TECNOLOGÍA**\n- WiFi 5G en todo el campus\n- Plataforma educativa virtual\n- Recursos digitales accesibles 24/7"
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

BECAS_DETALLADAS = {
    'beca social': {
        'nombre': 'Beca Social',
        'descripcion': 'Para estudiantes con necesidad económica demostrada',
        'cobertura': 'Hasta 100% de arancel',
        'requisitos': ['Análisis socioeconómico de la familia', 'Ingresos familiares por debajo del límite establecido', 'Documentación de ingresos (declaraciones de impuestos, nóminas)', 'Diligenciamiento de formulario de solicitud'],
        'beneficios': ['Exención total o parcial del arancel', 'Prioridad en acceso a servicios universitarios', 'Apoyo psicosocial', 'Acceso a programas de apoyo académico'],
        'renovacion': 'Anual, según desempeño académico (mínimo GPA 3.0)',
        'duracion': 'Durante toda la carrera',
        'solicitud': 'Contacta Secretaría Estudiantil: becas@udemedellin.edu.co'
    },
    'beca de honor': {
        'nombre': 'Beca de Honor',
        'descripcion': 'Para estudiantes con excelencia académica comprobada',
        'cobertura': 'Hasta 100% de arancel',
        'requisitos': ['Puntaje ICFES 85% o superior', 'Promedio de notas en bachiller 8.5 o superior', 'Prueba de admisión UdeM con resultado sobresaliente', 'Documento de identidad'],
        'beneficios': ['Exención total del arancel', 'Acceso a becas complementarias internacionales', 'Prioridad en investigación y semilleros científicos', 'Acceso a programas de posgrado con descuento', 'Reconocimiento público en ceremonia de grado'],
        'renovacion': 'Anual, mantener GPA mínimo de 3.8',
        'duracion': 'Durante toda la carrera',
        'solicitud': 'Se asigna automáticamente a los mejores puntajes en admisión'
    },
    'beca de excelencia': {
        'nombre': 'Beca de Excelencia',
        'descripcion': 'Para desempeño sobresaliente en pruebas de admisión',
        'cobertura': 'Hasta 80% de arancel',
        'requisitos': ['Resultados excepcionales en prueba de admisión UdeM', 'Documento de identidad', 'Entrevista con comité de admisiones'],
        'beneficios': ['Cobertura de hasta 80% del arancel', 'Acceso a oportunidades de investigación y pasantías', 'Prioridad para programas de intercambio internacional', 'Tutoría académica especializada', 'Membresía en asociaciones estudiantiles premium'],
        'renovacion': 'Semestral, mantener GPA mínimo de 3.5',
        'duracion': 'Durante la carrera, sujeto a desempeño',
        'solicitud': 'Se asigna durante proceso de admisión'
    },
    'monitoria': {
        'nombre': 'Monitoria Académica',
        'descripcion': 'Apoyo económico para estudiantes que desempeñan funciones de monitor',
        'cobertura': '$800,000 - $1,200,000 mensuales',
        'requisitos': ['Estar matriculado en la carrera', 'GPA mínimo de 3.5', 'Haber aprobado la materia en la que será monitor', 'Disponibilidad de 8-12 horas semanales', 'Entrevista con coordinador académico'],
        'beneficios': ['Ingreso mensual de $800,000 a $1,200,000', 'Experiencia en docencia y liderazgo', 'Refuerzo de conocimientos de la materia', 'Credencial de experiencia docente', 'Oportunidad de trabajo flexible con estudios'],
        'renovacion': 'Cada semestre, según disponibilidad y desempeño',
        'duracion': 'Durante toda la carrera',
        'solicitud': 'Dirigirse a coordinación académica del programa'
    },
    'beca deportiva': {
        'nombre': 'Estímulo Deportivo',
        'descripcion': 'Para atletas con desempeño competitivo reconocido',
        'cobertura': 'Hasta 60% de arancel',
        'requisitos': ['Ser atleta con desempeño competitivo comprobado', 'Certificado de participación en eventos departamentales, nacionales o internacionales', 'Carta de respaldo de entrenador o federación deportiva', 'Mantener vigencia competitiva', 'Documento de identidad'],
        'beneficios': ['Cobertura de hasta 60% del arancel', 'Entrenadores especializados disponibles', 'Acceso a instalaciones deportivas 24/7', 'Flexibilidad en horarios de clases para entrenamientos', 'Participación en eventos competitivos nacionales e internacionales', 'Apoyo nutricional y fisioterapia'],
        'renovacion': 'Anual, con comprobación de desempeño competitivo',
        'duracion': 'Mientras se mantenga desempeño deportivo',
        'solicitud': 'Contacta Dirección de Bienestar: bienestar@udemedellin.edu.co'
    },
    'beca cultural': {
        'nombre': 'Estímulo Cultural y Artístico',
        'descripcion': 'Para artistas y creadores con talento comprobado',
        'cobertura': 'Hasta 40% de arancel',
        'requisitos': ['Participación en agrupaciones artísticas reconocidas', 'Portafolio de trabajo artístico', 'Certificado de participación en eventos culturales', 'Audición o presentación ante comité evaluador', 'Documento de identidad'],
        'beneficios': ['Cobertura de hasta 40% del arancel', 'Apoyo en presentaciones y producciones artísticas', 'Acceso a espacios de ensayo y práctica', 'Colaboración con iniciativas culturales de la universidad', 'Flexibilidad horaria para compromisos artísticos', 'Visibilidad en eventos institucionales'],
        'renovacion': 'Semestral, con demostración de participación artística',
        'duracion': 'Mientras mantenga actividad artística',
        'solicitud': 'Contacta Dirección de Bienestar: bienestar@udemedellin.edu.co'
    },
    'beca multilingue': {
        'nombre': 'Estímulo de Multilingüismo',
        'descripcion': 'Para estudiantes con certificaciones en idiomas adicionales',
        'cobertura': '$500,000 semestral',
        'requisitos': ['Certificación en mínimo 2 idiomas (además del español)', 'Certificados reconocidos internacionalmente (TOEFL, IELTS, DELF, etc.)', 'Copia de certificados a Dirección de Idiomas', 'Estar matriculado actualmente'],
        'beneficios': ['Bono de $500,000 cada semestre', 'Reconocimiento público de competencias lingüísticas', 'Prioridad en programas de intercambio internacional', 'Acceso a recursos de aprendizaje de idiomas premium', 'Oportunidades de trabajo como intérprete o traductor'],
        'renovacion': 'Cada semestre, mantener certificaciones vigentes',
        'duracion': 'Mientras mantenga certificaciones activas',
        'solicitud': 'Contacta Dirección de Idiomas: idiomas@udemedellin.edu.co'
    }
}

KEYWORDS_MAP = {
    'contacto': ['contacto', 'teléfono', 'telefono', 'email', 'correo', 'llamar', 'direccion', 'dirección', 'ubicación', 'ubicacion', 'whatsapp', 'sede', 'dirección', 'teléfono de'],
    'horario': ['horario', 'cuando abre', 'cuando cierra', 'a que hora', 'que hora', 'funcionamiento', 'abierto', 'abren', 'cierra', 'atienden'],
    'becas': ['beca', 'becas', 'estímulo', 'estimul', 'ayuda economica', 'economia', 'descuento', 'financier', 'social', 'honor', 'excelencia', 'monitor', 'deportiv', 'cultural', 'monitoría', 'monitoria', 'apoyo economico'],
    'biblioteca': ['biblioteca', 'libreria', 'libro', 'material', 'aula', 'estudio', 'libros', 'préstamo', 'prestamo', 'digital', 'bases de datos'],
    'inscripcion': ['inscrip', 'registr', 'matricul', 'inscribir', 'registro', 'enroll', 'cómo me inscribo', 'como me inscribo', 'proceso de inscripción', 'proceso de inscripcion'],
    'admisiones': ['admision', 'admisión', 'requisito', 'titulo', 'diploma', 'ingreso', 'requisitos', 'qué necesito', 'que necesito'],
    'campus': ['campus', 'instalaciones', 'infraestructura', 'laboratorio', 'laboratorios', 'facilities', 'edificios', 'moderno', 'tecnología', 'tecnologia', 'gym', 'gimnasio', 'piscina'],
}

def obtener_facultad_carrera(carrera_nombre: str) -> Optional[dict]:
    """Encuentra la facultad a la que pertenece una carrera"""
    carrera_norm = normalizar_texto(carrera_nombre.lower())
    for fac_key, facultad in FACULTADES.items():
        for carrera_fac in facultad['carreras']:
            if normalizar_texto(carrera_fac.lower()) == carrera_norm:
                return facultad
    return None

def buscar_carrera(prompt: str) -> Optional[dict]:
    p_normalizado = normalizar_texto(prompt.lower())

    # 🎯 INTELIGENCIA CONTEXTUAL: Detectar si pregunta por ingenierías en general
    ingenieria_keywords = ['ingenieria', 'ingeniería', 'ingenierias', 'ingenierías', 'que ingenierias', 'cuales ingenierias', 'todas las ingenierias']
    if any(kw in p_normalizado for kw in ingenieria_keywords):
        # Mostrar solo si pregunta por ingeniería sin especificar cual
        if not any(ing in p_normalizado for ing in ['sistemas', 'civil', 'industrial', 'ambiental', 'financiera']):
            ingenierias = [
                '🖥️ **Ingeniería de Sistemas** - Software, AI, Cloud, Ciberseguridad',
                '🏗️ **Ingeniería Civil** - Infraestructura, construcción, sostenibilidad',
                '⚙️ **Ingeniería Industrial** - Optimización, procesos, producción',
                '🌍 **Ingeniería Ambiental** - Sostenibilidad, recursos, tecnologías limpias',
                '💰 **Ingeniería Financiera** - Mercados, inversiones, riesgo financiero'
            ]
            ing_list = '\n'.join(ingenierias)
            return {
                'text': f"**INGENIERÍAS DISPONIBLES EN UNIVERSIDAD DE MEDELLÍN** 🏆\n\n{ing_list}\n\n**Información general:**\n✅ Acreditación de Alta Calidad hasta 2027\n📊 Tasa de empleabilidad: 96.5%\n🔬 15+ grupos de investigación activos\n🌐 50+ convenios internacionales\n\n¿Cuál ingeniería te interesa? Pregúntame por el nombre y te doy todos los detalles.",
                'category': 'carrera_grupo',
                'has_more': False
            }

    # Detectar si pregunta por todas las carreras
    if any(kw in p_normalizado for kw in ['todas las carreras', 'que carreras', 'lista de carreras', 'listado de carreras', 'todas carreras']):
        carreras_list = '\n'.join([f"🎓 {carrera['nombre']}" for carrera in CARRERAS.values()])
        return {
            'text': f"**CARRERAS DISPONIBLES EN UNIVERSIDAD DE MEDELLÍN**\n\n{carreras_list}\n\n¿Cuál te interesa? Pregúntame por el nombre y te cuento todo sobre la carrera (duración, perfil, campo laboral, etc.)",
            'category': 'carrera',
            'has_more': False
        }

    # Buscar carrera específica
    for clave, info in CARRERAS.items():
        clave_normalizada = normalizar_texto(clave)
        nombre_normalizado = normalizar_texto(info['nombre'].lower())

        if clave_normalizada in p_normalizado or nombre_normalizado in p_normalizado:
            # 🎯 Buscar la facultad a la que pertenece
            facultad = obtener_facultad_carrera(info['nombre'])
            facultad_info = ""
            if facultad:
                facultad_info = f"\n\n**📚 Facultad:**\n{facultad['nombre']}\n👨‍💼 **Decano:** {facultad['decano']}\n📞 {facultad['contacto']}\n📧 {facultad['email']}"

            return {
                'text': f"**{info['nombre'].upper()}** ✅\n\n📚 **Duración:** {info['duracion']}\n📍 **Modalidad:** {info['modalidad']}\n\n**Descripción:**\n{info['descripcion']}\n\n**Perfil del profesional:**\n{info['perfil']}\n\n**Campo laboral:**\n{info['campo_laboral']}\n\n**Requisitos de admisión:**\n{info['requisitos']}{facultad_info}\n\n¿Quieres información sobre becas, profesores o proceso de inscripción?",
                'category': 'carrera',
                'has_more': False
            }
    return None

def buscar_categoria(prompt: str) -> Optional[dict]:
    p_normalizado = normalizar_texto(prompt.lower())

    # Detectar si pide más información o detalles
    pide_mas_info = any(kw in p_normalizado for kw in ['mas informacion', 'cuentame mas', 'detalles', 'detalle', 'especifico', 'todo sobre', 'informacion completa', 'saber mas', 'ampliacion', 'ampliado'])

    for categoria, keywords in KEYWORDS_MAP.items():
        for kw in keywords:
            kw_normalizado = normalizar_texto(kw)
            if kw_normalizado in p_normalizado:
                if categoria in RESPUESTAS:
                    # Si pide "más información" o pregunta específica, devolver expandido
                    usar_expandido = pide_mas_info or any(normalizar_texto(k) in p_normalizado for k in ['cuentame', 'quiero', 'quiero saber'])
                    texto = RESPUESTAS[categoria]['expandido'] if usar_expandido else RESPUESTAS[categoria]['corto']

                    return {
                        'text': texto,
                        'category': categoria,
                        'has_more': not usar_expandido
                    }
    return None

def buscar_beca(prompt: str) -> Optional[dict]:
    """Busca y devuelve información de una beca específica"""
    p_normalizado = normalizar_texto(prompt.lower())

    # Buscar beca específica
    for clave, info in BECAS_DETALLADAS.items():
        clave_normalizada = normalizar_texto(clave)
        nombre_normalizado = normalizar_texto(info['nombre'].lower())

        if clave_normalizada in p_normalizado or nombre_normalizado in p_normalizado:
            # Construir respuesta detallada de la beca
            requisitos_texto = '\n'.join([f"  • {req}" for req in info['requisitos']])
            beneficios_texto = '\n'.join([f"  • {ben}" for ben in info['beneficios']])

            texto = f"""**{info['nombre'].upper()}** 🎓

**Descripción:**
{info['descripcion']}

**Cobertura:**
{info['cobertura']}

**Requisitos:**
{requisitos_texto}

**Beneficios:**
{beneficios_texto}

**Renovación:**
{info['renovacion']}

**Duración:**
{info['duracion']}

**Cómo solicitar:**
{info['solicitud']}

¿Tienes otras preguntas sobre becas u otros temas?"""

            return {
                'text': texto,
                'category': 'beca_especifica',
                'has_more': False
            }
    return None

def buscar_profesores(prompt: str) -> Optional[dict]:
    """🎯 Devuelve información sobre profesores cuando se pregunta específicamente"""
    p_normalizado = normalizar_texto(prompt.lower())

    prof_keywords = ['profesor', 'profesores', 'docentes', 'docente', 'maestro', 'maestros', 'catedratico', 'catedrático']

    if not any(kw in p_normalizado for kw in prof_keywords):
        return None

    # Información general sobre profesores
    texto = """**PROFESORES UNIVERSIDAD DE MEDELLÍN** 👨‍🏫👩‍🏫

**CIFRAS GENERALES**
✅ 320+ docentes permanentes
✅ Experiencia profesional 10+ años promedio
✅ Participación en investigación de clase mundial
✅ Actualización continua en sus campos

**CUALIDADES DE NUESTROS DOCENTES**
• Docentes con experiencia profesional de 10+ años
• Participación activa en investigación de clase mundial
• Actualización continua en sus campos
• Comprometidos con la excelencia educativa
• Mentores de proyectos innovadores

**PROGRAMAS DE APOYO DOCENTE**
📚 **Desarrollo continuo** - Programa de capacitación permanente
🔬 **Investigación** - Incentivos para publicaciones y proyectos
🌐 **Intercambio internacional** - Movilidad académica internacional
💡 **Innovación pedagógica** - Apoyo para metodologías innovadoras

**POR CARRERA**
- **Ingeniería de Sistemas:** 35+ docentes (18 doctores, 22 maestros)
- **Derecho:** 28+ docentes (12 doctores, 16 maestros)
- **Administración:** 32+ docentes (15 doctores, 17 maestros)

¿Pregunta por una carrera específica para más detalles sobre sus profesores?"""

    return {
        'text': texto,
        'category': 'profesores',
        'has_more': False
    }

def buscar_decanos(prompt: str) -> Optional[dict]:
    """🎯 Devuelve información sobre decanos cuando se pregunta específicamente"""
    p_normalizado = normalizar_texto(prompt.lower())

    decano_keywords = ['decano', 'decanos', 'liderazgo', 'director', 'directores', 'facultad']

    if not any(kw in p_normalizado for kw in decano_keywords):
        return None

    # Mostrar decanos por facultad
    decanos_info = """**LIDERAZGO ACADÉMICO - DECANOS POR FACULTAD** 🏛️

**Facultad de Ingenierías**
👨‍💼 **Dr. Jorge Alberto Ruiz López**
📞 +57 (604) 590 4500 ext. 8901
📧 ingenieria@udemedellin.edu.co

**Facultad de Ciencias Económicas y Administrativas**
👩‍💼 **Dra. María Elena Vásquez González**
📞 +57 (604) 590 4500 ext. 8902
📧 ceconomicas@udemedellin.edu.co

**Facultad de Derecho**
👨‍💼 **Dr. Carlos Andrés Mendoza Pérez**
📞 +57 (604) 590 4500 ext. 8903
📧 derecho@udemedellin.edu.co

**Facultad de Comunicación**
👩‍💼 **Dra. Catalina López Rodríguez**
📞 +57 (604) 590 4500 ext. 8904
📧 comunicacion@udemedellin.edu.co

**Facultad de Diseño**
👨‍💼 **Mg. Fernando García Mejía**
📞 +57 (604) 590 4500 ext. 8905
📧 diseno@udemedellin.edu.co

**Facultad de Ciencias Sociales y Humanas**
👨‍💼 **Dr. Andrés Felipe Moreno Salazar**
📞 +57 (604) 590 4500 ext. 8906
📧 csociales@udemedellin.edu.co

¿Necesitas contactar a algún decano en particular?"""

    return {
        'text': decanos_info,
        'category': 'decanos',
        'has_more': False
    }

def buscar_calidad(prompt: str) -> Optional[dict]:
    """🎯 Devuelve información sobre acreditación y calidad cuando se pregunta"""
    p_normalizado = normalizar_texto(prompt.lower())

    calidad_keywords = ['calidad', 'acreditacion', 'acreditación', 'certificacion', 'certificación', 'excelencia', 'acreditada', 'reconocimiento']

    if not any(kw in p_normalizado for kw in calidad_keywords):
        return None

    texto = """**ACREDITACIÓN Y CALIDAD ACADÉMICA** ✨

**ACREDITACIÓN INSTITUCIONAL**
🏆 **Estado:** Vigente
📅 **Válido hasta:** 2028
🔐 **Otorgado por:** Ministerio de Educación Nacional
✅ **Garantiza:** Excelencia académica y administrativa en todos los programas

**CERTIFICACIONES ADICIONALES**
• ISO 9001:2015 en Gestión de Calidad
• ACBSP - The Accreditation Council for Business Schools and Programs
• Certificación en Competencias Digitales para Docentes
• Sello de Equidad de Género

**INDICADORES DE CALIDAD**
📊 **Tasa de egreso:** 89.5%
⭐ **Satisfacción estudiantes:** 4.6/5.0
💼 **Empleabilidad promedio:** 94.1%
👨‍🔬 **Investigadores activos:** 156
🔬 **Grupos de investigación:** 85+
📚 **Proyectos vigentes:** 250+

**INVESTIGACIÓN Y DESARROLLO**
• 85+ grupos de investigación activos
• 250+ proyectos de investigación vigentes
• Publicaciones en revistas indexadas internacionalmente
• Colaboración con universidades de clase mundial
• Semilleros de investigación para estudiantes

¿Quieres saber más sobre algún programa específico o sus acreditaciones?"""

    return {
        'text': texto,
        'category': 'calidad',
        'has_more': False
    }

def info_handler(prompt: str) -> Optional[str]:
    # 🎯 NUEVA LÓGICA INTELIGENTE - ORDEN POR ESPECIFICIDAD

    # Prioridad 1: Búsquedas específicas (Profesores, Decanos, Calidad)
    # Estas preguntas son MÁS específicas así que van primero
    prof_resp = buscar_profesores(prompt)
    if prof_resp:
        return json.dumps(prof_resp, ensure_ascii=False)

    decano_resp = buscar_decanos(prompt)
    if decano_resp:
        return json.dumps(decano_resp, ensure_ascii=False)

    calidad_resp = buscar_calidad(prompt)
    if calidad_resp:
        return json.dumps(calidad_resp, ensure_ascii=False)

    # Prioridad 2: Búsqueda de beca específica
    beca_resp = buscar_beca(prompt)
    if beca_resp:
        return json.dumps(beca_resp, ensure_ascii=False)

    # Prioridad 3: Búsqueda de carrera (incluyendo ingenierías como grupo)
    carrera_resp = buscar_carrera(prompt)
    if carrera_resp:
        return json.dumps(carrera_resp, ensure_ascii=False)

    # Prioridad 4: Búsqueda por categoría (Contacto, Horarios, Campus, etc.)
    categoria_resp = buscar_categoria(prompt)
    if categoria_resp:
        return json.dumps(categoria_resp, ensure_ascii=False)

    # Prioridad 5: Pregunta genérica o no reconocida
    if any(w in prompt.lower() for w in ('universidad', 'información', 'informacion', 'institución', 'institucion', 'help', 'ayuda')):
        response = {
            'text': "Soy el asistente virtual de **Universidad de Medellín**. Puedo ayudarte con:\n📚 **Carreras** | 💰 **Becas** | 📞 **Contactos** | ⏰ **Horarios** | 👨‍🏫 **Profesores** | 🏛️ **Decanos** | ✨ **Calidad**\n\n¿Qué necesitas saber?",
            'category': 'general',
            'has_more': False
        }
        return json.dumps(response, ensure_ascii=False)

    return None

def register(bot) -> None:
    bot.register_handler(info_handler)
