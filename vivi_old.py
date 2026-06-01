#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import json
import os
import difflib

# INFORMACIÓN COMPLETA DE TODAS LAS CARRERAS
CARRERAS = {
    'civil': {
        'nombre': 'Ingeniería Civil',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'alias': ['civil', 'infraestructura', 'construcción'],
        'descripcion': '''**INGENIERÍA CIVIL** - Construye el futuro

Forma profesionales capacitados para diseñar, construir y mantener infraestructuras.

📊 **PERFIL DEL EGRESADO:**
Profesional con capacidad de diseñar estructuras resistentes y sostenibles, gestionar proyectos de construcción, realizar análisis de impacto ambiental y participar en obras públicas y privadas.

💼 **CAMPOS LABORALES:**
✓ Empresas constructoras y desarrolladoras inmobiliarias
✓ Proyectos de infraestructura vial y de transporte
✓ Obras hidráulicas y sanitarias
✓ Entidades gubernamentales (Vías, Acueducto, CAR)
✓ Consultoría técnica y supervisión de obras
✓ Proyectos de energía y telecomunicaciones
✓ Independencia profesional

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Laboratorio de Mecánica de Suelos con equipos de última generación
• Laboratorio de Hormigón con pruebas de resistencia
• Convenios estratégicos con empresas constructoras líderes
• Prácticas en obras reales durante la carrera
• Certificación en BIM (Building Information Modeling)
• 96% de empleabilidad
• Salario inicial: $2,500,000 - $3,500,000
• Docentes con experiencia internacional

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Estructuras y análisis estructural
- Geotecnia e ingeniería de cimentaciones
- Vías y transporte
- Proyectos de agua y saneamiento
- Construcción sostenible

¿Necesitas más información o deseas conocer otra carrera?'''
    },
    'sistemas': {
        'nombre': 'Ingeniería de Sistemas',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'alias': ['sistemas', 'software', 'tecnología', 'programación', 'desarrollo'],
        'descripcion': '''**INGENIERÍA DE SISTEMAS** - Transforma con tecnología

Crea soluciones digitales que revolucionan industrias y mejoran vidas.

📊 **PERFIL DEL EGRESADO:**
Ingeniero especializado en desarrollo de software, análisis de datos, transformación digital, gestión de infraestructura tecnológica y soluciones empresariales inteligentes.

💼 **CAMPOS LABORALES:**
✓ Desarrollo de aplicaciones móviles y web
✓ Software empresarial y gestión de datos
✓ Big Data y Ciencia de Datos
✓ Cloud Computing (AWS, Azure, Google Cloud)
✓ Ciberseguridad e infraestructura TI
✓ Startup tecnológicas y fintech
✓ Consultoría tecnológica
✓ Machine Learning e Inteligencia Artificial

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Laboratorios con tecnología de punta
• Certificaciones Cloud: AWS Solutions Architect, Azure Developer
• Lenguajes: Python, Java, JavaScript, C++, Go, Rust
• Convenios con empresas tecnológicas Top 10 (Google, Microsoft, AWS)
• Prácticas pagadas en startups y empresas tech
• 98% de empleabilidad
• Salario inicial: $3,000,000 - $4,500,000
• Docentes de Google, Meta, Microsoft

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Desarrollo Full-Stack Web
- Mobile Development (iOS/Android)
- Cloud Architecture
- Data Science & Analytics
- Ciberseguridad

¿Deseas conocer otra ingeniería?'''
    },
    'industrial': {
        'nombre': 'Ingeniería Industrial',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'alias': ['industrial', 'procesos', 'optimización'],
        'descripcion': '''**INGENIERÍA INDUSTRIAL** - Optimiza resultados

Mejora procesos para generar mayor valor en organizaciones de cualquier sector.

📊 **PERFIL DEL EGRESADO:**
Profesional que optimiza recursos, procesos y sistemas en empresas, con visión estratégica y capacidad de liderazgo para mejorar eficiencia y competitividad.

💼 **CAMPOS LABORALES:**
✓ Consultoría empresarial y de procesos
✓ Manufactura y producción
✓ Logística y cadena de suministro global
✓ Banca, seguros y finanzas
✓ Retail y comercio electrónico
✓ Gestión de proyectos internacionales
✓ Emprendimiento e innovación

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Certificación Lean Six Sigma
• Metodologías Kaizen y SMED
• Simulación de procesos avanzada (Arena, Simul8)
• Análisis de datos con Python y Power BI
• Pasantías en empresas Fortune 500
• Convenios con empresas multinacionales
• 94% de empleabilidad
• Salario inicial: $2,800,000 - $4,000,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Optimización de Procesos
- Logística y Supply Chain
- Gestión de Calidad
- Análisis de Datos Empresarial
- Innovación y Emprendimiento

¿Interesado en otra carrera?'''
    },
    'mecanica': {
        'nombre': 'Ingeniería Mecánica',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'alias': ['mecánica', 'máquinas', 'manufactura'],
        'descripcion': '''**INGENIERÍA MECÁNICA** - Diseña máquinas del futuro

Crea máquinas y sistemas que impulsan la industria global.

📊 **PERFIL DEL EGRESADO:**
Ingeniero especializado en diseño, fabricación y automatización de máquinas y sistemas mecánicos con visión en sostenibilidad e innovación.

💼 **CAMPOS LABORALES:**
✓ Diseño e ingeniería asistida por computador (CAD)
✓ Industria automotriz y autopartes
✓ Energía renovable (solar, eólica, hidroeléctrica)
✓ Minería y extracción
✓ Robótica e automatización industrial
✓ Investigación y desarrollo (I+D)
✓ Consultoría técnica

🎓 **DIFERENCIALES UDEMEDELLIN:**
• CAD/CAM de última generación (Solidworks, NX, Fusion 360)
• Laboratorio de Máquinas Herramientas CNC
• Pruebas en Máquina Universal de 300 toneladas
• Análisis de elementos finitos (FEA)
• Convenios con plantas manufactureras líderes
• 95% de empleabilidad
• Salario inicial: $2,700,000 - $3,800,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Diseño Asistido por Computador
- Manufactura Avanzada
- Energías Renovables
- Automatización Industrial
- Robótica

¿Deseas conocer más programas?'''
    },
    'electronica': {
        'nombre': 'Ingeniería Electrónica',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'alias': ['electrónica', 'circuitos', 'iot', 'embebido'],
        'descripcion': '''**INGENIERÍA ELECTRÓNICA** - Conecta el mundo

Diseña sistemas inteligentes que conectan dispositivos e industrias.

📊 **PERFIL DEL EGRESADO:**
Ingeniero especializado en circuitos, sistemas embebidos, IoT y soluciones electrónicas inteligentes para automatización y comunicación.

💼 **CAMPOS LABORALES:**
✓ Telecomunicaciones y redes
✓ Electrónica de consumo
✓ Automatización industrial
✓ IoT y Smart Cities
✓ Dispositivos médicos
✓ Energía inteligente y microgrids
✓ Investigación y desarrollo

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Laboratorios de electrónica digital y analógica
• Simuladores: SPICE, Proteus, Multisim, Altium
• Microcontroladores: Arduino, PIC, STM32, ARM Cortex
• Desarrollos en FPGA y lógica programable
• Proyectos con aplicaciones reales en IoT
• Convenios con empresas de telecomunicaciones
• 97% de empleabilidad
• Salario inicial: $2,900,000 - $4,200,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Electrónica Digital y Analógica
- Sistemas Embebidos
- IoT y Comunicaciones
- Procesamiento de Señales
- Energía Inteligente

¿Quieres saber de otra ingeniería?'''
    },
    'ambiental': {
        'nombre': 'Ingeniería Ambiental',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'alias': ['ambiental', 'sostenibilidad', 'ambiente', 'ecología'],
        'descripcion': '''**INGENIERÍA AMBIENTAL** - Cuida el planeta

Protege la naturaleza mientras generas desarrollo sostenible.

📊 **PERFIL DEL EGRESADO:**
Profesional comprometido con sostenibilidad, gestión ambiental y protección de recursos naturales con soluciones innovadoras.

💼 **CAMPOS LABORALES:**
✓ Consultorías y auditorías ambientales
✓ Tratamiento de agua y residuos
✓ Energías renovables y eficiencia energética
✓ Minería y extracción sostenible
✓ Entidades ambientales (ANLA, Corporaciones)
✓ Industria manufacturera
✓ Monitoreo ambiental y cambio climático

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Laboratorio de Calidad de Agua y Aire
• Equipos de análisis ambiental especializados
• Proyectos de sustentabilidad con comunidades reales
• Normativa ambiental: Colombiana, Latinoamericana, Internacional
• Convenios con organismos ambientales (ANLA, Corpocol)
• Certificaciones en ISO 14001 y gestión ambiental
• 93% de empleabilidad
• Salario inicial: $2,600,000 - $3,600,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Tratamiento de Agua y Residuos
- Energías Renovables
- Cambio Climático
- Gestión de Recursos Naturales
- Contaminación y Calidad del Aire

¿Te interesa otra carrera?'''
    },
    'derecho': {
        'nombre': 'Derecho',
        'facultad': 'FACULTAD DE DERECHO',
        'duracion': '10 semestres',
        'costo': '$11,000,000 - $13,500,000/año',
        'alias': ['derecho', 'abogado', 'ley', 'justicia'],
        'descripcion': '''**DERECHO** - Defiende la justicia

Programa estrella de la UdeMedellin con mayor aprobación en examen de Estado.

📊 **PERFIL DEL EGRESADO:**
Abogado profesional e íntegro, capaz de defender derechos, asesorar en cualquier rama legal y contribuir al Estado de Derecho.

💼 **CAMPOS LABORALES:**
✓ Ejercicio profesional independiente
✓ Despachos de abogados Top 10
✓ Asesoría legal corporativa y M&A
✓ Entidades gubernamentales y públicas
✓ Justicia ordinaria y especializada
✓ Derecho internacional
✓ Docencia e investigación

🎓 **DIFERENCIALES UDEMEDELLIN:**
• **96% DE APROBACIÓN EN EXAMEN DE ESTADO** (mejor del país)
• Convenios con firmas de abogados Top 10 Colombia
• Simuladores de juicio y cortes con audiencias reales
• Clínica jurídica con casos reales desde 3er semestre
• Especializaciones en: Laboral, Comercial, Penal, Familia, Administrativo
• Docentes con experiencia en Corte Suprema y Constitucional
• Salario inicial: $3,500,000 - $6,000,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Derecho Comercial y Corporativo
- Derecho Laboral
- Derecho Penal
- Derecho Administrativo
- Derecho Internacional

¿Deseas conocer otro programa?'''
    },
    'administracion': {
        'nombre': 'Administración',
        'facultad': 'FACULTAD DE CIENCIAS ECONÓMICAS',
        'duracion': '8 semestres',
        'costo': '$10,000,000 - $12,000,000/año',
        'alias': ['administración', 'administracion', 'empresa', 'gerencia', 'management'],
        'descripcion': '''**ADMINISTRACIÓN** - Gestiona empresas exitosas

Lidera organizaciones hacia el éxito empresarial con visión estratégica.

📊 **PERFIL DEL EGRESADO:**
Administrador con visión estratégica, capacidad de liderazgo y herramientas para gestionar organizaciones en entornos complejos y globales.

💼 **CAMPOS LABORALES:**
✓ Gerencia general en empresas privadas multinacionales
✓ Consultoría empresarial y estratégica
✓ Startups y emprendimiento
✓ Sector público y ONG
✓ Gestión de recursos humanos
✓ Finanzas e inversión
✓ Logística y supply chain global

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Diplomado en Emprendimiento e Innovación
• Certificación en Project Management (PMP)
• Casos de empresas reales y estudios de caso
• Convenios con empresas multinacionales (Samsung, Intel, Nestlé)
• Intercambios internacionales en universidades prestigiosas
• Laboratorio de Emprendimiento con capital semilla
• 91% de empleabilidad
• Salario inicial: $2,500,000 - $3,800,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Gestión Estratégica
- Recursos Humanos
- Finanzas Corporativas
- Emprendimiento
- Dirección de Marketing

¿Quieres saber de otra carrera?'''
    },
    'contabilidad': {
        'nombre': 'Contabilidad',
        'facultad': 'FACULTAD DE CIENCIAS ECONÓMICAS',
        'duracion': '8 semestres',
        'costo': '$10,000,000 - $12,000,000/año',
        'alias': ['contabilidad', 'contador', 'finanzas', 'contable'],
        'descripcion': '''**CONTABILIDAD** - Controla las finanzas

Sé el experto financiero en cualquier organización, domina auditoría e impuestos.

📊 **PERFIL DEL EGRESADO:**
Contador público profesional, especializado en gestión financiera, auditoría y asesoría tributaria con ética y responsabilidad.

💼 **CAMPOS LABORALES:**
✓ Firmas de auditoría (Deloitte, EY, KPMG, PWC - Big 4)
✓ Asesoría tributaria y contable
✓ Departamentos de contabilidad corporativa
✓ Consultoría empresarial
✓ Entidades financieras y bancarias
✓ Independencia profesional
✓ Peritaje contable forense

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Certificación IFRS y NIIF (Normas Internacionales)
• Auditoría interna y externa con metodologías internacionales
• Tributación actualizada: nacional e internacional
• Prácticas pagadas en Big 4 y Top 10 contables
• Software profesional: SAP, Oracle, Microsoft Dynamics
• Convenios con Junta Central de Contadores
• 92% de empleabilidad
• Salario inicial: $2,300,000 - $3,500,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Auditoría y Control
- Tributación
- Contabilidad Financiera
- Gestión Contable
- Auditoría Forense

¿Te interesa otra carrera?'''
    },
    'comunicacion': {
        'nombre': 'Comunicación Social',
        'facultad': 'FACULTAD DE COMUNICACIÓN',
        'duracion': '8 semestres',
        'costo': '$9,500,000 - $11,500,000/año',
        'alias': ['comunicación', 'comunicacion', 'comunicador', 'medios'],
        'descripcion': '''**COMUNICACIÓN SOCIAL** - Crea mensajes que impactan

Conecta marcas con audiencias a través de estrategias innovadoras y contenido impactante.

📊 **PERFIL DEL EGRESADO:**
Comunicador especializado en medios, marketing y comunicación corporativa, con capacidad de crear contenido y gestionar audiencias.

💼 **CAMPOS LABORALES:**
✓ Agencias de publicidad y marketing
✓ Departamentos de comunicación corporativa
✓ Medios de comunicación (TV, radio, digital)
✓ Community management y redes sociales
✓ Producción audiovisual y transmedia
✓ Relaciones públicas
✓ Comunicación política y social

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Estudios de TV, radio y podcast profesionales
• Edición de video y fotografía profesional (Adobe, DaVinci)
• Estrategia digital y social media avanzada
• Convenios con agencias creativas líderes (Havas, McCann, Publicis)
• Prácticas en medios de comunicación (Caracol, RCN, CM&)
• Equipamiento multimedia de última generación
• 89% de empleabilidad
• Salario inicial: $2,000,000 - $3,200,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Comunicación Digital y Social Media
- Producción Audiovisual
- Periodismo Digital
- Comunicación Corporativa
- Marketing Digital

¿Deseas conocer más opciones?'''
    },
    'publicidad': {
        'nombre': 'Publicidad',
        'facultad': 'FACULTAD DE COMUNICACIÓN',
        'duracion': '8 semestres',
        'costo': '$9,500,000 - $11,500,000/año',
        'alias': ['publicidad', 'publicista', 'marketing', 'advertising'],
        'descripcion': '''**PUBLICIDAD** - Vende con creatividad

Crea campañas publicitarias que conquistan mercados y generan impacto.

📊 **PERFIL DEL EGRESADO:**
Publicista creativo con visión estratégica, capacidad de innovación y herramientas para crear campañas 360 en múltiples plataformas.

💼 **CAMPOS LABORALES:**
✓ Agencias de publicidad creativas de primer nivel
✓ Departamentos de marketing y brand management
✓ Mercadotecnia digital y e-commerce
✓ Branding y diseño corporativo
✓ Medios y planificación publicitaria
✓ Consultoría creativa
✓ Emprendimiento en marketing

🎓 **DIFERENCIALES UDEMEDELLIN:**
• Dirección de arte y diseño gráfico avanzado
• Producción audiovisual y cinematografía profesional
• Marketing digital, SEM, SEO y Growth Hacking
• Proyectos reales con marcas líderes (Colciencias, Bayer, Unilever)
• Convenios con agencias Top 10 (Leo Burnett, TBWA, Y&R)
• Portfolio competitivo a nivel nacional e internacional
• 88% de empleabilidad
• Salario inicial: $2,100,000 - $3,400,000

📚 **ÁREAS DE ESPECIALIZACIÓN:**
- Dirección de Arte y Creatividad
- Marketing Digital
- Producción Audiovisual
- Branding
- Publicidad Interactiva

¿Quieres saber de otra carrera?'''
    },
}

