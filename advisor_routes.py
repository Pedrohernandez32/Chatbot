# ============================================================
# Rutas para Asesores Humanos
# ============================================================

from flask import request, jsonify, current_app
from flask_login import current_user, login_required
from database import (
    create_advisor_request, get_pending_advisor_requests,
    assign_advisor_request, add_advisor_message, get_advisor_messages,
    get_advisor_request, close_advisor_request, register_advisor,
    set_advisor_status, get_available_advisors, get_user_by_id
)


def register_advisor_routes(app):
    """Registrar todas las rutas de asesores"""

    @app.route('/api/advisor/request', methods=['POST'])
    def request_advisor():
        """Crear solicitud para hablar con asesor humano"""
        try:
            data = request.get_json()
            name = data.get('name', 'Usuario')
            email = data.get('email', '')
            phone = data.get('phone', '')
            topic = data.get('topic', 'Consulta general')

            user_id = current_user.id if current_user.is_authenticated else None

            # Crear solicitud
            request_id = create_advisor_request(
                name=name,
                email=email,
                phone=phone,
                topic=topic,
                user_id=user_id
            )

            return jsonify({
                'success': True,
                'request_id': request_id,
                'message': 'Solicitud creada. Un asesor se conectará pronto.'
            }), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 400


    @app.route('/api/advisor/requests', methods=['GET'])
    @login_required
    def get_advisor_requests():
        """Obtener solicitudes pendientes (solo para asesores)"""
        # Verificar que el usuario sea un asesor
        user_data = get_user_by_id(current_user.id)
        if not user_data or not user_data.get('is_admin'):
            return jsonify({'error': 'No autorizado'}), 403

        requests = get_pending_advisor_requests()
        return jsonify({
            'success': True,
            'requests': requests
        }), 200


    @app.route('/api/advisor/assign/<int:request_id>', methods=['POST'])
    @login_required
    def assign_request(request_id):
        """Asignar solicitud a asesor"""
        user_data = get_user_by_id(current_user.id)
        if not user_data or not user_data.get('is_admin'):
            return jsonify({'error': 'No autorizado'}), 403

        assign_advisor_request(request_id, current_user.id)
        set_advisor_status(current_user.id, 'online')

        return jsonify({
            'success': True,
            'message': 'Solicitud asignada'
        }), 200


    @app.route('/api/advisor/message/<int:request_id>', methods=['POST'])
    def send_advisor_message(request_id):
        """Enviar mensaje en chat de asesor"""
        try:
            data = request.get_json()
            message = data.get('message', '').strip()

            if not message:
                return jsonify({'error': 'Mensaje vacío'}), 400

            # Determinar tipo de remitente
            if current_user.is_authenticated:
                sender_id = current_user.id
                sender_type = 'advisor' if get_user_by_id(current_user.id).get('is_admin') else 'user'
            else:
                sender_id = None
                sender_type = 'user'

            # Guardar mensaje
            add_advisor_message(request_id, sender_id, sender_type, message)

            return jsonify({
                'success': True,
                'message': 'Mensaje enviado'
            }), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 400


    @app.route('/api/advisor/messages/<int:request_id>', methods=['GET'])
    def get_messages(request_id):
        """Obtener historial de mensajes"""
        try:
            messages = get_advisor_messages(request_id)
            request_data = get_advisor_request(request_id)

            return jsonify({
                'success': True,
                'request': request_data,
                'messages': messages
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400


    @app.route('/api/advisor/close/<int:request_id>', methods=['POST'])
    @login_required
    def close_request(request_id):
        """Cerrar solicitud de asesor"""
        close_advisor_request(request_id)

        return jsonify({
            'success': True,
            'message': 'Solicitud cerrada'
        }), 200


    @app.route('/api/advisor/status', methods=['POST'])
    @login_required
    def update_advisor_status():
        """Actualizar estado de asesor (online/offline)"""
        data = request.get_json()
        status = data.get('status', 'offline')

        set_advisor_status(current_user.id, status)

        return jsonify({
            'success': True,
            'status': status
        }), 200


    @app.route('/api/advisor/available', methods=['GET'])
    def get_advisors_available():
        """Obtener asesores disponibles"""
        advisors = get_available_advisors()

        return jsonify({
            'success': True,
            'advisors': advisors,
            'available': len(advisors) > 0
        }), 200
