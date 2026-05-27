import json
import os
from typing import Optional, List, Dict, Any
from openai import OpenAI
import mock_api

# Tool definitions for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_student_info",
            "description": "Obtiene información detallada de un estudiante usando su ID (ej. 12345).",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "El ID del estudiante."}
                },
                "required": ["student_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_schedule",
            "description": "Obtiene el horario y detalles de un curso usando su código (ej. CS101).",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {"type": "string", "description": "El código del curso."}
                },
                "required": ["course_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_room_availability",
            "description": "Verifica si un aula está disponible usando su ID (ej. AULA-201).",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_id": {"type": "string", "description": "El ID del aula."}
                },
                "required": ["room_id"]
            }
        }
    }
]

# Map function names to actual Python functions
FUNCTION_MAP = {
    "get_student_info": mock_api.get_student_info,
    "get_course_schedule": mock_api.get_course_schedule,
    "check_room_availability": mock_api.check_room_availability,
}

def tool_handler(prompt: str) -> Optional[str]:
    """
    Handler que decide si el usuario necesita una herramienta de la API.
    Si es así, ejecuta la herramienta y retorna la respuesta final del LLM.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None # No API key, cannot use tool calling reliably via OpenAI

    client = OpenAI(api_key=api_key)

    # 1. Primera llamada al LLM para ver si quiere usar una herramienta
    messages = [
        {"role": "system", "content": "Eres un asistente universitario. Usa las herramientas proporcionadas para responder preguntas sobre estudiantes, cursos y aulas. Si la pregunta es general, responde normalmente. Si necesitas datos específicos, usa una herramienta."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Si el LLM no quiso usar herramientas, devolvemos None para que otros handlers lo intenten
    # (o podríamos devolver la respuesta si queremos que el tool_plugin sea el fallback general,
    # pero según el plan, queremos que sea la prioridad más alta SOLO para acciones).
    if not tool_calls:
        # Para evitar que el tool_plugin robe todas las respuestas generales,
        # solo devolvemos la respuesta si el LLM está muy seguro de que es una respuesta final
        # sin herramientas. Pero el diseño de "Chain of Responsibility" sugiere devolver None
        # si no hay una "acción" clara.
        return None

    # 2. Ejecutar las herramientas solicitadas
    messages.append(response_message)

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        function_to_call = FUNCTION_MAP.get(function_name)
        if function_to_call:
            # Llamamos a la función del mock_api con los argumentos
            # Nota: asumiendo que la función acepta un solo argumento basado en el schema
            arg_key = list(function_args.keys())[0]
            result = function_to_call(function_args[arg_key])

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result, ensure_ascii=False)
            })

    # 3. Segunda llamada al LLM para sintetizar la respuesta final con los datos de la API
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    return final_response.choices[0].message.content

def register(bot) -> None:
    """Registra el manejador de herramientas en el chatbot."""
    bot.register_handler(tool_handler)
