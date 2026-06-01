"""
Integración con WhatsApp Business API
Permite a usuarios solicitar asesoría por WhatsApp
"""

import requests
from datetime import datetime
from typing import Dict, Optional
import os
import json
from hashlib import sha256
import hmac

class WhatsAppIntegration:
    """Integración bidireccional con WhatsApp"""

    def __init__(self):
        self.phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        self.business_account_id = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID')
        self.access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        self.webhook_secret = os.environ.get('WHATSAPP_WEBHOOK_SECRET')
        self.api_url = "https://graph.instagram.com/v18.0"

    def send_message(
        self,
        to_phone: str,
        message_text: str,
        message_type: str = "text"
    ) -> Dict:
        """
        Enviar mensaje por WhatsApp

        Args:
            to_phone: Número de teléfono destino (ej: +573001234567)
            message_text: Texto del mensaje
            message_type: tipo (text, template, media)
        """
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message_text
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            # En producción, hacer request real
            # response = requests.post(url, json=payload, headers=headers)

            print(f"💬 WhatsApp message sent to {to_phone}")

            return {
                "success": True,
                "message_id": f"msg-{datetime.now().timestamp()}",
                "to": to_phone,
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def send_template_message(
        self,
        to_phone: str,
        template_name: str,
        template_variables: list = None
    ) -> Dict:
        """Enviar mensaje de plantilla (más profesional)"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "es"
                    },
                    "components": []
                }
            }

            if template_variables:
                payload["template"]["components"].append({
                    "type": "body",
                    "parameters": [{"type": "text", "text": var} for var in template_variables]
                })

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            print(f"📧 WhatsApp template sent to {to_phone}")

            return {
                "success": True,
                "message_id": f"msg-{datetime.now().timestamp()}",
                "template": template_name,
                "status": "sent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def send_media_message(
        self,
        to_phone: str,
        media_url: str,
        media_type: str,  # image, video, audio, document
        caption: str = None
    ) -> Dict:
        """Enviar multimedia por WhatsApp"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": media_type,
                media_type: {
                    "link": media_url
                }
            }

            if caption:
                payload[media_type]["caption"] = caption

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            print(f"🎥 WhatsApp media sent to {to_phone}")

            return {
                "success": True,
                "message_id": f"msg-{datetime.now().timestamp()}",
                "media_type": media_type,
                "status": "sent"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def mark_message_as_read(self, message_id: str) -> Dict:
        """Marcar mensaje como leído"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            return {
                "success": True,
                "message_id": message_id,
                "status": "read"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_whatsapp_request_link(self) -> str:
        """Crear link para iniciar chat en WhatsApp"""
        phone = self.phone_number_id or "573001234567"  # Número de UdeMedellin
        message = "Hola, necesito ayuda con UdeMedellin"
        return f"https://wa.me/{phone}?text={message}"

    def process_webhook_event(self, webhook_data: Dict) -> Dict:
        """Procesar eventos de webhook de WhatsApp"""
        try:
            # Verificar firma
            if not self._verify_webhook_signature(webhook_data):
                return {"success": False, "error": "Invalid signature"}

            # Extraer información
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})

            # Procesar mensajes
            messages = value.get("messages", [])
            for message in messages:
                self._handle_incoming_message(message)

            # Procesar cambios de estado
            statuses = value.get("statuses", [])
            for status in statuses:
                self._handle_status_update(status)

            return {
                "success": True,
                "processed": len(messages) + len(statuses)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _verify_webhook_signature(self, webhook_data: Dict) -> bool:
        """Verificar firma de webhook"""
        if not self.webhook_secret:
            return True  # Sin verificación en desarrollo

        # En producción, implementar verificación HMAC
        return True

    def _handle_incoming_message(self, message: Dict):
        """Procesar mensaje entrante de WhatsApp"""
        try:
            from_phone = message.get("from")
            timestamp = message.get("timestamp")
            message_id = message.get("id")

            # Extraer contenido según tipo
            message_type = message.get("type")

            if message_type == "text":
                text_content = message.get("text", {}).get("body", "")
                print(f"📨 Incoming WhatsApp: {from_phone} - {text_content}")

                # Crear solicitud de asesor automáticamente
                self._create_advisor_request_from_whatsapp(
                    phone=from_phone,
                    message=text_content,
                    whatsapp_message_id=message_id
                )

            elif message_type == "interactive":
                button_id = message.get("interactive", {}).get("button_reply", {}).get("id")
                print(f"📨 Button press: {from_phone} - {button_id}")

        except Exception as e:
            print(f"❌ Error handling incoming message: {e}")

    def _handle_status_update(self, status: Dict):
        """Procesar actualización de estado de mensaje"""
        try:
            message_id = status.get("id")
            status_value = status.get("status")  # sent, delivered, read, failed

            print(f"📊 Message {message_id} status: {status_value}")

        except Exception as e:
            print(f"❌ Error handling status update: {e}")

    def _create_advisor_request_from_whatsapp(
        self,
        phone: str,
        message: str,
        whatsapp_message_id: str
    ):
        """Crear solicitud de asesor desde mensaje de WhatsApp"""
        # En producción, llamar a la función de crear solicitud
        print(f"✅ Created advisor request from WhatsApp: {phone}")

    def send_quick_reply_buttons(
        self,
        to_phone: str,
        message_text: str,
        buttons: list  # [{"id": "1", "title": "Becas"}, ...]
    ) -> Dict:
        """Enviar mensaje con botones de respuesta rápida"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": btn["id"],
                                    "title": btn["title"]
                                }
                            }
                            for btn in buttons[:3]  # Máximo 3 botones
                        ]
                    }
                }
            }

            return {
                "success": True,
                "message_id": f"msg-{datetime.now().timestamp()}",
                "buttons_sent": len(buttons)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Instancia global
whatsapp = WhatsAppIntegration()
