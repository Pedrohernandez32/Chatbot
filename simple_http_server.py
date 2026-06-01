#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import json
import os
from urllib.parse import urlparse, parse_qs

# Información detallada de cada programa
PROGRAMAS = {
    'civil': {
        'nombre': 'Ingeniería Civil',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA CIVIL**

Forma profesionales capacitados para diseñar, construir y mantener infraestructuras.

**PERFIL DEL EGRESADO:**
- Diseña estructuras resistentes y sostenibles
- Gestiona proyectos de construcción
- Realiza análisis de impacto ambiental
- Participa en obras públicas y privadas

**CAMPOS LABORALES:**
✓ Empresas constructoras y desarrolladoras
✓ Entidades gubernamentales (Vías, Acueducto)
✓ Consultoría técnica
✓ Independencia profesional
✓ Proyectos de infraestructura vial, hidráulica

**DIFERENCIALES:**
- Laboratorios de Mecánica de Suelos y Hormigón
- Convenios con empresas constructoras
- Prácticas en obras reales
- 96% de empleabilidad

¿Necesitas más detalles o deseas conocer otra ingeniería?'''
    },
    'sistemas': {
        'nombre': 'Ingeniería de Sistemas',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA DE SISTEMAS**

Forma profesionales para diseñar y gestionar soluciones tecnológicas innovadoras.

**PERFIL DEL EGRESADO:**
- Desarrolla software de calidad
- Diseña sistemas de información empresariales
- Gestiona bases de datos
- Implementa soluciones Cloud y IA
- Realiza análisis de ciberseguridad

**CAMPOS LABORALES:**
✓ Desarrollo de software
✓ Análisis de sistemas
✓ Consultoría tecnológica
✓ Big Data y Analytics
✓ Ciberseguridad
✓ Startups tecnológicas

**DIFERENCIALES:**
- Laboratorios con tecnología de punta
- Lenguajes: Java, Python, C++, JavaScript
- Certificaciones en Cloud (AWS, Azure)
- 98% de empleabilidad
- Salarios competitivos

¿Interesado en otras ingenierías?'''
    },
    'industrial': {
        'nombre': 'Ingeniería Industrial',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA INDUSTRIAL**

Forma profesionales para optimizar procesos y recursos en organizaciones.

**PERFIL DEL EGRESADO:**
- Optimiza procesos productivos
- Gestiona proyectos empresariales
- Analiza costos y eficiencia
- Mejora calidad y productividad
- Gestiona cadenas de suministro

**CAMPOS LABORALES:**
✓ Consultoría empresarial
✓ Manufactura y producción
✓ Logística y distribución
✓ Sector financiero
✓ Optimización de procesos
✓ Emprendimiento

**DIFERENCIALES:**
- Metodologías Lean y Six Sigma
- Simulación de procesos
- Análisis de datos avanzado
- Pasantías en empresas líderes
- 94% de empleabilidad

¿Qué otra ingeniería te interesa?'''
    },
    'mecanica': {
        'nombre': 'Ingeniería Mecánica',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA MECÁNICA**

Forma profesionales para diseñar y fabricar máquinas y sistemas mecánicos.

**PERFIL DEL EGRESADO:**
- Diseña equipos y máquinas
- Realiza análisis de resistencia
- Gestiona procesos de manufactura
- Desarrolla máquinas de automatización
- Innova en energías renovables

**CAMPOS LABORALES:**
✓ Diseño y manufactura
✓ Automotriz
✓ Energía (hidroeléctrica, térmica, eólica)
✓ Minería
✓ Consultoría técnica
✓ Investigación y desarrollo

**DIFERENCIALES:**
- CAD/CAM de última generación
- Laboratorio de Máquinas Herramientas
- Pruebas en Máquina Universal
- Convenios con plantas manufactureras
- 95% de empleabilidad

¿Te interesa saber de otra ingeniería?'''
    },
    'electronica': {
        'nombre': 'Ingeniería Electrónica',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA ELECTRÓNICA**

Forma profesionales para diseñar sistemas electrónicos avanzados e IoT.

**PERFIL DEL EGRESADO:**
- Diseña circuitos electrónicos
- Desarrolla sistemas embebidos
- Implementa soluciones IoT
- Trabaja con señales digitales
- Automatiza procesos

**CAMPOS LABORALES:**
✓ Telecomunicaciones
✓ Electrónica de consumo
✓ Automatización industrial
✓ IoT y Smart Cities
✓ Investigación y desarrollo
✓ Manufactura de componentes

**DIFERENCIALES:**
- Laboratorios de electrónica digital y analógica
- Simuladores SPICE y Proteus
- Microcontroladores y FPGA
- Proyectos con aplicaciones reales
- 97% de empleabilidad

¿Deseas conocer la Ingeniería Ambiental?'''
    },
    'ambiental': {
        'nombre': 'Ingeniería Ambiental',
        'facultad': 'FACULTAD DE INGENIERÍAS',
        'duracion': '10 semestres',
        'costo': '$12,500,000 - $15,000,000/año',
        'descripcion': '''**INGENIERÍA AMBIENTAL**

Forma profesionales comprometidos con la sostenibilidad y protección ambiental.

**PERFIL DEL EGRESADO:**
- Diseña sistemas de tratamiento de agua y residuos
- Realiza evaluaciones ambientales
- Gestiona recursos naturales
- Implementa energías renovables
- Desarrolla proyectos sostenibles

**CAMPOS LABORALES:**
✓ Consultorías ambientales
✓ Empresas de servicios ambientales
✓ Entidades ambientales (ANLA, Corporaciones)
✓ Industria manufacturera
✓ Energías renovables
✓ Minería sostenible

**DIFERENCIALES:**
- Laboratorio de Calidad de Agua
- Proyectos de sostenibilidad
- Normativa ambiental actualizada
- Convenios con organismos ambientales
- 93% de empleabilidad

¿Necesitas información sobre otras carreras?'''
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

        # Buscar ingeniería específica
        for key, info in PROGRAMAS.items():
            if key in message or info['nombre'].lower() in message:
                return info['descripcion']

        # Palabras clave generales
        if any(word in message for word in ['ingenier']):
            return """**FACULTAD DE INGENIERÍAS - Programas Disponibles:**

Tenemos 6 programas de ingeniería de excelencia:

1. **Ingeniería Civil** - Infraestructuras y construcción
2. **Ingeniería de Sistemas** - Software y tecnología
3. **Ingeniería Industrial** - Optimización de procesos
4. **Ingeniería Mecánica** - Diseño de máquinas
5. **Ingeniería Electrónica** - Sistemas electrónicos e IoT
6. **Ingeniería Ambiental** - Sostenibilidad

**DATOS GENERALES:**
- Duración: 10 semestres
- Costo: $12,5M - $15M/año
- Empleabilidad: 93-98%
- Laboratorios de última generación

Escribe el nombre de cualquier ingeniería para conocer detalles específicos, o pregunta sobre otra carrera."""

        elif any(word in message for word in ['inscr', 'registro', 'admisión', 'cómo ingres', 'requisito']):
            return """Para inscribirte a un pregrado en la UdeMedellín necesitas:

1. **Documentos requeridos:**
   - Diploma de bachiller
   - Documento de identidad
   - Certificados de calificaciones

2. **Proceso de admisión:**
   - Presentar pruebas de admisión (SABER 11 o similar)
   - Diligenciar formulario en www.udemedellin.edu.co
   - Pagar valor de inscripción
   - Esperar resultado (generalmente 2-3 semanas)

3. **Próximos pasos:**
   - Reservar cupo
   - Pagar matrícula
   - Asistir a inducción

¿Necesitas información sobre programas específicos?"""

        elif any(word in message for word in ['beca', 'financiación', 'apoyo económico', 'descuento']):
            return """Excelente pregunta sobre becas. La UdeMedellín ofrece:

**TIPOS DE BECAS:**
- **Mérito Académico:** Hasta 100% (según ICFES)
- **Socioeconómica:** Hasta 80% (según ingresos)
- **Deportiva:** Hasta 75% (atletas destacados)
- **Convenios:** Con empresas (variable)
- **Desempeño:** Por excelencia durante estudios

**MONTO PROMEDIO:** $8M - $15M/año

**REQUISITOS:**
- Solicitar en admisiones
- Documentación socioeconómica
- Análisis de perfil académico

Contacta: **+57 (604) 590-4500 ext. 1234**"""

        elif any(word in message for word in ['programa', 'carrera', 'pregrado', 'qué estudiar', 'facultad', 'derecho', 'administr', 'comunicación', 'diseño']):
            return """Tenemos **27 programas de pregrado** en **7 facultades**:

**FACULTAD DE INGENIERÍAS:** (6 programas)
Civil, Sistemas, Industrial, Mecánica, Electrónica, Ambiental

**FACULTAD DE DERECHO:**
Derecho (96% aprobados en examen de Estado)

**FACULTAD DE CIENCIAS ECONÓMICAS:**
Administración, Contabilidad, Economía, Mercadotecnia

**FACULTAD DE COMUNICACIÓN:**
Comunicación Social, Publicidad

**FACULTAD DE DISEÑO:**
Diseño Gráfico, Diseño Industrial

**FACULTAD DE CIENCIAS:**
Matemáticas, Física, Química

**FACULTAD DE HUMANIDADES:**
Licenciaturas, Filosofía

¿Cuál programa te interesa? Dime el nombre o la facultad."""

        elif any(word in message for word in ['campus', 'dónde', 'ubicación', 'instalación', 'infraestructur', 'aula', 'laboratorio']):
            return """¡Nuestro Campus Vivo es espectacular!

**UBICACIÓN:**
Carrera 87 N° 30-65, Laureles, Medellín
Metro: Estación Estadio (5 min)

**INFRAESTRUCTURA:**
✓ Teatro Gabriel Obregón Botero - 1,702 sillas
✓ Biblioteca Eduardo Fernández Botero - 80,000+ volúmenes
✓ Laboratorios de Última Generación
✓ Coliseo Deportivo completo
✓ Centro de Idiomas
✓ Zonas Verdes y áreas de descanso
✓ Comedor Universitario

¿Te gustaría una visita virtual?"""

        elif any(word in message for word in ['idioma', 'inglés', 'francés', 'alemán']):
            return """**CENTRO DE IDIOMAS - Primer Nivel**

**IDIOMAS:**
- Inglés (6 niveles)
- Francés (5 niveles)
- Alemán (4 niveles)
- Italiano (3 niveles)
- Chino Mandarín (3 niveles)

**CERTIFICACIONES:**
Cambridge, DELF, Goethe

**HORARIOS:**
- Matutino: 6:30am - 9:00am
- Vespertino: 5:00pm - 8:00pm
- Sabatino: 9:00am - 1:00pm

**COSTO:** $350,000 - $450,000/nivel

Información: **idiomas@udemedellin.edu.co**"""

        elif any(word in message for word in ['contact', 'teléfono', 'correo', 'dirección']):
            return """**CONTACTOS UDEMEDELLIN**

📞 **+57 (604) 590-4500**
📧 **info@udemedellin.edu.co**
📍 **Carrera 87 N° 30-65, Medellín**

**HORARIO:**
Lunes-Viernes: 8:00am - 12:00pm y 2:00pm - 6:00pm
Sábados: 9:00am - 1:00pm

**EXTENSIONES:**
- Admisiones: 1010
- Becas: 1234
- Registro: 1050
- Idiomas: 2100
- Deportes: 2200

**SEDE BOGOTÁ:**
Calle 57 # 9-52, Chapinero"""

        else:
            return """¡Hola! Soy Vivi, tu asistente virtual de la UdeMedellín.

Puedo ayudarte con:
✓ **Ingenierías** - Civil, Sistemas, Industrial, Mecánica, Electrónica, Ambiental
✓ **Admisiones** - Cómo inscribirse
✓ **Becas** - Financiación
✓ **Programas** - Todas las carreras
✓ **Campus** - Instalaciones
✓ **Idiomas** - Centro de Idiomas
✓ **Contacto** - Teléfono y dirección

¿Qué te gustaría saber?"""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    os.chdir('C:\\Users\\p20on\\Documents\\Vsproyects\\Chatbot')
    server_address = ('127.0.0.1', 9999)
    httpd = http.server.HTTPServer(server_address, ViviHandler)
    print("Vivi HTTP Server en http://localhost:9999")
    httpd.serve_forever()
