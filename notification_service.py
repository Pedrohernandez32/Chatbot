"""
Sistema de Notificaciones Push para Navegador
Maneja notificaciones en tiempo real para usuarios y asesores
"""

from datetime import datetime
from typing import Dict, List, Optional
import json

class NotificationService:
    """Servicio centralizado de notificaciones"""

    # Almacenar subscripciones de usuarios
    subscriptions = {}  # {user_id: [subscription_objects]}

    # Plantillas de notificaciones
    NOTIFICATION_TEMPLATES = {
        "advisor_assigned": {
            "title": "✅ Asesor Asignado",
            "template": "¡{advisor_name} ha sido asignado a tu solicitud! Responderá en breve.",
            "icon": "👨‍💼",
            "tag": "advisor_assigned"
        },
        "new_message": {
            "title": "💬 Nuevo Mensaje",
            "template": "{sender_name}: {message_preview}...",
            "icon": "💬",
            "tag": "new_message"
        },
        "queue_position": {
            "title": "⏳ Actualización de Cola",
            "template": "Tu posición en la cola: #{position} | Tiempo estimado: {wait_time} min",
            "icon": "⏳",
            "tag": "queue_position"
        },
        "request_closed": {
            "title": "✔️ Solicitud Cerrada",
            "template": "Tu consulta ha sido resuelta. ¿Nos das una calificación?",
            "icon": "⭐",
            "tag": "request_closed"
        },
        "advisor_online": {
            "title": "🟢 Asesor en Línea",
            "template": "{advisor_name} está en línea. ¡Solicita ayuda ahora!",
            "icon": "🟢",
            "tag": "advisor_online"
        },
        "new_request": {
            "title": "🔔 Nueva Solicitud",
            "template": "{user_name} necesita ayuda con {topic}",
            "icon": "🔔",
            "tag": "new_request"
        },
        "appointment_reminder": {
            "title": "📅 Recordatorio de Cita",
            "template": "Tu cita con {advisor_name} es en {time_remaining} minutos",
            "icon": "📅",
            "tag": "appointment_reminder"
        },
        "message_received": {
            "title": "📬 Mensaje Recibido",
            "template": "Tienes un nuevo mensaje de {sender_name}",
            "icon": "📬",
            "tag": "message_received"
        }
    }

    @staticmethod
    def subscribe(user_id: int, subscription: Dict) -> bool:
        """Registrar subscripción de usuario para notificaciones push"""
        try:
            if user_id not in NotificationService.subscriptions:
                NotificationService.subscriptions[user_id] = []

            # Evitar duplicados
            if subscription not in NotificationService.subscriptions[user_id]:
                NotificationService.subscriptions[user_id].append(subscription)

            print(f"✅ Subscripción registrada para usuario {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error al registrar subscripción: {e}")
            return False

    @staticmethod
    def unsubscribe(user_id: int) -> bool:
        """Desuscribir usuario"""
        try:
            if user_id in NotificationService.subscriptions:
                del NotificationService.subscriptions[user_id]
                print(f"✅ Subscripción eliminada para usuario {user_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error al desuscribir: {e}")
            return False

    @staticmethod
    def send_notification(
        user_id: int,
        notification_type: str,
        **kwargs
    ) -> Dict:
        """
        Enviar notificación a usuario

        Args:
            user_id: ID del usuario
            notification_type: Tipo de notificación (advisor_assigned, new_message, etc)
            **kwargs: Variables para rellenar plantilla (advisor_name, message_preview, etc)
        """
        if notification_type not in NotificationService.NOTIFICATION_TEMPLATES:
            return {"success": False, "error": "Tipo de notificación no válida"}

        template = NotificationService.NOTIFICATION_TEMPLATES[notification_type]

        try:
            # Rellenar plantilla
            body = template["template"].format(**kwargs)

            notification = {
                "id": f"{user_id}_{datetime.now().timestamp()}",
                "title": template["title"],
                "body": body,
                "icon": template["icon"],
                "tag": template["tag"],
                "badge": "https://udemedellin.edu.co/badge.png",
                "timestamp": datetime.now().isoformat(),
                "type": notification_type,
                "data": {
                    "url": kwargs.get("url", "/"),
                    "request_id": kwargs.get("request_id"),
                    "user_id": user_id
                }
            }

            # En aplicación real, aquí se enviaría a Web Push API
            print(f"🔔 Notificación enviada a usuario {user_id}: {notification['title']}")

            return {
                "success": True,
                "notification": notification
            }

        except KeyError as e:
            return {
                "success": False,
                "error": f"Variable faltante en plantilla: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def notify_advisor_assigned(user_id: int, advisor_name: str, request_id: int) -> Dict:
        """Notificar que un asesor fue asignado"""
        return NotificationService.send_notification(
            user_id,
            "advisor_assigned",
            advisor_name=advisor_name,
            request_id=request_id,
            url=f"/solicitudes/{request_id}"
        )

    @staticmethod
    def notify_new_message(
        user_id: int,
        sender_name: str,
        message_preview: str,
        request_id: int
    ) -> Dict:
        """Notificar nuevo mensaje"""
        return NotificationService.send_notification(
            user_id,
            "new_message",
            sender_name=sender_name,
            message_preview=message_preview[:50],  # Primeros 50 caracteres
            request_id=request_id,
            url=f"/chat/{request_id}"
        )

    @staticmethod
    def notify_queue_update(
        user_id: int,
        position: int,
        wait_time: int
    ) -> Dict:
        """Notificar actualización de posición en cola"""
        return NotificationService.send_notification(
            user_id,
            "queue_position",
            position=position,
            wait_time=wait_time
        )

    @staticmethod
    def notify_request_closed(user_id: int, request_id: int) -> Dict:
        """Notificar que solicitud fue cerrada"""
        return NotificationService.send_notification(
            user_id,
            "request_closed",
            request_id=request_id,
            url=f"/calificar/{request_id}"
        )

    @staticmethod
    def notify_advisor_online(user_id: int, advisor_name: str) -> Dict:
        """Notificar que asesor está en línea"""
        return NotificationService.send_notification(
            user_id,
            "advisor_online",
            advisor_name=advisor_name
        )

    @staticmethod
    def notify_new_request(advisor_id: int, user_name: str, topic: str, request_id: int) -> Dict:
        """Notificar asesor sobre nueva solicitud"""
        return NotificationService.send_notification(
            advisor_id,
            "new_request",
            user_name=user_name,
            topic=topic,
            request_id=request_id,
            url=f"/solicitudes/{request_id}"
        )

    @staticmethod
    def notify_appointment_reminder(
        user_id: int,
        advisor_name: str,
        time_remaining: int
    ) -> Dict:
        """Recordatorio de cita (15 minutos antes)"""
        return NotificationService.send_notification(
            user_id,
            "appointment_reminder",
            advisor_name=advisor_name,
            time_remaining=time_remaining
        )

    @staticmethod
    def get_notification_stats() -> Dict:
        """Obtener estadísticas de notificaciones"""
        total_subscriptions = sum(
            len(subs) for subs in NotificationService.subscriptions.values()
        )

        return {
            "total_users": len(NotificationService.subscriptions),
            "total_subscriptions": total_subscriptions,
            "timestamp": datetime.now().isoformat()
        }


# Instancia global
notification_service = NotificationService()
