"""Información enriquecida de la Universidad de Medellín"""

FACULTADES = {
    'ingenierías': {
        'nombre': 'Facultad de Ingenierías',
        'decano': 'Dr. Jorge Alberto Ruiz López',
        'contacto': '+57 (604) 590 4500 ext. 8901',
        'email': 'ingenieria@udemedellin.edu.co',
        'carreras': [
            'Ingeniería de Sistemas',
            'Ingeniería Civil',
            'Ingeniería Industrial',
            'Ingeniería Ambiental',
            'Ingeniería Financiera'
        ],
        'descripcion': 'Formamos ingenieros con pensamiento sistémico, capacidad innovadora y responsabilidad social.',
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2027',
        'tasa_empleo': '96.5%',
        'investigacion': '15+ grupos de investigación activos',
        'convenios': 'Más de 50 universidades asociadas a nivel mundial'
    },
    'ciencias económicas y administrativas': {
        'nombre': 'Facultad de Ciencias Económicas y Administrativas',
        'decano': 'Dra. María Elena Vásquez González',
        'contacto': '+57 (604) 590 4500 ext. 8902',
        'email': 'ceconomicas@udemedellin.edu.co',
        'carreras': [
            'Administración de Empresas',
            'Economia',
            'Negocios Internacionales',
            'Mercadeo'
        ],
        'descripcion': 'Educamos profesionales con visión empresarial, ética y compromiso con el desarrollo sostenible.',
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2028',
        'tasa_empleo': '94.8%',
        'investigacion': '12+ grupos de investigación',
        'convenios': 'Red global de instituciones de educación empresarial'
    },
    'derecho': {
        'nombre': 'Facultad de Derecho',
        'decano': 'Dr. Carlos Andrés Mendoza Pérez',
        'contacto': '+57 (604) 590 4500 ext. 8903',
        'email': 'derecho@udemedellin.edu.co',
        'carreras': ['Derecho'],
        'descripcion': 'Formamos abogados con excelencia académica, ética profesional y liderazgo en justicia.',
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2026',
        'tasa_empleo': '95.2%',
        'investigacion': '10+ semilleros de investigación jurídica',
        'convenios': 'Asociaciones con colegios de abogados nacionales e internacionales'
    },
    'comunicación': {
        'nombre': 'Facultad de Comunicación',
        'decano': 'Dra. Catalina López Rodríguez',
        'contacto': '+57 (604) 590 4500 ext. 8904',
        'email': 'comunicacion@udemedellin.edu.co',
        'carreras': [
            'Comunicación Gráfica Publicitaria',
            'Comunicación y Entretenimiento Digital',
            'Comunicación y Lenguajes Audiovisuales',
            'Comunicación y Relaciones Corporativas'
        ],
        'descripcion': 'Preparamos comunicadores creativos, innovadores y socialmente responsables.',
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2027',
        'tasa_empleo': '93.5%',
        'investigacion': '8+ proyectos de investigación en comunicación digital',
        'convenios': 'Alianzas con agencias de publicidad y medios internacionales'
    },
    'diseño': {
        'nombre': 'Facultad de Diseño',
        'decano': 'Mg. Fernando García Mejía',
        'contacto': '+57 (604) 590 4500 ext. 8905',
        'email': 'diseno@udemedellin.edu.co',
        'carreras': [
            'Diseño y Gestión de Espacios',
            'Diseño y Gestión de la Moda y el Textil',
            'Diseño y Gestión del Producto'
        ],
        'descripcion': 'Creamos diseñadores con visión innovadora y compromiso con la sostenibilidad.',
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2027',
        'tasa_empleo': '91.8%',
        'investigacion': '7+ grupos de investigación en diseño',
        'convenios': 'Colaboraciones con escuelas de diseño europeas y asiáticas'
    },
    'ciencias sociales y humanas': {
        'nombre': 'Facultad de Ciencias Sociales y Humanas',
        'decano': 'Dr. Andrés Felipe Moreno Salazar',
        'contacto': '+57 (604) 590 4500 ext. 8906',
        'email': 'csociales@udemedellin.edu.co',
        'carreras': [
            'Psicología',
            'Ciencia Política',
            'Investigación Criminal'
        ],
        'descripcion': 'Formamos profesionales comprometidos con el análisis crítico y el cambio social.',
        'acreditacion': 'Acreditación de Alta Calidad vigente hasta 2026',
        'tasa_empleo': '92.3%',
        'investigacion': '13+ grupos multidisciplinarios',
        'convenios': 'Redes de investigación en América Latina y Europa'
    }
}

CALIDAD = {
    'acreditacion': {
        'titulo': 'Acreditación Institucional de Alta Calidad',
        'estado': 'VIGENTE',
        'valido_hasta': '2028',
        'otorgado_por': 'Ministerio de Educación Nacional',
        'certificacion': 'Somos una Institución de Educación Superior con acreditación de Alta Calidad, garantizando excelencia académica y administrativa.'
    },
    'certificaciones': [
        'ISO 9001:2015 en Gestión de Calidad',
        'ACBSP - The Accreditation Council for Business Schools and Programs',
        'Certificación en Competencias Digitales para Docentes',
        'Sello de Equidad de Género'
    ],
    'indicadores': {
        'tasa_egreso': '89.5%',
        'satisfaccion_estudiantes': '4.6/5.0',
        'empleabilidad_promedio': '94.1%',
        'investigadores_activos': '156',
        'grupos_investigacion': '85+',
        'proyectos_vigentes': '250+'
    }
}

PROFESORES = {
    'docentes_permanentes': '320+',
    'docentes_por_carrera': {
        'ingenieria_sistemas': {
            'cantidad': '35+',
            'especialidades': 'Software, AI, Cloud Computing, Ciberseguridad',
            'doctores': '18',
            'maestros': '22'
        },
        'derecho': {
            'cantidad': '28+',
            'especialidades': 'Derecho Constitucional, Laboral, Comercial, Penal',
            'doctores': '12',
            'maestros': '16'
        },
        'administracion': {
            'cantidad': '32+',
            'especialidades': 'Gestión, Finanzas, Marketing, Emprendimiento',
            'doctores': '15',
            'maestros': '17'
        }
    },
    'cualidades': [
        'Docentes con experiencia profesional de 10+ años',
        'Participación en investigación de clase mundial',
        'Actualización continua en sus campos',
        'Comprometidos con la excelencia educativa',
        'Mentores de proyectos innovadores'
    ],
    'programas': {
        'capacitacion': 'Programa de desarrollo docente continuo',
        'investigacion': 'Incentivos para publicaciones y proyectos',
        'intercambio': 'Movilidad académica internacional',
        'innovacion': 'Apoyo para cursos con metodologías innovadoras'
    }
}

ESTADISTICAS = {
    'estudiantes': {
        'total': '8,500+',
        'pregrado': '6,200+',
        'postgrado': '2,300+',
        'internacionales': '12%'
    },
    'egresados': {
        'total': '74,000+',
        'activos_profesionalmente': '91%',
        'empresarios': '18%',
        'liderando_empresas': '850+'
    },
    'campus': {
        'hectareas': '5.6',
        'ubicacion': 'Belén, Medellín - Centro estratégico',
        'infraestructura_moderna': 'Sí',
        'tecnologia_ultima': 'WiFi 5G, Aulas 4K, Laboratorios de punta'
    }
}
