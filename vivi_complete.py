#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import json
import os

# BASE DE DATOS COMPLETA DE TODOS LOS PROGRAMAS
PROGRAMAS = {
    'civil': {
        'nombre': 'Ingeniería Civil',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA CIVIL** - Construye el futuro

Diseña y construye la infraestructura que conecta el mundo.

📊 **PERFIL:** Profesional que diseña, construye y mantiene infraestructuras (puentes, carreteras, edificios, hidroeléctricas)

💼 **CAMPOS LABORALES:**
✓ Empresas constructoras y desarrolladoras inmobiliarias
✓ Proyectos de infraestructura vial y de transporte
✓ Obras hidráulicas y sanitarias
✓ Entidades gubernamentales (Vías, Acueducto, CAR)
✓ Consultoría técnica y supervisión de obras
✓ Proyectos de energía y telecomunicaciones

🎓 **DIFERENCIALES:**
- Laboratorio de Mecánica de Suelos y Hormigón
- Convenios con empresas constructoras líderes
- Prácticas en obras reales durante carrera
- 96% de empleabilidad
- Salario inicial: $2,500,000 - $3,500,000

¿Deseas saber de otra ingeniería?'''
    },
    'sistemas': {
        'nombre': 'Ingeniería de Sistemas',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA DE SISTEMAS** - Transforma con tecnología

Crea soluciones digitales que revolucionan industrias.

📊 **PERFIL:** Ingeniero especializado en desarrollo de software, análisis de datos y transformación digital

💼 **CAMPOS LABORALES:**
✓ Desarrollo de aplicaciones y software empresarial
✓ Big Data y Ciencia de Datos
✓ Cloud Computing (AWS, Azure, Google Cloud)
✓ Ciberseguridad e infraestructura TI
✓ Startup tecnológicas y fintech
✓ Consultoría tecnológica
✓ Machine Learning e Inteligencia Artificial

🎓 **DIFERENCIALES:**
- Laboratorios con tecnología de punta
- Certificaciones en Cloud: AWS, Azure, Google Cloud
- Lenguajes: Python, Java, JavaScript, C++
- Convenios con empresas tecnológicas líderes
- 98% de empleabilidad
- Salario inicial: $3,000,000 - $4,500,000

¿Quieres conocer otras opciones?'''
    },
    'industrial': {
        'nombre': 'Ingeniería Industrial',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA INDUSTRIAL** - Optimiza resultados

Mejora procesos para generar mayor valor en organizaciones.

📊 **PERFIL:** Profesional que optimiza recursos, procesos y sistemas en empresas de cualquier sector

💼 **CAMPOS LABORALES:**
✓ Consultoría empresarial y de procesos
✓ Manufactura y producción
✓ Logística y cadena de suministro
✓ Banca y seguros
✓ Retail y comercio electrónico
✓ Gestión de proyectos
✓ Emprendimiento

🎓 **DIFERENCIALES:**
- Metodologías Lean, Six Sigma y Kaizen
- Simulación de procesos avanzada
- Análisis de datos y Business Intelligence
- Pasantías en empresas Fortune 500
- 94% de empleabilidad
- Salario inicial: $2,800,000 - $4,000,000

¿Interesado en otra carrera?'''
    },
    'mecanica': {
        'nombre': 'Ingeniería Mecánica',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA MECÁNICA** - Diseña máquinas del futuro

Crea máquinas y sistemas que impulsan la industria global.

📊 **PERFIL:** Ingeniero que diseña, fabrica y automatiza máquinas y sistemas mecánicos

💼 **CAMPOS LABORALES:**
✓ Diseño y manufactura
✓ Industria automotriz
✓ Energía renovable (solar, eólica, hidroeléctrica)
✓ Minería y extracción
✓ Robótica e automatización
✓ Investigación y desarrollo
✓ Consultoría técnica

🎓 **DIFERENCIALES:**
- CAD/CAM de última generación (Solidworks, NX)
- Laboratorio de Máquinas Herramientas CNC
- Pruebas en Máquina Universal de 300 toneladas
- Convenios con plantas manufactureras
- 95% de empleabilidad
- Salario inicial: $2,700,000 - $3,800,000

¿Deseas conocer más programas?'''
    },
    'electronica': {
        'nombre': 'Ingeniería Electrónica',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA ELECTRÓNICA** - Conecta el mundo

Diseña sistemas inteligentes que conectan dispositivos e industrias.

📊 **PERFIL:** Ingeniero especializado en circuitos, sistemas embebidos e IoT

💼 **CAMPOS LABORALES:**
✓ Telecomunicaciones y redes
✓ Electrónica de consumo
✓ Automatización industrial
✓ IoT y Smart Cities
✓ Dispositivos médicos
✓ Energía inteligente
✓ Investigación y desarrollo

🎓 **DIFERENCIALES:**
- Laboratorios de electrónica digital y analógica
- Simuladores profesionales: SPICE, Proteus, Multisim
- Microcontroladores: Arduino, PIC, ARM
- Proyectos con aplicaciones en IoT
- 97% de empleabilidad
- Salario inicial: $2,900,000 - $4,200,000

¿Quieres saber de otra ingeniería?'''
    },
    'ambiental': {
        'nombre': 'Ingeniería Ambiental',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA AMBIENTAL** - Cuida el planeta

Protege la naturaleza mientras generas desarrollo sostenible.

📊 **PERFIL:** Profesional comprometido con sostenibilidad y protección del medio ambiente

💼 **CAMPOS LABORALES:**
✓ Consultorías y auditorías ambientales
✓ Tratamiento de agua y residuos
✓ Energías renovables y eficiencia energética
✓ Minería y extracción sostenible
✓ Entidades ambientales (ANLA, Corporaciones)
✓ Industria manufacturera
✓ Monitoreo ambiental

🎓 **DIFERENCIALES:**
- Laboratorio de Calidad de Agua y Aire
- Proyectos de sustentabilidad real
- Normativa ambiental colombiana e internacional
- Convenios con organismos ambientales
- 93% de empleabilidad
- Salario inicial: $2,600,000 - $3,600,000

¿Te interesa otra carrera?'''
    },
    'derecho': {
        'nombre': 'Derecho',
        'facultad': 'FACULTAD DE DERECHO',
        'duracion': '10 semestres',
        'costo': '$11,000,000 - $13,500,000/año',
        'descripcion': '''**DERECHO** - Defiende la justicia

Estudia la disciplina más prestigiosa de la UdeMedellin.

📊 **PERFIL:** Abogado preparado para defender derechos en cualquier rama legal

💼 **CAMPOS LABORALES:**
✓ Ejercicio profesional independiente
✓ Despachos de abogados líderes
✓ Asesoría legal corporativa
✓ Entidades gubernamentales y públicas
✓ Justicia ordinaria y especializada
✓ Derecho internacional
✓ Docencia y investigación

🎓 **DIFERENCIALES:**
- **96% de aprobación en Examen de Estado** (la mejor del país)
- Convenios con firmas de abogados Top 10
- Simuladores de juicio y cortes
- Clínica jurídica con casos reales
- Especializaciones en Derecho Laboral, Comercial, Penal
- Salario inicial: $3,500,000 - $6,000,000

¿Deseas conocer otro programa?'''
    },
    'administracion': {
        'nombre': 'Administración',
        'facultad': 'FACULTAD DE CIENCIAS ECONÓMICAS',
        'duracion': '8 semestres',
        'costo': '$10,000,000 - $12,000,000/año',
        'descripcion': '''**ADMINISTRACIÓN** - Gestiona empresas exitosas

Lidera organizaciones hacia el éxito empresarial.

📊 **PERFIL:** Administrador con visión estratégica y capacidad de liderazgo

💼 **CAMPOS LABORALES:**
✓ Gerencia general en empresas privadas
✓ Consultoría empresarial y estratégica
✓ Startups y emprendimiento
✓ Sector público y ONG
✓ Gestión de recursos humanos
✓ Finanzas y inversión
✓ Logística y supply chain

🎓 **DIFERENCIALES:**
- Diplomado en Emprendimiento
- Certificación en Project Management (PMP)
- Casos de empresas reales
- Convenios con empresas multinacionales
- Intercambios internacionales
- 91% de empleabilidad
- Salario inicial: $2,500,000 - $3,800,000

¿Quieres saber de otra carrera?'''
    },
    'contabilidad': {
        'nombre': 'Contabilidad',
        'facultad': 'FACULTAD DE CIENCIAS ECONÓMICAS',
        'duracion': '8 semestres',
        'costo': '$10,000,000 - $12,000,000/año',
        'descripcion': '''**CONTABILIDAD** - Controla las finanzas

Sé el experto financiero en cualquier organización.

📊 **PERFIL:** Contador público capacitado en gestión financiera y tributaria

💼 **CAMPOS LABORALES:**
✓ Firmas de auditoría (Big 4 y Top 10)
✓ Asesoría tributaria y contable
✓ Departamentos de contabilidad corporativa
✓ Consultoría empresarial
✓ Entidades financieras
✓ Independencia profesional
✓ Peritaje contable

🎓 **DIFERENCIALES:**
- Certificación IFRS y NIIF
- Auditoría interna y externa
- Tributación actualizada
- Prácticas en firmas auditoras líderes
- Software contable profesional: SAP, Oracle
- 92% de empleabilidad
- Salario inicial: $2,300,000 - $3,500,000

¿Te interesa otra carrera?'''
    },
    'comunicacion': {
        'nombre': 'Comunicación Social',
        'facultad': 'FACULTAD DE COMUNICACIÓN',
        'duracion': '8 semestres',
        'costo': '$9,500,000 - $11,500,000/año',
        'descripcion': '''**COMUNICACIÓN SOCIAL** - Crea mensajes que impactan

Conecta marcas con audiencias a través de estrategias innovadoras.

📊 **PERFIL:** Comunicador especializado en medios, marketing y comunicación corporativa

💼 **CAMPOS LABORALES:**
✓ Agencias de publicidad y marketing
✓ Departamentos de comunicación corporativa
✓ Medios de comunicación (TV, radio, digital)
✓ Community management y redes sociales
✓ Producción audiovisual
✓ Relaciones públicas
✓ Comunicación política y social

🎓 **DIFERENCIALES:**
- Estudios de TV, radio y podcast profesionales
- Edición de video y fotografía avanzada
- Estrategia digital y social media
- Convenios con agencias creativas líderes
- Prácticas en medios de comunicación
- 89% de empleabilidad
- Salario inicial: $2,000,000 - $3,200,000

¿Deseas conocer más opciones?'''
    },
    'publicidad': {
        'nombre': 'Publicidad',
        'facultad': 'FACULTAD DE COMUNICACIÓN',
        'duracion': '8 semestres',
        'costo': '$9,500,000 - $11,500,000/año',
        'descripcion': '''**PUBLICIDAD** - Vende con creatividad

Crea campañas publicitarias que conquistan mercados.

📊 **PERFIL:** Publicista creativo con visión estratégica y comercial

💼 **CAMPOS LABORALES:**
✓ Agencias de publicidad creativas
✓ Departamentos de marketing
✓ Mercadotecnia digital y e-commerce
✓ Branding y diseño corporativo
✓ Medios y planificación publicitaria
✓ Consultoría creativa
✓ Emprendimiento

🎓 **DIFERENCIALES:**
- Dirección de arte y diseño gráfico
- Producción audiovisual y cinematografía
- Marketing digital y SEM/SEO
- Proyectos reales con marcas
- Convenios con agencias Top 10
- Portfolio profesional
- 88% de empleabilidad
- Salario inicial: $2,100,000 - $3,400,000

¿Quieres saber de otra carrera?'''
    },
    'economia': {
        'nombre': 'Economía',
        'facultad': 'FACULTAD DE CIENCIAS ECONÓMICAS',
        'duracion': '8 semestres',
        'costo': '$10,000,000 - $12,000,000/año',
        'descripcion': '''**ECONOMÍA** - Analiza mercados globales

Entiende y predice el comportamiento de economías y mercados.

📊 **PERFIL:** Economista especializado en análisis macroeconómico y política económica

💼 **CAMPOS LABORALES:**
✓ Banco de la República y entidades financieras
✓ Análisis económico corporativo
✓ Consultoría económica y de inversión
✓ Organismos internacionales (FMI, BID, ONU)
✓ Investigación y docencia
✓ Análisis de riesgo
✓ Inversión y bolsa de valores

🎓 **DIFERENCIALES:**
- Análisis econométrico avanzado
- Modelos de series de tiempo
- Python y R para análisis de datos
- Prácticas en bancos y entidades financieras
- Convenios con instituciones internacionales
- 90% de empleabilidad
- Salario inicial: $2,400,000 - $3,800,000

¿Te interesa otra carrera?'''
    },
    'mercadotecnia': {
        'nombre': 'Mercadotecnia',
        'facultad': 'FACULTAD DE CIENCIAS ECONÓMICAS',
        'duracion': '8 semestres',
        'costo': '$10,000,000 - $12,000,000/año',
        'descripcion': '''**MERCADOTECNIA** - Domina el mercado

Desarrolla estrategias de marketing que generan resultados.

📊 **PERFIL:** Especialista en marketing estratégico y gestión de marcas

💼 **CAMPOS LABORALES:**
✓ Departamentos de marketing corporativo
✓ Agencias de publicidad y marketing
✓ E-commerce y comercio digital
✓ Empresas de consumo y retail
✓ Consultoría de marketing
✓ Product management
✓ Emprendimiento

🎓 **DIFERENCIALES:**
- Marketing digital y data analytics
- Gestión de redes sociales
- Consumer insights y investigación de mercado
- Prácticas en empresas multinacionales
- Certificaciones en Google Analytics, Meta
- 90% de empleabilidad
- Salario inicial: $2,300,000 - $3,500,000

¿Deseas conocer otra opción?'''
    },
    'diseno': {
        'nombre': 'Diseño Gráfico',
        'facultad': 'FACULTAD DE DISEÑO',
        'duracion': '8 semestres',
        'costo': '$10,500,000 - $12,500,000/año',
        'descripcion': '''**DISEÑO GRÁFICO** - Crea belleza y función

Diseña identidades visuales que marcan la diferencia.

📊 **PERFIL:** Diseñador especializado en comunicación visual y diseño de marca

💼 **CAMPOS LABORALES:**
✓ Agencias de diseño y creatividad
✓ Diseño corporativo y branding
✓ Diseño editorial y packaging
✓ Diseño digital e interfaces
✓ Dirección de arte
✓ Consultoría de imagen corporativa
✓ Emprendimiento

🎓 **DIFERENCIALES:**
- Software profesional: Adobe Creative Suite
- Tipografía y composición avanzada
- Diseño web y UX/UI
- Prácticas en agencias creativas
- Portfolio internacional
- 87% de empleabilidad
- Salario inicial: $2,200,000 - $3,400,000

¿Te interesa otro programa?'''
    },
    'industrial_diseno': {
        'nombre': 'Diseño Industrial',
        'facultad': 'FACULTAD DE DISEÑO',
        'duracion': '8 semestres',
        'costo': '$10,500,000 - $12,500,000/año',
        'descripcion': '''**DISEÑO INDUSTRIAL** - Diseña productos innovadores

Crea objetos funcionales y hermosos que mejoran la vida.

📊 **PERFIL:** Diseñador especializado en desarrollo de productos

💼 **CAMPOS LABORALES:**
✓ Empresas de manufactura
✓ Consultoría de diseño e innovación
✓ Diseño de muebles y decoración
✓ Electrónica de consumo
✓ Industria automotriz
✓ Startup de productos
✓ Emprendimiento

🎓 **DIFERENCIALES:**
- Modelado 3D: Rhino, Solidworks, Fusion 360
- Prototipado rápido y fabricación digital
- Sostenibilidad en diseño
- Taller de manufactura
- 88% de empleabilidad
- Salario inicial: $2,200,000 - $3,500,000

¿Deseas saber de otra carrera?'''
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
                error_response = {'response': json.dumps({'text': str(e)}, ensure_ascii=False)}
                response_json = json.dumps(error_response, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response_json)
        else:
            self.send_response(404)
            self.end_headers()

    def obtener_respuesta(self, message):
        """Obtener respuesta específica basada en el mensaje"""

        # Buscar programa específico
        for key, info in PROGRAMAS.items():
            if key in message or info['nombre'].lower() in message:
                return info['descripcion']

        # Respuestas generales
        if any(word in message for word in ['ingenier']):
            return '''**FACULTAD DE INGENIERÍAS - 6 Programas Excelentes**

Escribe el nombre de la ingeniería para detalles:

1. **Civil** - Infraestructuras y construcción
2. **Sistemas** - Software e IA
3. **Industrial** - Optimización de procesos
4. **Mecánica** - Máquinas e innovación
5. **Electrónica** - IoT y sistemas inteligentes
6. **Ambiental** - Sostenibilidad

Empleabilidad: 93-98% | Salarios: $2,6M - $4,5M'''

        elif any(word in message for word in ['derecho']):
            return PROGRAMAS['derecho']['descripcion']

        elif any(word in message for word in ['administr']):
            return PROGRAMAS['administracion']['descripcion']

        elif any(word in message for word in ['contab']):
            return PROGRAMAS['contabilidad']['descripcion']

        elif any(word in message for word in ['comunicacion']):
            return PROGRAMAS['comunicacion']['descripcion']

        elif any(word in message for word in ['publicidad']):
            return PROGRAMAS['publicidad']['descripcion']

        elif any(word in message for word in ['economia']):
            return PROGRAMAS['economia']['descripcion']

        elif any(word in message for word in ['mercado']):
            return PROGRAMAS['mercadotecnia']['descripcion']

        elif any(word in message for word in ['diseno', 'diseño', 'grafico']):
            return PROGRAMAS['diseno']['descripcion']

        elif any(word in message for word in ['diseno industrial', 'industrial', 'producto']):
            return PROGRAMAS['industrial_diseno']['descripcion']

        elif any(word in message for word in ['carrera', 'programa', 'pregrado', 'qué estudiar']):
            return '''**27 PROGRAMAS DE PREGRADO - Elige tu camino**

**FACULTAD DE INGENIERÍAS** (6 programas)
Civil | Sistemas | Industrial | Mecánica | Electrónica | Ambiental

**FACULTAD DE DERECHO** (1 programa)
Derecho

**FACULTAD DE CIENCIAS ECONÓMICAS** (4 programas)
Administración | Contabilidad | Economía | Mercadotecnia

**FACULTAD DE COMUNICACIÓN** (2 programas)
Comunicación Social | Publicidad

**FACULTAD DE DISEÑO** (2 programas)
Diseño Gráfico | Diseño Industrial

Escribe el nombre de cualquier carrera para detalles específicos.'''

        elif any(word in message for word in ['inscr', 'registro', 'admisión', 'cómo ingres', 'requisito']):
            return '''Para inscribirte a la UdeMedellín:

1. Diploma de bachiller
2. Pruebas de admisión (SABER 11)
3. Formulario en www.udemedellin.edu.co
4. Pagar valor de inscripción
5. Esperar resultado (2-3 semanas)

Contacto: +57 (604) 590-4500 ext. 1010'''

        elif any(word in message for word in ['beca', 'financiación', 'apoyo económico']):
            return '''**BECAS Y FINANCIACIÓN**

Tipos:
✓ Mérito Académico: Hasta 100%
✓ Socioeconómica: Hasta 80%
✓ Deportiva: Hasta 75%
✓ Convenios: Variable
✓ Desempeño: Por excelencia

Contacto: +57 (604) 590-4500 ext. 1234'''

        elif any(word in message for word in ['campus', 'dónde', 'ubicación', 'infraestructur']):
            return '''**CAMPUS VIVO - Carrera 87 N° 30-65, Medellín**

✓ Teatro Gabriel Obregón Botero (1,702 sillas)
✓ Biblioteca Eduardo Fernández Botero
✓ Laboratorios de última generación
✓ Coliseo deportivo completo
✓ Centro de Idiomas
✓ Zonas verdes

Metro: Estación Estadio (5 min)'''

        elif any(word in message for word in ['idioma', 'inglés', 'francés', 'alemán']):
            return '''**CENTRO DE IDIOMAS**

Inglés | Francés | Alemán | Italiano | Chino

Certificaciones: Cambridge, DELF, Goethe
Costo: $350,000 - $450,000/nivel
Horarios: Matutino | Vespertino | Sabatino

Info: idiomas@udemedellin.edu.co'''

        elif any(word in message for word in ['contact', 'teléfono', 'correo']):
            return '''📞 +57 (604) 590-4500
📧 info@udemedellin.edu.co
📍 Carrera 87 N° 30-65, Medellín

Horario: Lunes-Viernes 8am-6pm | Sábado 9am-1pm

EXTENSIONES:
- Admisiones: 1010
- Becas: 1234
- Registro: 1050
- Idiomas: 2100'''

        else:
            return '''¡Hola! Soy Vivi, tu asistente de la UdeMedellín.

Puedo ayudarte con:
✓ 27 Programas académicos
✓ Admisiones e inscripción
✓ Becas y financiación
✓ Campus e infraestructura
✓ Centro de Idiomas
✓ Contacto y ubicación

¿Qué carrera te interesa?'''

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    os.chdir('C:\\Users\\p20on\\Documents\\Vsproyects\\Chatbot')
    server_address = ('127.0.0.1', 9999)
    httpd = http.server.HTTPServer(server_address, ViviHandler)
    print("Vivi HTTP Server en http://localhost:9999")
    httpd.serve_forever()
