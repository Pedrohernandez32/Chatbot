"""
Sistema Mejorado de Asesores Humanos - Backend Profesional
Features: WebSocket, Inteligencia artificial, Analytics, Notificaciones
"""

from datetime import datetime, timedelta
from enum import Enum
import json
from typing import Optional, Dict, List


class RequestStatus(Enum):
    """Estados posibles de una solicitud"""
    WAITING = "waiting"          # Esperando asesor
    ASSIGNED = "assigned"        # Asignado a asesor
    ACTIVE = "active"            # Chat activo
    CLOSED = "closed"            # Chat cerrado
    RATED = "rated"              # Ya fue calificado


class AdvisorStatus(Enum):
    """Estados de asesor"""
    OFFLINE = "offline"          # No disponible
    ONLINE = "online"            # Disponible
    BUSY = "busy"                # Ocupado (máx chats)
    AWAY = "away"                # Ausente temporalmente


class AssignmentStrategy:
    """Estrategia inteligente de asignación de asesores"""

    @staticmethod
    def get_best_advisor(advisors: List[Dict], request: Dict) -> Optional[Dict]:
        """
        Selecciona el mejor asesor basado en:
        - Especialidad (department)
        - Disponibilidad
        - Carga actual
        - Tasa de satisfacción
        - Tiempo promedio de respuesta
        """
        if not advisors:
            return None

        # Filtrar asesores disponibles
        available = [a for a in advisors
                    if a['status'] == 'online' and a['current_chats'] < a['max_chats']]

        if not available:
            return None

        # Puntuar asesores
        scores = {}
        for advisor in available:
            score = 0

            # Factor 1: Especialidad coincide (40%)
            if advisor.get('department', '').lower() in request.get('topic', '').lower():
                score += 40

            # Factor 2: Menos ocupado (30%)
            occupancy = advisor['current_chats'] / advisor['max_chats']
            score += 30 * (1 - occupancy)

            # Factor 3: Mejor calificación (20%)
            rating = advisor.get('avg_rating', 4.0)
            score += (rating / 5.0) * 20

            # Factor 4: Tiempo de respuesta más rápido (10%)
            avg_response_time = advisor.get('avg_response_time_seconds', 30)
            score += 10 * max(0, (60 - avg_response_time) / 60)

            scores[advisor['id']] = score

        # Devolver el mejor
        best_id = max(scores, key=scores.get)
        return next(a for a in available if a['id'] == best_id)


class AdvancedAnalytics:
    """Análisis y métricas del sistema"""

    @staticmethod
    def calculate_advisor_metrics(advisor_id: int, messages: List[Dict],
                                  requests: List[Dict]) -> Dict:
        """Calcula métricas completas de un asesor"""

        advisor_requests = [r for r in requests if r['assigned_to'] == advisor_id]
        closed_requests = [r for r in advisor_requests if r['status'] == 'closed']

        metrics = {
            'total_requests': len(advisor_requests),
            'closed_requests': len(closed_requests),
            'active_requests': len([r for r in advisor_requests if r['status'] == 'active']),
            'avg_rating': 0.0,
            'total_messages': 0,
            'avg_response_time_seconds': 0,
            'avg_resolution_time_minutes': 0,
            'customer_satisfaction': 0.0,
            'messages_per_request': 0,
            'performance_score': 0.0
        }

        if closed_requests:
            # Calificación promedio
            ratings = [r.get('rating', 0) for r in closed_requests if r.get('rating')]
            metrics['avg_rating'] = sum(ratings) / len(ratings) if ratings else 0

            # Tiempo promedio de resolución
            resolution_times = []
            for req in closed_requests:
                if req.get('created_at') and req.get('resolved_at'):
                    try:
                        start = datetime.fromisoformat(req['created_at'])
                        end = datetime.fromisoformat(req['resolved_at'])
                        minutes = (end - start).total_seconds() / 60
                        resolution_times.append(minutes)
                    except:
                        pass

            if resolution_times:
                metrics['avg_resolution_time_minutes'] = sum(resolution_times) / len(resolution_times)

        # Mensajes del asesor
        advisor_messages = [m for m in messages if m['sender_id'] == advisor_id and m['sender_type'] == 'advisor']
        metrics['total_messages'] = len(advisor_messages)

        if advisor_requests:
            metrics['messages_per_request'] = metrics['total_messages'] / len(advisor_requests)

        # Score de rendimiento (0-100)
        performance = 0
        performance += metrics['avg_rating'] * 20  # 20%
        performance += min(100, metrics['messages_per_request'] * 10) * 0.1  # 10%
        performance += (100 - min(100, metrics['avg_resolution_time_minutes'])) * 0.3  # 30%
        performance += (closed_requests / max(1, advisor_requests)) * 100 * 0.4  # 40%

        metrics['performance_score'] = min(100, max(0, performance))

        return metrics


    @staticmethod
    def get_system_analytics(requests: List[Dict], messages: List[Dict],
                            advisors: List[Dict]) -> Dict:
        """Obtiene análisis del sistema completo"""

        closed = [r for r in requests if r['status'] == 'closed']

        analytics = {
            'total_requests': len(requests),
            'closed_requests': len(closed),
            'avg_resolution_time_minutes': 0,
            'avg_wait_time_minutes': 0,
            'customer_satisfaction_avg': 0,
            'total_messages': len(messages),
            'advisors_online': len([a for a in advisors if a['status'] == 'online']),
            'advisors_total': len(advisors),
            'busiest_hour': None,
            'most_common_topic': None,
            'requests_by_status': {},
            'peak_hours': []
        }

        # Por status
        for status in RequestStatus:
            count = len([r for r in requests if r['status'] == status.value])
            analytics['requests_by_status'][status.value] = count

        # Tiempo de resolución
        resolution_times = []
        wait_times = []
        for req in closed:
            try:
                if req.get('created_at') and req.get('resolved_at'):
                    start = datetime.fromisoformat(req['created_at'])
                    end = datetime.fromisoformat(req['resolved_at'])
                    resolution_times.append((end - start).total_seconds() / 60)

                if req.get('created_at') and req.get('assigned_at'):
                    start = datetime.fromisoformat(req['created_at'])
                    assigned = datetime.fromisoformat(req['assigned_at'])
                    wait_times.append((assigned - start).total_seconds() / 60)
            except:
                pass

        if resolution_times:
            analytics['avg_resolution_time_minutes'] = sum(resolution_times) / len(resolution_times)

        if wait_times:
            analytics['avg_wait_time_minutes'] = sum(wait_times) / len(wait_times)

        # Satisfacción
        ratings = [r.get('rating', 0) for r in closed if r.get('rating')]
        if ratings:
            analytics['customer_satisfaction_avg'] = sum(ratings) / len(ratings)

        # Tema más común
        topics = [r.get('topic', 'Otra') for r in requests]
        if topics:
            analytics['most_common_topic'] = max(set(topics), key=topics.count)

        return analytics


