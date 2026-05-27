from typing import Dict, Any, Optional

# Mock data to simulate a real university database
STUDENTS = {
    "12345": {
        "name": "Juan Pérez",
        "career": "Ingeniería de Sistemas",
        "status": "Activo",
        "semester": 5,
        "email": "juan.perez@udem.edu.co"
    },
    "67890": {
        "name": "María García",
        "career": "Psicología",
        "status": "Activo",
        "semester": 3,
        "email": "maria.garcia@udem.edu.co"
    }
}

COURSES = {
    "CS101": {
        "name": "Introducción a la Programación",
        "schedule": "Lunes y Miércoles 08:00 - 10:00",
        "room": "AULA-201",
        "professor": "Dr. Alan Turing"
    },
    "PSY202": {
        "name": "Psicología Cognitiva",
        "schedule": "Martes y Jueves 14:00 - 16:00",
        "room": "AULA-105",
        "professor": "Dra. Sigmond Freud"
    }
}

ROOMS = {
    "AULA-201": {"available": True, "capacity": 40, "type": "Lab"},
    "AULA-105": {"available": False, "capacity": 30, "type": "Theory"},
}

def get_student_info(student_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene información detallada de un estudiante por su ID."""
    print(f"[MockAPI] Consultando info de estudiante: {student_id}")
    return STUDENTS.get(student_id)

def get_course_schedule(course_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene el horario y detalles de un curso por su código."""
    print(f"[MockAPI] Consultando horario de curso: {course_id}")
    return COURSES.get(course_id)

def check_room_availability(room_id: str) -> Optional[Dict[str, Any]]:
    """Verifica si un aula está disponible."""
    print(f"[MockAPI] Consultando disponibilidad de aula: {room_id}")
    return ROOMS.get(room_id)
