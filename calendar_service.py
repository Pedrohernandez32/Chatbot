"""
Sistema de Calendario y Agendamiento de Citas
Permite a usuarios agendar citas con asesores específicos
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json

class TimeSlot(Enum):
    """Franjas horarias disponibles"""
    MORNING_1 = "08:00-09:00"
    MORNING_2 = "09:00-10:00"
    MORNING_3 = "10:00-11:00"
    LATE_MORNING = "11:00-12:00"
    AFTERNOON_1 = "14:00-15:00"
    AFTERNOON_2 = "15:00-16:00"
    AFTERNOON_3 = "16:00-17:00"
    EVENING_1 = "18:00-19:00"
    EVENING_2 = "19:00-20:00"

class CalendarService:
    """Servicio de calendario y agendamiento"""

    # Simular base de datos de citas
    appointments = {}  # {appointment_id: appointment_data}
    advisor_schedules = {}  # {advisor_id: {date: [available_slots]}}

    @staticmethod
    def get_advisor_availability(
        advisor_id: int,
        days_ahead: int = 7
    ) -> Dict:
        """
        Obtener disponibilidad de un asesor

        Returns:
            Diccionario con días y franjas disponibles
        """
        try:
            availability = {}

            for day_offset in range(1, days_ahead + 1):
                date = datetime.now() + timedelta(days=day_offset)

                # Saltar fines de semana
                if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                    continue

                date_str = date.strftime("%Y-%m-%d")

                # Simular disponibilidad (en producción, consultar BD)
                available_slots = [
                    slot.value for slot in TimeSlot
                    if CalendarService._is_slot_available(advisor_id, date, slot)
                ]

                if available_slots:
                    availability[date_str] = {
                        "date": date_str,
                        "day": date.strftime("%A"),
                        "available_slots": available_slots,
                        "total_available": len(available_slots)
                    }

            return {
                "success": True,
                "advisor_id": advisor_id,
                "availability": availability,
                "total_days": len(availability)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def schedule_appointment(
        advisor_id: int,
        user_id: int,
        user_name: str,
        user_email: str,
        date: str,  # YYYY-MM-DD
        time_slot: str,  # HH:MM-HH:MM
        topic: str,
        notes: str = None
    ) -> Dict:
        """
        Agendar cita con asesor

        Args:
            advisor_id: ID del asesor
            user_id: ID del usuario
            user_name: Nombre del usuario
            user_email: Email del usuario
            date: Fecha (YYYY-MM-DD)
            time_slot: Franja horaria (HH:MM-HH:MM)
            topic: Tema de la cita
            notes: Notas adicionales
        """
        try:
            # Validar disponibilidad
            if not CalendarService._is_slot_available_for_date(
                advisor_id, date, time_slot
            ):
                return {
                    "success": False,
                    "error": "This time slot is no longer available"
                }

            appointment_id = f"apt-{datetime.now().timestamp()}"

            appointment = {
                "id": appointment_id,
                "advisor_id": advisor_id,
                "user_id": user_id,
                "user_name": user_name,
                "user_email": user_email,
                "date": date,
                "time_slot": time_slot,
                "topic": topic,
                "notes": notes,
                "status": "confirmed",
                "created_at": datetime.now().isoformat(),
                "reminder_sent": False,
                "meeting_link": None  # Se genera cuando comienza
            }

            CalendarService.appointments[appointment_id] = appointment

            # Generar Google Meet link
            appointment["meeting_link"] = CalendarService._generate_meet_link(
                appointment_id
            )

            # Enviar confirmación por email
            CalendarService._send_confirmation_email(appointment)

            # Agendar recordatorio
            CalendarService._schedule_reminder(appointment_id)

            return {
                "success": True,
                "appointment": appointment,
                "message": f"Cita agendada para {date} en {time_slot}",
                "confirmation_sent": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_user_appointments(user_id: int) -> Dict:
        """Obtener citas de un usuario"""
        try:
            user_appointments = [
                apt for apt in CalendarService.appointments.values()
                if apt["user_id"] == user_id
            ]

            # Ordenar por fecha
            user_appointments.sort(key=lambda x: x["date"])

            return {
                "success": True,
                "user_id": user_id,
                "appointments": user_appointments,
                "total": len(user_appointments)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_advisor_appointments(advisor_id: int, date: str = None) -> Dict:
        """Obtener citas agendadas con un asesor"""
        try:
            advisor_appointments = [
                apt for apt in CalendarService.appointments.values()
                if apt["advisor_id"] == advisor_id
            ]

            if date:
                advisor_appointments = [
                    apt for apt in advisor_appointments
                    if apt["date"] == date
                ]

            advisor_appointments.sort(key=lambda x: x["time_slot"])

            return {
                "success": True,
                "advisor_id": advisor_id,
                "date": date,
                "appointments": advisor_appointments,
                "total": len(advisor_appointments)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def cancel_appointment(appointment_id: str, reason: str = None) -> Dict:
        """Cancelar una cita agendada"""
        try:
            if appointment_id not in CalendarService.appointments:
                return {
                    "success": False,
                    "error": "Appointment not found"
                }

            appointment = CalendarService.appointments[appointment_id]

            # Cambiar estado
            appointment["status"] = "cancelled"
            appointment["cancellation_reason"] = reason
            appointment["cancelled_at"] = datetime.now().isoformat()

            # Notificar al asesor y usuario
            CalendarService._notify_cancellation(appointment)

            return {
                "success": True,
                "appointment_id": appointment_id,
                "message": "Appointment cancelled successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def reschedule_appointment(
        appointment_id: str,
        new_date: str,
        new_time_slot: str
    ) -> Dict:
        """Reprogramar una cita a otra fecha/hora"""
        try:
            if appointment_id not in CalendarService.appointments:
                return {
                    "success": False,
                    "error": "Appointment not found"
                }

            appointment = CalendarService.appointments[appointment_id]

            # Validar nueva disponibilidad
            if not CalendarService._is_slot_available_for_date(
                appointment["advisor_id"], new_date, new_time_slot
            ):
                return {
                    "success": False,
                    "error": "New time slot is not available"
                }

            # Actualizar
            old_date = appointment["date"]
            old_time = appointment["time_slot"]

            appointment["date"] = new_date
            appointment["time_slot"] = new_time_slot
            appointment["rescheduled_at"] = datetime.now().isoformat()
            appointment["previous_date"] = old_date
            appointment["previous_time"] = old_time

            # Notificar
            CalendarService._send_rescheduled_email(appointment)

            return {
                "success": True,
                "appointment": appointment,
                "message": f"Cita reprogramada para {new_date} en {new_time_slot}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def check_reminders() -> List[str]:
        """
        Verificar citas que necesitan recordatorio (15 minutos antes)
        Se ejecuta cada minuto desde el servidor
        """
        reminders_sent = []

        try:
            now = datetime.now()

            for apt_id, apt in CalendarService.appointments.items():
                if apt["reminder_sent"] or apt["status"] != "confirmed":
                    continue

                # Parsear fecha y hora
                apt_datetime = datetime.strptime(
                    f"{apt['date']} {apt['time_slot'][:5]}",
                    "%Y-%m-%d %H:%M"
                )

                # Si falta 15 minutos, enviar recordatorio
                time_until = (apt_datetime - now).total_seconds() / 60

                if 14 <= time_until <= 16:
                    CalendarService._send_reminder(apt)
                    apt["reminder_sent"] = True
                    reminders_sent.append(apt_id)

        except Exception as e:
            print(f"❌ Error checking reminders: {e}")

        return reminders_sent

    # Métodos privados auxiliares
    @staticmethod
    def _is_slot_available(advisor_id: int, date: datetime, slot: TimeSlot) -> bool:
        """Verificar si una franja está disponible"""
        # Simular: todos los slots están disponibles excepto algunos
        if date.day % 3 == 0:  # Cada tercer día, algunos slots ocupados
            return slot != TimeSlot.MORNING_1
        return True

    @staticmethod
    def _is_slot_available_for_date(advisor_id: int, date: str, time_slot: str) -> bool:
        """Verificar disponibilidad para una fecha específica"""
        # Verificar que no haya otra cita en esa hora
        for apt in CalendarService.appointments.values():
            if (apt["advisor_id"] == advisor_id and
                apt["date"] == date and
                apt["time_slot"] == time_slot and
                apt["status"] != "cancelled"):
                return False
        return True

    @staticmethod
    def _generate_meet_link(appointment_id: str) -> str:
        """Generar link de Google Meet"""
        return f"https://meet.google.com/ude-{appointment_id}"

    @staticmethod
    def _send_confirmation_email(appointment: Dict):
        """Enviar email de confirmación"""
        print(f"📧 Confirmation email sent to {appointment['user_email']}")

    @staticmethod
    def _send_rescheduled_email(appointment: Dict):
        """Enviar email de reprogramación"""
        print(f"📧 Rescheduled email sent to {appointment['user_email']}")

    @staticmethod
    def _send_reminder(appointment: Dict):
        """Enviar recordatorio de cita próxima"""
        print(f"🔔 Reminder sent for appointment {appointment['id']}")

    @staticmethod
    def _schedule_reminder(appointment_id: str):
        """Agendar recordatorio"""
        print(f"⏰ Reminder scheduled for appointment {appointment_id}")

    @staticmethod
    def _notify_cancellation(appointment: Dict):
        """Notificar cancelación"""
        print(f"📭 Cancellation notification sent for {appointment['id']}")


# Instancia global
calendar_service = CalendarService()
