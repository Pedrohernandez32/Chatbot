"""WhatsApp integration for advisor and AI chat"""
import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = "https://graph.instagram.com/v18.0"
WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_ID')
WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
WHATSAPP_BUSINESS_ACCOUNT_ID = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID')


def send_whatsapp_message(phone_number: str, message_text: str, message_type: str = 'text') -> bool:
    """Send a WhatsApp message using WhatsApp Business API"""
    if not all([WHATSAPP_PHONE_ID, WHATSAPP_ACCESS_TOKEN]):
        logger.warning('WhatsApp credentials not configured')
        return False

    try:
        url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages"
        headers = {
            'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Formatear número de teléfono (agregar código de país si falta)
        if not phone_number.startswith('+'):
            phone_number = f'+57{phone_number}' if not phone_number.startswith('57') else f'+{phone_number}'

        payload = {
            'messaging_product': 'whatsapp',
            'to': phone_number,
            'type': 'text',
            'text': {'body': message_text}
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            logger.info(f'WhatsApp message sent to {phone_number}')
            return True
        else:
            logger.error(f'Failed to send WhatsApp: {response.text}')
            return False

    except Exception as e:
        logger.error(f'WhatsApp send error: {str(e)}')
        return False


def parse_whatsapp_webhook(data: dict) -> Optional[dict]:
    """Parse incoming WhatsApp webhook message"""
    try:
        # Estructura: messages -> [0] -> from, text, type
        messages = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [])

        if not messages:
            return None

        msg = messages[0]
        return {
            'from': msg.get('from'),
            'type': msg.get('type', 'text'),
            'text': msg.get('text', {}).get('body', ''),
            'message_id': msg.get('id'),
            'timestamp': msg.get('timestamp')
        }

    except (IndexError, KeyError, TypeError) as e:
        logger.error(f'Error parsing WhatsApp webhook: {str(e)}')
        return None


def verify_whatsapp_webhook(token: str, challenge: str, verify_token: str) -> Optional[str]:
    """Verify WhatsApp webhook token"""
    if token == verify_token:
        return challenge
    return None


def notify_advisor_whatsapp(phone_number: str, user_name: str, request_id: int) -> bool:
    """Notify advisor about new request via WhatsApp"""
    message = (
        f"📞 Nueva solicitud de asesor\n\n"
        f"Cliente: {user_name}\n"
        f"Teléfono: {phone_number}\n"
        f"ID Solicitud: {request_id}\n\n"
        f"Responde desde la plataforma: /admin"
    )
    # Aquí irá el número del asesor (desde env var)
    advisor_phone = os.environ.get('ADVISOR_WHATSAPP_NOTIFY')
    if advisor_phone:
        return send_whatsapp_message(advisor_phone, message)
    return False


def send_ai_response_whatsapp(phone_number: str, response_text: str) -> bool:
    """Send AI response via WhatsApp"""
    # Dividir en mensajes más pequeños si es muy largo
    max_length = 1024
    messages = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]

    for msg in messages:
        if not send_whatsapp_message(phone_number, msg):
            return False
    return True
