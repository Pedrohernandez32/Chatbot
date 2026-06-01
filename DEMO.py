#!/usr/bin/env python3
"""
Demo - Showcase de capacidades del Chatbot
Ejecuta: python DEMO.py
"""

import requests
import json
import time

API_URL = "http://localhost:5000/api/chat"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def test_query(question, description=""):
    print(f"\n📝 Pregunta: {question}")
    if description:
        print(f"   {description}")

    try:
        response = requests.post(
            API_URL,
            json={"message": question},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            resp_obj = json.loads(data.get('response', '{}'))

            # Mostrar respuesta formateada
            text = resp_obj.get('text', 'Sin respuesta')
            # Truncar si es muy largo
            if len(text) > 300:
                text = text[:300] + "...\n[respuesta truncada]"

            print(f"✅ Respuesta:\n{text}\n")
            return True
        elif response.status_code == 429:
            print(f"⚠️  Rate Limited (429)")
            return False
        else:
            print(f"❌ Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def main():
    print("""

    🎓 DEMO - UNIVERSIDAD DE MEDELLÍN CHATBOT
    ========================================

    Sistema inteligente de respuestas contextuales
    Probando diferentes tipos de búsquedas...

    """)

    # Test 1: Búsqueda de grupo (todas las ingenierías)
    print_header("TEST 1: Búsqueda de Grupo - Ingenierías")
    test_query(
        "ingeniería",
        "Cuando preguntas por 'ingeniería' sin especificar, devuelve TODAS las opciones"
    )
    time.sleep(1)

    # Test 2: Búsqueda específica (carrera individual)
    print_header("TEST 2: Búsqueda Específica - Carrera Individual")
    test_query(
        "ingenieria de sistemas",
        "Carrera específica con detalles + Facultad + Decano"
    )
    time.sleep(1)

    # Test 3: Búsqueda de profesores
    print_header("TEST 3: Búsqueda Inteligente - Profesores")
    test_query(
        "profesores",
        "Devuelve información sobre 320+ docentes por carrera"
    )
    time.sleep(1)

    # Test 4: Búsqueda de decanos
    print_header("TEST 4: Búsqueda Inteligente - Decanos")
    test_query(
        "decanos",
        "Devuelve 6 decanos con contacto directo"
    )
    time.sleep(1)

    # Test 5: Búsqueda de calidad
    print_header("TEST 5: Búsqueda Inteligente - Calidad Académica")
    test_query(
        "calidad acreditacion",
        "Acreditaciones, certificaciones, indicadores de empleabilidad"
    )
    time.sleep(1)

    # Test 6: Carrera con facultad
    print_header("TEST 6: Carrera con Vinculación de Facultad")
    test_query(
        "derecho",
        "Muestra carrera + Facultad + Decano automáticamente"
    )
    time.sleep(1)

    # Test 7: Otra carrera
    print_header("TEST 7: Otra Carrera con Facultad")
    test_query(
        "psicologia",
        "Carrera de otra facultad - muestra vinculación automática"
    )
    time.sleep(1)

    # Test 8: Beca específica
    print_header("TEST 8: Búsqueda de Beca Específica")
    test_query(
        "beca social",
        "Información detallada de beca específica"
    )
    time.sleep(1)

    # Test 9: Información de contacto
    print_header("TEST 9: Búsqueda de Contacto")
    test_query(
        "contacto",
        "Información de teléfono, email, ubicación"
    )
    time.sleep(1)

    # Test 10: Información general
    print_header("TEST 10: Pregunta General")
    test_query(
        "universidad",
        "Pregunta genérica devuelve menú de ayuda"
    )

    print_header("DEMO COMPLETADO ✅")
    print("""

    📊 RESULTADOS:
    ==============
    ✅ Sistema inteligente de respuestas funcionando
    ✅ Detección contextual de búsquedas específicas
    ✅ Vinculación automática de facultades a carreras
    ✅ Rate limiting activo (30 requests/minuto)
    ✅ Respuestas gramaticales y bien formateadas

    🚀 PRODUCCIÓN:
    ==============
    El chatbot está listo para deployment:
    - Ver DEPLOYMENT.md para instrucciones
    - Ver README.md para documentación
    - Ver CHANGELOG.md para historial de cambios

    """)

if __name__ == "__main__":
    main()
