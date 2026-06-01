CARRERAS_DETALLADAS = {
    'civil': '''**INGENIERÍA CIVIL** - Construye el futuro

Forma profesionales capacitados para diseñar, construir y mantener infraestructuras.

PERFIL DEL EGRESADO:
Profesional con capacidad de diseñar estructuras resistentes y sostenibles, gestionar proyectos de construcción, realizar análisis de impacto ambiental.

CAMPOS LABORALES:
• Empresas constructoras y desarrolladoras inmobiliarias
• Proyectos de infraestructura vial y de transporte
• Obras hidráulicas y sanitarias
• Entidades gubernamentales (Vías, Acueducto, CAR)
• Consultoría técnica y supervisión de obras

DIFERENCIALES UDEMEDELLIN:
• Laboratorio de Mecánica de Suelos con equipos de última generación
• Laboratorio de Hormigón con pruebas de resistencia
• Convenios estratégicos con empresas constructoras líderes
• Prácticas en obras reales durante la carrera
• 96% de empleabilidad
• Salario inicial: $2,500,000 - $3,500,000''',

    'sistemas': '''**INGENIERÍA DE SISTEMAS** - Transforma con tecnología

Crea soluciones digitales que revolucionan industrias y mejoran vidas.

PERFIL DEL EGRESADO:
Ingeniero especializado en desarrollo de software, análisis de datos, transformación digital, gestión de infraestructura tecnológica.

CAMPOS LABORALES:
• Desarrollo de aplicaciones móviles y web
• Software empresarial y gestión de datos
• Big Data y Ciencia de Datos
• Cloud Computing (AWS, Azure, Google Cloud)
• Ciberseguridad e infraestructura TI
• Startup tecnológicas y fintech
• Consultoría tecnológica

DIFERENCIALES UDEMEDELLIN:
• Laboratorios con tecnología de punta
• Certificaciones Cloud: AWS Solutions Architect, Azure Developer
• Convenios con empresas tecnológicas Top 10 (Google, Microsoft, AWS)
• Prácticas pagadas en startups y empresas tech
• 98% de empleabilidad
• Salario inicial: $3,000,000 - $4,500,000''',

    'derecho': '''**DERECHO** - Defiende la justicia

Programa estrella de la UdeMedellin con mayor aprobación en examen de Estado.

PERFIL DEL EGRESADO:
Abogado profesional e íntegro, capaz de defender derechos, asesorar en cualquier rama legal.

CAMPOS LABORALES:
• Ejercicio profesional independiente
• Despachos de abogados Top 10
• Asesoría legal corporativa y M&A
• Entidades gubernamentales y públicas
• Justicia ordinaria y especializada
• Derecho internacional

DIFERENCIALES UDEMEDELLIN:
• 96% DE APROBACIÓN EN EXAMEN DE ESTADO (mejor del país)
• Convenios con firmas de abogados Top 10 Colombia
• Clínica jurídica con casos reales desde 3er semestre
• Especializaciones en: Laboral, Comercial, Penal, Familia, Administrativo
• Salario inicial: $3,500,000 - $6,000,000''',

    'administracion': '''**ADMINISTRACIÓN** - Gestiona empresas exitosas

Lidera organizaciones hacia el éxito empresarial con visión estratégica.

PERFIL DEL EGRESADO:
Administrador con visión estratégica y capacidad de liderazgo para gestionar organizaciones.

CAMPOS LABORALES:
• Gerencia general en empresas privadas multinacionales
• Consultoría empresarial y estratégica
• Startups y emprendimiento
• Gestión de recursos humanos
• Finanzas e inversión

DIFERENCIALES UDEMEDELLIN:
• Diplomado en Emprendimiento e Innovación
• Certificación en Project Management (PMP)
• Casos de empresas reales y estudios de caso
• Convenios con empresas multinacionales (Samsung, Intel, Nestlé)
• 91% de empleabilidad
• Salario inicial: $2,500,000 - $3,800,000''',

    'becas': '''**BECAS Y FINANCIACIÓN - 5 Opciones Disponibles**

1. **Beca de Mérito Académico** - Hasta 100%
   Recompensa a estudiantes con desempeño académico sobresaliente
   Requisito: Puntaje ICFES superior a 90 percentil

2. **Beca Socioeconómica** - Hasta 80%
   Ofrece oportunidades educativas a estudiantes de recursos limitados
   Requisito: Ingresos familiares según análisis socioeconómico

3. **Beca Deportiva** - Hasta 75%
   Apoya a atletas de alto rendimiento
   Requisito: Ser atleta de nivel nacional o internacional

4. **Becas por Convenio** - Variable (30%-100%)
   Acuerdos especiales con empresas
   Requisito: Ser empleado o vinculado a organización convenida

5. **Beca por Desempeño** - Hasta 50%
   Reconoce excelente rendimiento durante tus estudios
   Requisito: Promedio semestral 4.2 o superior

Contacto Becas: becas@udemedellin.edu.co
Teléfono: +57 (604) 590-4500 ext. 1234'''
}

def obtener_respuesta_detallada(mensaje):
    """Obtener respuesta profesional y detallada de Vivi"""
    mensaje_lower = mensaje.lower()
    
    # Búsqueda en carreras
    if 'civil' in mensaje_lower:
        return CARRERAS_DETALLADAS['civil']
    elif 'sistemas' in mensaje_lower or 'software' in mensaje_lower:
        return CARRERAS_DETALLADAS['sistemas']
    elif 'derecho' in mensaje_lower:
        return CARRERAS_DETALLADAS['derecho']
    elif 'administr' in mensaje_lower:
        return CARRERAS_DETALLADAS['administracion']
    elif 'beca' in mensaje_lower or 'financiación' in mensaje_lower:
        return CARRERAS_DETALLADAS['becas']
    
    return None