class NotificationManager:
    """Gestiona notificaciones en tiempo real"""

    def __init__(self):
        self.subscribers = {}  # {user_id: [callback, ...]}

    def subscribe(self, user_id: int, callback):
        """Suscribir usuario a notificaciones"""
        if user_id not in self.subscribers:
            self.subscribers[user_id] = []
        self.subscribers[user_id].append(callback)

    def notify_new_request(self, request: Dict, advisors: List[Dict]):
        """Notificar a asesores sobre nueva solicitud"""
        for advisor in advisors:
            if advisor['status'] == 'online':
                message = {
                    'type': 'new_request',
                    'request_id': request['id'],
                    'topic': request['topic'],
                    'timestamp': datetime.now().isoformat()
                }
                self._send_to_user(advisor['user_id'], message)

    def notify_message_received(self, request_id: int, sender_name: str,
                               message_preview: str, recipient_id: int):
        """Notificar nuevo mensaje"""
        message = {
            'type': 'new_message',
            'request_id': request_id,
            'from': sender_name,
            'preview': message_preview[:100],
            'timestamp': datetime.now().isoformat()
        }
        self._send_to_user(recipient_id, message)

    def notify_advisor_assigned(self, request_id: int, advisor_name: str,
                               user_id: int):
        """Notificar usuario que se le asignó asesor"""
        message = {
            'type': 'advisor_assigned',
            'request_id': request_id,
            'advisor_name': advisor_name,
            'timestamp': datetime.now().isoformat()
        }
        self._send_to_user(user_id, message)

    def notify_waiting_users(self, wait_time_minutes: int, position: int,
                            advisors_available: int):
        """Notificar a usuarios en espera sobre su posición"""
        message = {
            'type': 'wait_update',
            'position': position,
            'estimated_wait_minutes': wait_time_minutes,
            'advisors_available': advisors_available,
            'timestamp': datetime.now().isoformat()
        }
        return message

    def _send_to_user(self, user_id: int, message: Dict):
        """Enviar notificación a usuario"""
        if user_id in self.subscribers:
            for callback in self.subscribers[user_id]:
                try:
                    callback(message)
                except Exception as e:
                    print(f"Error enviando notificación: {e}")


class ValidationEngine:
    """Validaciones robustas"""

    @staticmethod
    def validate_request(data: Dict) -> tuple[bool, str]:
        """Validar solicitud de asesor"""

        if not data.get('name', '').strip():
            return False, "Nombre requerido"

        if not data.get('email', '').strip():
            return False, "Email requerido"

        if not self._is_valid_email(data['email']):
            return False, "Email inválido"

        if 'phone' in data and data['phone']:
            if not self._is_valid_phone(data['phone']):
                return False, "Teléfono inválido"

        if not data.get('topic', '').strip():
            return False, "Tema requerido"

        valid_topics = ['Becas', 'Admisiones', 'Campus', 'Horarios', 'Otra consulta']
        if data['topic'] not in valid_topics:
            return False, f"Tema inválido. Válidos: {', '.join(valid_topics)}"

        return True, "OK"

    @staticmethod
    def validate_message(message: str) -> tuple[bool, str]:
        """Validar mensaje"""

        if not message:
            return False, "Mensaje vacío"

        if len(message) > 5000:
            return False, "Mensaje demasiado largo (máx 5000 caracteres)"

        if len(message.strip()) < 1:
            return False, "Mensaje solo contiene espacios"

        return True, "OK"

    @staticmethod
    def validate_rating(rating: int) -> tuple[bool, str]:
        """Validar calificación"""

        if not isinstance(rating, int):
            return False, "Rating debe ser número entero"

        if rating < 1 or rating > 5:
            return False, "Rating debe estar entre 1 y 5"

        return True, "OK"

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validar formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        """Validar formato de teléfono"""
        import re
        # Acepta formatos: +57 300 1234567, 3001234567, +573001234567
        pattern = r'^(\+\d{1,3})?[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4}$'
        return re.match(pattern, phone.replace(' ', '')) is not None


# Instancia global del gestor de notificaciones
notification_manager = NotificationManager()
