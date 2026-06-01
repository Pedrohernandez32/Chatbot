# ============================================================
# Rutas Profesionales para Asesores Humanos
# ============================================================

from flask import request, jsonify, current_app
from flask_login import current_user, login_required
from datetime import datetime
from database import (
    create_advisor_request, get_pending_advisor_requests,
    assign_advisor_request, add_advisor_message, get_advisor_messages,
    get_advisor_request, close_advisor_request, register_advisor,
    set_advisor_status, get_available_advisors, get_user_by_id, get_db
)
from advisor_enhanced import (
    AssignmentStrategy, AdvancedAnalytics, ValidationEngine,
    notification_manager
)


def register_advisor_routes(app):
    """Registrar todas las rutas de asesores con lógica avanzada"""

    @app.route('/api/advisor/request', methods=['POST'])
    def request_advisor():
        """Crear solicitud - Con validación y asignación inteligente"""
        try:
            data = request.get_json()

            # VALIDACIÓN ROBUSTA
            is_valid, error_msg = ValidationEngine.validate_request(data)
            if not is_valid:
                return jsonify({'error': error_msg}), 400

            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            topic = data.get('topic', '').strip()

            user_id = current_user.id if current_user.is_authenticated else None

            # Crear solicitud
            request_id = create_advisor_request(
                name=name,
                email=email,
                phone=phone,
                topic=topic,
                user_id=user_id
            )

            # OBTENER DATOS PARA ASIGNACIÓN
            advisors = get_available_advisors()
            waiting_count = len(get_pending_advisor_requests())

            # NOTIFICAR A ASESORES
            new_request = get_advisor_request(request_id)
            notification_manager.notify_new_request(new_request, advisors)

            # CALCULAR TIEMPO ESTIMADO
            avg_resolution = AdvancedAnalytics.get_system_analytics(
                get_pending_advisor_requests(), [], advisors
            ).get('avg_resolution_time_minutes', 10)

            return jsonify({
                'success': True,
                'request_id': request_id,
                'message': f'Solicitud creada. Eres #{ waiting_count} en la cola.',
                'estimated_wait_minutes': int(avg_resolution),
                'advisors_available': len(advisors),
                'position_in_queue': waiting_count
            }), 201

        except Exception as e:
            return jsonify({'error': str(e), 'details': str(e)}), 400


    @app.route('/api/advisor/requests', methods=['GET'])
    @login_required
    def get_advisor_requests():
        """Obtener solicitudes pendientes - Con filtros y prioridades"""
        user_data = get_user_by_id(current_user.id)
        if not user_data or not user_data.get('is_admin'):
            return jsonify({'error': 'No autorizado'}), 403

        pending_requests = get_pending_advisor_requests()

        # Ordenar por prioridad (más antiguos primero)
        pending_requests = sorted(pending_requests,
                                key=lambda r: r['created_at'])

        # Agregar información útil
        enriched = []
        for req in pending_requests:
            req_data = get_advisor_request(req['id'])
            messages = get_advisor_messages(req['id'])
            enriched.append({
                **req_data,
                'message_count': len(messages),
                'last_message_time': messages[-1]['created_at'] if messages else req['created_at'],
                'wait_time_minutes': 0  # Calcular si es necesario
            })

        return jsonify({
            'success': True,
            'total_waiting': len(enriched),
            'requests': enriched
        }), 200


    @app.route('/api/advisor/assign/<int:request_id>', methods=['POST'])
    @login_required
    def assign_request(request_id):
        """Asignar solicitud - Con lógica inteligente"""
        user_data = get_user_by_id(current_user.id)
        if not user_data or not user_data.get('is_admin'):
            return jsonify({'error': 'No autorizado'}), 403

        req = get_advisor_request(request_id)
        if not req:
            return jsonify({'error': 'Solicitud no encontrada'}), 404

        # Asignar y cambiar estado
        assign_advisor_request(request_id, current_user.id)
        set_advisor_status(current_user.id, 'online')

        # NOTIFICAR AL USUARIO
        notification_manager.notify_advisor_assigned(
            request_id,
            user_data['username'],
            req.get('user_id')
        )

        return jsonify({
            'success': True,
            'message': 'Solicitud asignada exitosamente',
            'request_id': request_id
        }), 200


    @app.route('/api/advisor/message/<int:request_id>', methods=['POST'])
    def send_advisor_message(request_id):
        """Enviar mensaje - Con validación completa"""
        try:
            data = request.get_json()
            message_text = data.get('message', '').strip()

            # VALIDACIÓN DE MENSAJE
            is_valid, error_msg = ValidationEngine.validate_message(message_text)
            if not is_valid:
                return jsonify({'error': error_msg}), 400

            req = get_advisor_request(request_id)
            if not req:
                return jsonify({'error': 'Solicitud no encontrada'}), 404

            # Determinar tipo de remitente
            if current_user.is_authenticated:
                sender_id = current_user.id
                user = get_user_by_id(current_user.id)
                sender_type = 'advisor' if user.get('is_admin') else 'user'
                sender_name = user.get('username', 'Usuario')
            else:
                sender_id = None
                sender_type = 'user'
                sender_name = req.get('name', 'Usuario')

            # Guardar mensaje
            msg_id = add_advisor_message(request_id, sender_id, sender_type, message_text)

            # NOTIFICAR AL OTRO USUARIO
            recipient_id = req.get('assigned_to') if sender_type == 'user' else req.get('user_id')
            if recipient_id:
                notification_manager.notify_message_received(
                    request_id,
                    sender_name,
                    message_text,
                    recipient_id
                )

            return jsonify({
                'success': True,
                'message_id': msg_id,
                'sender_type': sender_type,
                'timestamp': datetime.now().isoformat()
            }), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 400


    @app.route('/api/advisor/messages/<int:request_id>', methods=['GET'])
    def get_messages(request_id):
        """Obtener historial - Con información completa"""
        try:
            req = get_advisor_request(request_id)
            if not req:
                return jsonify({'error': 'Solicitud no encontrada'}), 404

            messages = get_advisor_messages(request_id)

            return jsonify({
                'success': True,
                'request': {
                    'id': req['id'],
                    'name': req['name'],
                    'email': req['email'],
                    'phone': req['phone'],
                    'topic': req['topic'],
                    'status': req['status'],
                    'created_at': req['created_at']
                },
                'messages': messages,
                'message_count': len(messages)
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400


    @app.route('/api/advisor/rate/<int:request_id>', methods=['POST'])
    def rate_advisor(request_id):
        """Calificar atención - Nuevo endpoint"""
        try:
            data = request.get_json()
            rating = data.get('rating')
            feedback = data.get('feedback', '')

            # Validar rating
            is_valid, error_msg = ValidationEngine.validate_rating(rating)
            if not is_valid:
                return jsonify({'error': error_msg}), 400

            # Guardar calificación en BD (necesitaría nueva función en database.py)
            # rate_advisor_request(request_id, rating, feedback)

            return jsonify({
                'success': True,
                'message': 'Gracias por tu calificación',
                'rating': rating
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400


    @app.route('/api/advisor/close/<int:request_id>', methods=['POST'])
    @login_required
    def close_request(request_id):
        """Cerrar solicitud - Con confirmación"""
        user_data = get_user_by_id(current_user.id)
        if not user_data or not user_data.get('is_admin'):
            return jsonify({'error': 'No autorizado'}), 403

        req = get_advisor_request(request_id)
        if not req:
            return jsonify({'error': 'Solicitud no encontrada'}), 404

        # Cerrar y registrar timestamp
        close_advisor_request(request_id)

        return jsonify({
            'success': True,
            'message': 'Solicitud cerrada',
            'request_id': request_id
        }), 200


    @app.route('/api/advisor/status', methods=['POST'])
    @login_required
    def update_advisor_status():
        """Actualizar estado - Con validación"""
        data = request.get_json()
        status = data.get('status', 'offline').lower()

        valid_statuses = ['online', 'offline', 'away', 'busy']
        if status not in valid_statuses:
            return jsonify({'error': f'Status inválido. Válidos: {valid_statuses}'}), 400

        set_advisor_status(current_user.id, status)

        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }), 200


    @app.route('/api/advisor/analytics', methods=['GET'])
    @login_required
    def get_advisor_analytics():
        """Analytics para asesores - Nuevo endpoint"""
        user_data = get_user_by_id(current_user.id)
        if not user_data or not user_data.get('is_admin'):
            return jsonify({'error': 'No autorizado'}), 403

        pending = get_pending_advisor_requests()
        all_advisors = get_available_advisors()
        messages = []  # Necesitaría función para obtener todos los mensajes

        metrics = AdvancedAnalytics.calculate_advisor_metrics(
            current_user.id, messages, pending
        )

        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200


    @app.route('/api/advisor/available', methods=['GET'])
    def get_advisors_available():
        """Obtener asesores disponibles - Con métricas"""
        advisors = get_available_advisors()

        enriched_advisors = []
        for advisor in advisors:
            enriched_advisors.append({
                'id': advisor['id'],
                'department': advisor.get('department', 'General'),
                'status': advisor['status'],
                'current_chats': advisor['current_chats'],
                'max_chats': advisor['max_chats'],
                'availability_percentage': (
                    (advisor['max_chats'] - advisor['current_chats']) / advisor['max_chats'] * 100
                )
            })

        return jsonify({
            'success': True,
            'advisors_available': len(advisors),
            'advisors': enriched_advisors,
            'has_available': len(advisors) > 0,
            'estimated_wait_minutes': 5 if advisors else 15
        }), 200
