"""
Rutas para todas las integraciones:
- Notificaciones Push
- Google Meet
- WhatsApp
- Calendario y Agendamiento
"""

from flask import request, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from notification_service import notification_service
from google_meet_integration import google_meet
from whatsapp_integration import whatsapp
from calendar_service import calendar_service
from database import get_user_by_id, get_advisor_request

def register_integration_routes(app):
    """Registrar todas las rutas de integraciones"""

    # ==================== NOTIFICACIONES PUSH ====================

    @app.route('/api/notifications/subscribe', methods=['POST'])
    def subscribe_notifications():
        """Subscribirse a notificaciones push"""
        try:
            data = request.get_json()
            user_id = current_user.id if current_user.is_authenticated else data.get('user_id')

            if not user_id:
                return jsonify({'error': 'user_id required'}), 400

            subscription = data.get('subscription')
            success = notification_service.subscribe(user_id, subscription)

            return jsonify({
                'success': success,
                'message': 'Subscribed to notifications',
                'user_id': user_id
            }), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/notifications/unsubscribe', methods=['POST'])
    @login_required
    def unsubscribe_notifications():
        """Desuscribirse de notificaciones push"""
        try:
            success = notification_service.unsubscribe(current_user.id)

            return jsonify({
                'success': success,
                'message': 'Unsubscribed from notifications'
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/notifications/stats', methods=['GET'])
    @login_required
    def get_notification_stats():
        """Obtener estadísticas de notificaciones"""
        try:
            user_data = get_user_by_id(current_user.id)
            if not user_data or not user_data.get('is_admin'):
                return jsonify({'error': 'Admin access required'}), 403

            stats = notification_service.get_notification_stats()

            return jsonify({
                'success': True,
                'stats': stats
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # ==================== GOOGLE MEET ====================

    @app.route('/api/videocall/create', methods=['POST'])
    def create_videocall():
        """Crear videollamada de Google Meet"""
        try:
            data = request.get_json()

            meeting = google_meet.create_meeting(
                title=data.get('title'),
                description=data.get('description'),
                start_time=datetime.fromisoformat(data.get('start_time')),
                duration_minutes=data.get('duration_minutes', 30),
                participants=data.get('participants', [])
            )

            if meeting['success']:
                # Enviar invitación
                for participant in data.get('participants', []):
                    google_meet.send_meeting_invite(
                        meeting['meeting']['id'],
                        participant.get('email'),
                        participant.get('name')
                    )

            return jsonify(meeting), 201

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/videocall/<meeting_id>', methods=['GET'])
    def get_videocall(meeting_id):
        """Obtener detalles de videollamada"""
        try:
            meeting = google_meet.get_meeting_details(meeting_id)
            return jsonify(meeting), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/videocall/<meeting_id>/end', methods=['POST'])
    def end_videocall(meeting_id):
        """Finalizar videollamada"""
        try:
            result = google_meet.end_meeting(meeting_id)
            return jsonify(result), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/videocall/<meeting_id>/record', methods=['POST'])
    def record_videocall(meeting_id):
        """Activar grabación"""
        try:
            result = google_meet.record_meeting(meeting_id)
            return jsonify(result), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    # ==================== WHATSAPP ====================

    @app.route('/api/whatsapp/send', methods=['POST'])
    def send_whatsapp():
        """Enviar mensaje por WhatsApp"""
        try:
            data = request.get_json()

            result = whatsapp.send_message(
                to_phone=data.get('phone'),
                message_text=data.get('message'),
                message_type=data.get('type', 'text')
            )

            return jsonify(result), 201

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/whatsapp/webhook', methods=['POST'])
    def whatsapp_webhook():
        """Webhook para recibir mensajes de WhatsApp"""
        try:
            data = request.get_json()
            result = whatsapp.process_webhook_event(data)
            return jsonify(result), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/whatsapp/qr', methods=['GET'])
    def get_whatsapp_qr():
        """Obtener link para conectar por WhatsApp"""
        try:
            link = whatsapp.create_whatsapp_request_link()

            return jsonify({
                'success': True,
                'whatsapp_link': link,
                'message': 'Click para chatear por WhatsApp'
            }), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    # ==================== CALENDARIO Y AGENDAMIENTO ====================

    @app.route('/api/calendar/availability/<int:advisor_id>', methods=['GET'])
    def get_availability(advisor_id):
        """Obtener disponibilidad de asesor"""
        try:
            days = request.args.get('days', 7, type=int)

            availability = calendar_service.get_advisor_availability(
                advisor_id=advisor_id,
                days_ahead=days
            )

            return jsonify(availability), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/calendar/appointment', methods=['POST'])
    def schedule_appointment():
        """Agendar cita con asesor"""
        try:
            data = request.get_json()

            user_id = current_user.id if current_user.is_authenticated else None

            appointment = calendar_service.schedule_appointment(
                advisor_id=data.get('advisor_id'),
                user_id=user_id,
                user_name=data.get('name'),
                user_email=data.get('email'),
                date=data.get('date'),
                time_slot=data.get('time_slot'),
                topic=data.get('topic'),
                notes=data.get('notes')
            )

            return jsonify(appointment), 201

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/calendar/appointments', methods=['GET'])
    def get_user_appointments():
        """Obtener citas del usuario"""
        try:
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401

            appointments = calendar_service.get_user_appointments(
                current_user.id
            )

            return jsonify(appointments), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/calendar/advisor/<int:advisor_id>/appointments', methods=['GET'])
    @login_required
    def get_advisor_appointments(advisor_id):
        """Obtener citas de un asesor"""
        try:
            user_data = get_user_by_id(current_user.id)
            if not user_data or not user_data.get('is_admin'):
                return jsonify({'error': 'Admin access required'}), 403

            date = request.args.get('date')

            appointments = calendar_service.get_advisor_appointments(
                advisor_id=advisor_id,
                date=date
            )

            return jsonify(appointments), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/calendar/appointment/<appointment_id>/cancel', methods=['POST'])
    def cancel_appointment(appointment_id):
        """Cancelar cita"""
        try:
            data = request.get_json()

            result = calendar_service.cancel_appointment(
                appointment_id=appointment_id,
                reason=data.get('reason')
            )

            return jsonify(result), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/calendar/appointment/<appointment_id>/reschedule', methods=['POST'])
    def reschedule_appointment(appointment_id):
        """Reprogramar cita"""
        try:
            data = request.get_json()

            result = calendar_service.reschedule_appointment(
                appointment_id=appointment_id,
                new_date=data.get('date'),
                new_time_slot=data.get('time_slot')
            )

            return jsonify(result), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/calendar/reminders/check', methods=['POST'])
    def check_reminders():
        """Verificar y enviar recordatorios (ejecutar cada minuto)"""
        try:
            # Este endpoint debería ser llamado por un cron job cada minuto
            reminders_sent = calendar_service.check_reminders()

            return jsonify({
                'success': True,
                'reminders_sent': reminders_sent,
                'count': len(reminders_sent)
            }), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    # ==================== ENDPOINT DE PRUEBA ====================

    @app.route('/api/integrations/status', methods=['GET'])
    def integration_status():
        """Estado de todas las integraciones"""
        try:
            pwa_manager = {}
            if 'PWAManager' in dir():
                pwa_manager = {'initialized': True}

            return jsonify({
                'success': True,
                'integrations': {
                    'notifications': {'status': 'active'},
                    'google_meet': {'status': 'active'},
                    'whatsapp': {'status': 'configured'},
                    'calendar': {'status': 'active'},
                    'pwa': pwa_manager
                },
                'timestamp': datetime.now().isoformat()
            }), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
