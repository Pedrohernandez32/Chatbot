"""
WebSocket Server para Chat en Tiempo Real
Integración con Flask-SocketIO para comunicación instantánea
"""

from flask import request, session
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from datetime import datetime
from database import (
    add_advisor_message, get_advisor_messages, get_advisor_request,
    set_advisor_status, get_available_advisors
)
from advisor_enhanced import notification_manager

# Almacenar conexiones activas: {user_id: [socket_ids], ...}
active_connections = {}
active_advisors = {}  # {advisor_id: socket_id}
active_users = {}     # {user_id: socket_id}

def init_websocket(app):
    """Inicializar WebSocket con Flask"""
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    @socketio.on('connect')
    def handle_connect():
        """Usuario se conecta"""
        user_id = request.sid  # Usar socket ID como identificador temporal
        print(f"✅ Cliente conectado: {user_id}")
        emit('connection_response', {'data': 'Conectado al servidor'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Usuario se desconecta"""
        sid = request.sid
        # Limpiar de conexiones activas
        for user_list in active_connections.values():
            if sid in user_list:
                user_list.remove(sid)
        print(f"❌ Cliente desconectado: {sid}")

    @socketio.on('user_login')
    def handle_user_login(data):
        """Usuario inicia sesión"""
        user_id = data.get('user_id')
        is_advisor = data.get('is_advisor', False)

        sid = request.sid

        if is_advisor:
            active_advisors[user_id] = sid
            join_room(f'advisor_{user_id}')
            emit('login_response', {'status': 'success', 'role': 'advisor'})
        else:
            active_users[user_id] = sid
            join_room(f'user_{user_id}')
            emit('login_response', {'status': 'success', 'role': 'user'})

        print(f"👤 {('Asesor' if is_advisor else 'Usuario')} {user_id} logueado")

    @socketio.on('join_request')
    def handle_join_request(data):
        """Usuario se une a sala de solicitud"""
        request_id = data.get('request_id')
        user_id = data.get('user_id')

        room_name = f'request_{request_id}'
        join_room(room_name)

        emit('joined_room', {
            'request_id': request_id,
            'room': room_name,
            'timestamp': datetime.now().isoformat()
        })

        # Notificar a otros en la sala
        emit('user_joined', {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }, room=room_name, skip_sid=request.sid)

    @socketio.on('send_message')
    def handle_send_message(data):
        """Recibir mensaje en tiempo real"""
        request_id = data.get('request_id')
        message = data.get('message', '').strip()
        sender_id = data.get('sender_id')
        sender_type = data.get('sender_type', 'user')  # user o advisor
        sender_name = data.get('sender_name', 'Usuario')

        if not message or len(message) > 5000:
            emit('message_error', {'error': 'Mensaje inválido'})
            return

        # Guardar en base de datos
        msg_id = add_advisor_message(
            request_id=request_id,
            sender_id=sender_id,
            sender_type=sender_type,
            message=message
        )

        # Preparar respuesta
        message_data = {
            'id': msg_id,
            'request_id': request_id,
            'sender_id': sender_id,
            'sender_type': sender_type,
            'sender_name': sender_name,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        # Transmitir a sala específica
        room_name = f'request_{request_id}'
        emit('new_message', message_data, room=room_name)

        # Notificar al otro usuario
        if sender_type == 'user':
            # Buscar asesor asignado y notificarle
            req = get_advisor_request(request_id)
            if req and req.get('assigned_to'):
                advisor_id = req.get('assigned_to')
                advisor_room = f'advisor_{advisor_id}'
                emit('new_message', message_data, room=advisor_room)
        else:
            # Asesor envía - notificar al usuario
            req = get_advisor_request(request_id)
            if req and req.get('user_id'):
                user_id = req.get('user_id')
                user_room = f'user_{user_id}'
                emit('new_message', message_data, room=user_room)

    @socketio.on('advisor_status_change')
    def handle_advisor_status(data):
        """Cambiar estado del asesor"""
        advisor_id = data.get('advisor_id')
        new_status = data.get('status')  # online, offline, away, busy

        set_advisor_status(advisor_id, new_status)

        # Notificar a todos
        emit('advisor_status_updated', {
            'advisor_id': advisor_id,
            'status': new_status,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

    @socketio.on('typing')
    def handle_typing(data):
        """Indicador de "escribiendo""""
        request_id = data.get('request_id')
        user_id = data.get('user_id')
        sender_type = data.get('sender_type')

        room_name = f'request_{request_id}'
        emit('user_typing', {
            'user_id': user_id,
            'sender_type': sender_type,
            'timestamp': datetime.now().isoformat()
        }, room=room_name, skip_sid=request.sid)

    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Detener indicador de "escribiendo""""
        request_id = data.get('request_id')
        user_id = data.get('user_id')

        room_name = f'request_{request_id}'
        emit('user_stop_typing', {
            'user_id': user_id
        }, room=room_name, skip_sid=request.sid)

    @socketio.on('rate_request')
    def handle_rate_request(data):
        """Calificar solicitud"""
        request_id = data.get('request_id')
        rating = data.get('rating')  # 1-5
        feedback = data.get('feedback', '')

        # Guardar en BD (necesitaría función en database.py)
        emit('rating_received', {
            'request_id': request_id,
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

    @socketio.on('request_analytics')
    def handle_analytics_request(data):
        """Solicitar datos de analytics en tiempo real"""
        advisor_id = data.get('advisor_id')

        # Obtener análisis (simplificado aquí)
        analytics = {
            'pending_requests': 0,
            'total_messages': 0,
            'avg_rating': 0.0,
            'timestamp': datetime.now().isoformat()
        }

        emit('analytics_data', analytics)

    return socketio