# INFORMACIÓN DETALLADA DE BECAS
BECAS = {
    'merito': {
        'nombre': 'Beca de Mérito Académico',
        'alias': ['merito', 'mérito', 'académico', 'icfes'],
        'cobertura': 'Hasta 100%',
        'descripcion': '''**BECA DE MÉRITO ACADÉMICO** - Reconoce tu excelencia

Recompensa a estudiantes con desempeño académico sobresaliente.

📊 **COBERTURA:**
Hasta 100% de la matrícula anual
(Desde $5M hasta cobertura total según méritos)

**REQUISITOS:**
✓ Puntaje ICFES superior a 90 percentil
✓ Promedio académico bachillerato: 9.0 o superior
✓ Prueba de admisión UdeMedellin con resultado sobresaliente
✓ Análisis curricular con logros académicos documentados

**BENEFICIARIOS:**
✓ Aspirantes de pregrado (cualquier programa)
✓ Estudiantes con expediente de excelencia
✓ Participantes de olimpiadas científicas
✓ Ganadores de concursos académicos

**PROCESO DE SOLICITUD:**
1. Completar formulario en admisiones@udemedellin.edu.co
2. Enviar: ICFES, promedio bachillerato, logros académicos
3. Evaluación por comisión de becas (2 semanas)
4. Entrevista con rector o decano (si aplica)
5. Notificación de resultado

**CONTACTO:**
📧 becas@udemedellin.edu.co
📞 +57 (604) 590-4500 ext. 1234

¿Necesitas información sobre otra beca?'''
    },
    'socioeconomica': {
        'nombre': 'Beca Socioeconómica',
        'alias': ['socioeconómica', 'socioeconómica', 'socioeconomica', 'ingresos'],
        'cobertura': 'Hasta 80%',
        'descripcion': '''**BECA SOCIOECONÓMICA** - Igualdad de oportunidades

Ofrece oportunidades educativas a estudiantes de recursos limitados.

📊 **COBERTURA:**
Hasta 80% de la matrícula anual
(Según nivel de ingresos familiares)

**REQUISITOS:**
✓ Ingresos familiares mensuales: $1,500,000 - $4,000,000
✓ SISBEN o documento de vulnerabilidad
✓ Desempeño académico mínimo: 8.0 promedio
✓ Certificación de domicilio y composición familiar

**BENEFICIARIOS:**
✓ Estudiantes de estratos 1, 2, 3 y parte de estrato 4
✓ Hijos de desplazados o víctimas de violencia
✓ Estudiantes en situación de vulnerabilidad documentada
✓ Cabeza de familia con menores a cargo

**APOYO ADICIONAL:**
✓ Bonificación en comedor universitario (30% descuento)
✓ Acceso a biblioteca digital sin costo
✓ Orientación financiera personal
✓ Posibilidad de apoyo laboral en campus

**PROCESO DE SOLICITUD:**
1. Contactar Oficina de Becas
2. Traer documentación: SISBEN, cedula, comprobante ingresos
3. Estudio socioeconómico (visita a domicilio opcional)
4. Evaluación y aprobación (4 semanas)
5. Desembolso automático cada semestre

**CONTACTO:**
📧 becas@udemedellin.edu.co
📞 +57 (604) 590-4500 ext. 1234

¿Deseas saber de otra beca?'''
    },
    'deportiva': {
        'nombre': 'Beca Deportiva',
        'alias': ['deportiva', 'deporte', 'atleta', 'deportivo'],
        'cobertura': 'Hasta 75%',
        'descripcion': '''**BECA DEPORTIVA** - Talento atlético

Apoya a atletas de alto rendimiento en su formación profesional.

📊 **COBERTURA:**
Hasta 75% de la matrícula anual
(Según categoría atlética)

**REQUISITOS:**
✓ Ser atleta de alto rendimiento (nivel nacional o internacional)
✓ Certifación de participación en torneos oficiales
✓ Desempeño académico mínimo: 8.0
✓ Aval de federación o asociación deportiva

**DEPORTES ELEGIBLES:**
✓ Fútbol, Baloncesto, Voleibol
✓ Atletismo, Natación
✓ Tenis, Bádminton, Squash
✓ Ciclismo, Judo, Lucha libre
✓ Otros deportes olímpicos reconocidos

**CATEGORÍAS:**
✓ Élite: Atletas de selección nacional (100% apoyo deportivo)
✓ Alto Rendimiento: Campeones departamentales (75% matrícula)
✓ Talento: Promisas deportivas (50% matrícula)

**BENEFICIOS ADICIONALES:**
✓ Acceso a centros de entrenamiento universitarios
✓ Coaching y preparación física profesional
✓ Flexibilidad en horarios académicos para competencias
✓ Apoyo nutricional especializado
✓ Seguro de lesiones deportivas

**PROCESO DE SOLICITUD:**
1. Contactar Dirección de Deportes
2. Presentar: Certificados de competencias, medallas/trofeos
3. Evaluación técnica por entrenador de la modalidad
4. Entrevista con director de deportes
5. Aprobación y firma de pacto deportivo-académico

**CONTACTO:**
📧 deportes@udemedellin.edu.co
📞 +57 (604) 590-4500 ext. 2200

¿Te interesa otra beca?'''
    },
    'convenio': {
        'nombre': 'Becas por Convenio',
        'alias': ['convenio', 'convenios', 'empresa', 'corporativo'],
        'cobertura': 'Variable (30%-100%)',
        'descripcion': '''**BECAS POR CONVENIO** - Alianzas empresariales

Acuerdos especiales con empresas para apoyar a colaboradores y familias.

📊 **COBERTURA:**
Variable entre 30% - 100%
(Según convenio y empresa)

**CONVENIOS VIGENTES:**
✓ Sectores: Energía, Telecom, Manufactura, Tecnología
✓ Empresas: Ecopetrol, Grupo EPM, Colciencias, Bancolombia, Telefónica
✓ Cobertura: Empleados, hijos de empleados, jubilados

**TIPOS DE CONVENIOS:**
✓ Convenios Laborales: Empleados de empresa
✓ Convenios Sindicales: Afiliados a sindicatos
✓ Convenios Gremiales: Agremiados
✓ Convenios Institucionales: ONG, fundaciones

**REQUISITOS TÍPICOS:**
✓ Ser empleado o vinculado a organización convenida
✓ Antigüedad mínima (generalmente 6 meses)
✓ Desempeño académico: 7.0 o superior
✓ Certificación de permanencia en la empresa

**PROCEDIMIENTO:**
1. Verificar si su empresa tiene convenio
2. Solicitar certificado de convenio en RH de empresa
3. Presentar documentación en oficina de becas UdeMedellin
4. Validación y aprobación automática
5. Integración en sistema de descuentos

**EMPRESAS CON MAYOR COBERTURA:**
📊 100% Cobertura: Ecopetrol, EPM (solo hijos empleados)
📊 80% Cobertura: Telefónica, Bancolombia
📊 70% Cobertura: Colciencias, Seguros Suramericana
📊 50% Cobertura: Grupo Argos, Cemento Argos

**CONTACTO:**
📧 becas@udemedellin.edu.co
📞 +57 (604) 590-4500 ext. 1234
💼 Preguntar por tu empresa específicamente

¿Deseas información sobre otra beca?'''
    },
    'desempenio': {
        'nombre': 'Beca por Desempeño Académico',
        'alias': ['desempeño', 'desempeno', 'rendimiento', 'semestral'],
        'cobertura': 'Hasta 50%',
        'descripcion': '''**BECA POR DESEMPEÑO ACADÉMICO** - Recompensa tu progreso

Reconoce y respalda el excelente rendimiento durante tus estudios.

📊 **COBERTURA:**
Hasta 50% de la matrícula anual
(Renovable cada semestre según desempeño)

**REQUISITOS:**
✓ Promedio semestral: 4.2 o superior (en escala 5.0)
✓ Mínimo 15 créditos aprobados por semestre
✓ Ninguna calificación inferior a 3.0
✓ Comportamiento académico y convivencial excelente

**RENOVACIÓN:**
✓ Beca se renueva cada semestre si se mantiene promedio
✓ Incremento de cobertura: 4.2 (25%) → 4.5 (35%) → 4.7 (50%)
✓ Hasta 10 semestres consecutivos

**PÚBLICO OBJETIVO:**
✓ Cualquier estudiante de pregrado UdeMedellin
✓ Sin restricción de estrato o situación económica
✓ Independiente de fuente de financiamiento inicial

**BENEFICIOS ADICIONALES:**
✓ Reconocimiento en acto académico semestral
✓ Inscripción garantizada en cursos electivos
✓ Prioridad en matrículas tempranas
✓ Acceso a programas de liderazgo

**AUTOMATIZACIÓN:**
✓ Sistema genera automáticamente al final de semestre
✓ No requiere solicitud, se aplica sobre matrícula
✓ Notificación por email

**CONTACTO:**
📧 registro@udemedellin.edu.co
📞 +57 (604) 590-4500 ext. 1050
🎓 Consultar estado de becas en portal estudiantil

¿Te gustaría saber de otra beca?'''
    }
}

class ViviHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/interfaz.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body.decode('utf-8'))
                message = data.get('message', '').strip().lower()

                response_text = self.obtener_respuesta(message)

                response_data = {'response': json.dumps({'text': response_text}, ensure_ascii=False)}
                response_json = json.dumps(response_data, ensure_ascii=False).encode('utf-8')

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', len(response_json))
                self.end_headers()
                self.wfile.write(response_json)
            except Exception as e:
                error_response = {'response': json.dumps({'text': f'Error: {str(e)}'}, ensure_ascii=False)}
                response_json = json.dumps(error_response, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response_json)
        else:
            self.send_response(404)
            self.end_headers()

    def obtener_respuesta(self, message):
        """Obtener respuesta específica con búsqueda inteligente"""

        # Búsqueda exacta en carreras
        for key, carrera in CARRERAS.items():
            if key in message or carrera['nombre'].lower() in message:
                for alias in carrera['alias']:
                    if alias in message:
                        return carrera['descripcion']

        # Búsqueda exacta en becas
        for key, beca in BECAS.items():
            if key in message or beca['nombre'].lower() in message:
                for alias in beca['alias']:
                    if alias in message:
                        return beca['descripcion']

        # Búsqueda similar (fuzzy matching) para carreras
        if any(word in message for word in ['carrera', 'programa', 'pregrado', 'estudio', 'qué estudiar']):
            matches = self.buscar_similar(message, list(CARRERAS.values()) + list(BECAS.values()))
            if matches:
                return f'''¿Tal vez buscas...?\n\n{matches}\n\nEscribe el nombre exacto de la carrera o beca para más detalles.'''

        # Respuestas generales
        if any(word in message for word in ['ingenier']):
            return '''**FACULTAD DE INGENIERÍAS - 6 Programas de Excelencia**

Escribe el nombre de la ingeniería para detalles profesionales:

1. **Ingeniería Civil** - Infraestructuras y construcción
2. **Ingeniería de Sistemas** - Software, desarrollo y IA
3. **Ingeniería Industrial** - Optimización de procesos
4. **Ingeniería Mecánica** - Máquinas e innovación
5. **Ingeniería Electrónica** - IoT y sistemas inteligentes
6. **Ingeniería Ambiental** - Sostenibilidad y ambiente

📊 **DATOS GENERALES:**
✓ Duración: 10 semestres
✓ Costo: $12,5M - $15M/año
✓ Empleabilidad: 93-98%
✓ Laboratorios de clase mundial
✓ Salarios iniciales: $2,6M - $4,5M

¿Cuál carrera te interesa? Escribe su nombre para detalles específicos.'''

        elif any(word in message for word in ['beca', 'financiación', 'apoyo', 'descuento', 'costo', 'dinero']):
            return '''**BECAS Y FINANCIACIÓN - 5 Opciones Disponibles**

Escribe el tipo de beca para conocer requisitos y beneficios:

1. **Mérito Académico** - Reconoce tu excelencia (Hasta 100%)
2. **Socioeconómica** - Igualdad de oportunidades (Hasta 80%)
3. **Deportiva** - Talento atlético (Hasta 75%)
4. **Convenio** - Alianzas empresariales (30%-100%)
5. **Desempeño** - Recompensa tu progreso (Hasta 50%)

📊 **DATOS GENERALES:**
✓ Cobertura desde 30% hasta 100%
✓ Renovación semestral según desempeño
✓ Beneficios adicionales en servicios universitarios
✓ Apoyo en servicios estudiantiles
✓ Más de 2,000 estudiantes con beca

**PRÓXIMOS PASOS:**
📧 becas@udemedellin.edu.co
📞 +57 (604) 590-4500 ext. 1234

¿Qué tipo de beca te interesa? Escribe su nombre.'''

        elif any(word in message for word in ['inscr', 'admisión', 'cómo ingres', 'requisito', 'solicitud']):
            return '''**ADMISIÓN - PROCESO COMPLETO**

📋 **DOCUMENTOS REQUERIDOS:**
✓ Diploma de bachiller (original o copia auténtica)
✓ Cédula de identidad (original)
✓ Certificado de calificaciones bachillerato
✓ Foto digital reciente (3x4)

⏳ **PASOS DEL PROCESO:**
1. Crear cuenta en www.udemedellin.edu.co
2. Presentar pruebas de admisión (SABER 11 o equivalente)
3. Diligenciar formulario de inscripción
4. Pagar valor de inscripción ($500,000)
5. Resultado: 2-3 semanas

✓ **OCUPAR CUPO:**
6. Reservar cupo (48 horas)
7. Pagar matrícula inicial
8. Asistir a inducción

📞 **CONTACTO - ADMISIONES:**
📧 admisiones@udemedellin.edu.co
📞 +57 (604) 590-4500 ext. 1010
⏰ Lunes-Viernes 8am-6pm | Sábado 9am-1pm

¿Necesitas información sobre algún programa específico?'''

        elif any(word in message for word in ['campus', 'dónde', 'ubicación', 'infraestructura', 'instalación']):
            return '''**CAMPUS VIVO - UBICACIÓN Y INFRAESTRUCTURA**

📍 **UBICACIÓN PRINCIPAL:**
Carrera 87 N° 30-65, Barrio Laureles
Medellín, Antioquia
🚇 Metro: Estación Estadio (5 min caminando)

🏢 **INFRAESTRUCTURA DESTACADA:**
✓ Teatro Gabriel Obregón Botero (1,702 asientos)
✓ Biblioteca Eduardo Fernández Botero (80,000 volúmenes)
✓ Laboratorios especializados por facultad
✓ Coliseo deportivo completo (baloncesto, voleibol, etc.)
✓ Centro de Idiomas moderno
✓ Zonas verdes para recreación
✓ Comedor universitario con menú variado
✓ Cafetería y espacios de estudio

📞 **CONTACTO:**
📍 +57 (604) 590-4500

¿Deseas conocer detalles de un programa específico?'''

        elif any(word in message for word in ['idioma', 'inglés', 'francés', 'alemán', 'chino']):
            return '''**CENTRO DE IDIOMAS - EDUCACIÓN MULTILINGÜE**

🌍 **IDIOMAS OFRECIDOS:**
✓ Inglés (6 niveles) - Certificación Cambridge
✓ Francés (5 niveles) - Certificación DELF
✓ Alemán (4 niveles) - Certificación Goethe
✓ Italiano (3 niveles)
✓ Chino Mandarín (3 niveles)

📚 **MODALIDADES:**
✓ Clases presenciales
✓ Clases virtuales
✓ Intensivos en verano
✓ Conversación y negocios

⏰ **HORARIOS:**
Matutino: 6:30am - 9:00am
Vespertino: 5:00pm - 8:00pm
Sabatino: 9:00am - 1:00pm

💰 **COSTO:**
$350,000 - $450,000 por nivel

📧 **INFORMACIÓN:**
idiomas@udemedellin.edu.co
📞 +57 (604) 590-4500 ext. 2100

¿Algo más que desees saber?'''

        elif any(word in message for word in ['contact', 'teléfono', 'correo', 'dirección', 'ubicación']):
            return '''**CONTACTO - INFORMACIÓN GENERAL**

📞 **TELÉFONO PRINCIPAL:**
+57 (604) 590-4500

📧 **EMAIL GENERAL:**
info@udemedellin.edu.co

📍 **DIRECCIÓN PRINCIPAL:**
Carrera 87 N° 30-65, Medellín

⏰ **HORARIO DE ATENCIÓN:**
Lunes-Viernes: 8:00am - 12:00pm y 2:00pm - 6:00pm
Sábado: 9:00am - 1:00pm
Domingo: Cerrado

📋 **EXTENSIONES DIRECTAS:**
• Admisiones: ext. 1010
• Becas: ext. 1234
• Registro y Calificaciones: ext. 1050
• Centro de Idiomas: ext. 2100
• Dirección de Deportes: ext. 2200
• Biblioteca: ext. 1500

🌐 **SEDE BOGOTÁ:**
Calle 57 # 9-52, Chapinero
📞 +57 (1) 345-6789

📱 **REDES SOCIALES:**
@udemedellin (Facebook, Instagram, TikTok)

¿Necesitas información específica sobre algo?'''

        else:
            return '''¡Hola! Soy **Vivi**, tu asistente virtual de la Universidad de Medellín 🎓

Te puedo ayudar con:

🎓 **CARRERAS** - Conoce nuestros 27 programas
   • 6 Ingenierías (Civil, Sistemas, Industrial, etc.)
   • Derecho, Administración, Contabilidad
   • Comunicación, Publicidad, Diseño y más

💰 **BECAS** - 5 opciones de financiación
   • Mérito Académico | Socioeconómica | Deportiva
   • Convenios empresariales | Desempeño

📋 **ADMISIÓN** - Cómo inscribirse
📍 **CAMPUS** - Ubicación e infraestructura
🌍 **IDIOMAS** - Centro de Idiomas
📞 **CONTACTO** - Teléfono y dirección

**¿Qué te gustaría saber?**
Escribe el nombre de una carrera, beca, o cualquier pregunta sobre UdeMedellin.'''

    def buscar_similar(self, message, opciones):
        """Buscar opciones similares usando fuzzy matching"""
        palabras_clave = []
        for opcion in opciones:
            nombre = opcion.get('nombre', '').lower()
            if nombre and difflib.SequenceMatcher(None, message, nombre).ratio() > 0.6:
                palabras_clave.append(nombre)

        if palabras_clave:
            return '\n'.join([f"✓ {p.title()}" for p in palabras_clave[:5]])
        return ''

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    os.chdir('C:\\Users\\p20on\\Documents\\Vsproyects\\Chatbot')
    server_address = ('127.0.0.1', 9999)
    httpd = http.server.HTTPServer(server_address, ViviHandler)
    print("Vivi Professional Server en http://localhost:9999")
    httpd.serve_forever()
