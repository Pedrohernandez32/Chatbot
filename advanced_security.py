"""
Seguridad Avanzada - 2FA, OAuth, Encriptación, Auditoría
"""

import os
import secrets
import qrcode
import json
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import hashlib
import hmac

# ==================== TWO-FACTOR AUTHENTICATION ====================

class TwoFactorAuth:
    """Sistema de autenticación de dos factores (2FA)"""

    @staticmethod
    def generate_secret() -> str:
        """Generar secreto TOTP para Google Authenticator"""
        import pyotp
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(user_email: str, secret: str) -> str:
        """
        Generar código QR para Google Authenticator
        Returns: URL base64 encoded de la imagen QR
        """
        try:
            import pyotp

            totp = pyotp.TOTP(secret)
            uri = totp.provisioning_uri(
                name=user_email,
                issuer_name='UdeMedellin Chat'
            )

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convertir a base64
            import io
            import base64

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            print(f"❌ Error generating QR: {e}")
            return ""

    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verificar token TOTP"""
        try:
            import pyotp

            totp = pyotp.TOTP(secret)
            return totp.verify(token)

        except Exception as e:
            print(f"❌ Error verifying token: {e}")
            return False

    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """
        Generar códigos de backup para recuperación
        """
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append({
                "code": code,
                "used": False,
                "created_at": datetime.now().isoformat()
            })
        return codes

# ==================== OAUTH 2.0 ====================

class OAuth2:
    """Autenticación OAuth 2.0 con Google y Microsoft"""

    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')

    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_OAUTH_CLIENT_ID')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_OAUTH_CLIENT_SECRET')
    MICROSOFT_REDIRECT_URI = os.environ.get('MICROSOFT_OAUTH_REDIRECT_URI', 'http://localhost:5000/auth/microsoft/callback')

    @staticmethod
    def get_google_auth_url(state: str) -> str:
        """Generar URL de autenticación de Google"""
        params = {
            'client_id': OAuth2.GOOGLE_CLIENT_ID,
            'redirect_uri': OAuth2.GOOGLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state
        }

        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    @staticmethod
    def get_microsoft_auth_url(state: str) -> str:
        """Generar URL de autenticación de Microsoft"""
        params = {
            'client_id': OAuth2.MICROSOFT_CLIENT_ID,
            'redirect_uri': OAuth2.MICROSOFT_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state
        }

        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{query_string}"

    @staticmethod
    def verify_oauth_state(stored_state: str, returned_state: str) -> bool:
        """Verificar estado CSRF"""
        return stored_state == returned_state

    @staticmethod
    def handle_google_callback(code: str, state: str) -> Dict:
        """Procesar callback de Google"""
        # En producción, intercambiar código por token
        return {
            "success": True,
            "provider": "google",
            "message": "Implementar intercambio de código en producción"
        }

    @staticmethod
    def handle_microsoft_callback(code: str, state: str) -> Dict:
        """Procesar callback de Microsoft"""
        # En producción, intercambiar código por token
        return {
            "success": True,
            "provider": "microsoft",
            "message": "Implementar intercambio de código en producción"
        }

# ==================== ENCRIPTACIÓN ====================

class Encryption:
    """Sistema de encriptación de datos sensibles"""

    CIPHER_KEY = os.environ.get('ENCRYPTION_KEY', 'default-key-change-in-production').encode()

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash de contraseña con salt
        Returns: (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            iterations=100000
        ).hex()

        return hashed, salt

    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Verificar contraseña hasheada"""
        test_hash, _ = Encryption.hash_password(password, salt)
        return hmac.compare_digest(hashed, test_hash)

    @staticmethod
    def encrypt_field(data: str) -> str:
        """Encriptar campo de datos"""
        from cryptography.fernet import Fernet

        try:
            f = Fernet(Encryption.CIPHER_KEY)
            return f.encrypt(data.encode()).decode()
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            return data

    @staticmethod
    def decrypt_field(encrypted_data: str) -> str:
        """Desencriptar campo de datos"""
        from cryptography.fernet import Fernet

        try:
            f = Fernet(Encryption.CIPHER_KEY)
            return f.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return ""

# ==================== AUDITORÍA ====================

class AuditLog:
    """Sistema de auditoría de acciones"""

    logs = []

    @staticmethod
    def log_action(
        user_id: int,
        action: str,
        resource: str,
        details: Dict,
        status: str = "success"
    ):
        """Registrar acción de usuario"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details,
            "status": status,
            "ip_address": details.get('ip_address', 'unknown'),
            "user_agent": details.get('user_agent', 'unknown')
        }

        AuditLog.logs.append(log_entry)

        # En producción, guardar en BD
        print(f"📋 Audit: {action} on {resource} by user {user_id}")

        return log_entry

    @staticmethod
    def get_user_logs(user_id: int, hours: int = 24) -> list:
        """Obtener logs de un usuario"""
        since = datetime.now() - timedelta(hours=hours)

        return [
            log for log in AuditLog.logs
            if log['user_id'] == user_id and
            datetime.fromisoformat(log['timestamp']) > since
        ]

    @staticmethod
    def detect_suspicious_activity(user_id: int) -> Dict:
        """Detectar actividad sospechosa"""
        logs = AuditLog.get_user_logs(user_id, hours=24)

        failed_logins = sum(1 for log in logs if log['action'] == 'login' and log['status'] == 'failed')
        unusual_times = sum(1 for log in logs if self._is_unusual_time(log['timestamp']))
        ip_changes = len(set(log['ip_address'] for log in logs))

        alerts = []

        if failed_logins > 5:
            alerts.append("❌ Múltiples intentos de login fallidos")

        if ip_changes > 3:
            alerts.append("⚠️ Acceso desde múltiples direcciones IP")

        if unusual_times > 3:
            alerts.append("⚠️ Acceso en horas inusuales")

        return {
            "user_id": user_id,
            "alerts": alerts,
            "risk_level": "high" if len(alerts) > 0 else "low"
        }

    @staticmethod
    def _is_unusual_time(timestamp_str: str) -> bool:
        """Verificar si es hora inusual (2am-5am)"""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return 2 <= dt.hour <= 5
        except:
            return False

# ==================== RATE LIMITING AVANZADO ====================

class AdvancedRateLimiter:
    """Rate limiting inteligente por tipo de operación"""

    limits = {
        "login": {"requests": 5, "window": 300},  # 5 login attempts en 5 min
        "api": {"requests": 30, "window": 60},    # 30 requests/minuto
        "chat": {"requests": 100, "window": 60},  # 100 msgs/minuto
        "password_reset": {"requests": 3, "window": 3600},  # 3 resets/hora
    }

    attempts = {}

    @staticmethod
    def check_limit(user_id: int, operation_type: str) -> Tuple[bool, Dict]:
        """
        Verificar si usuario excede límite
        Returns: (allowed, remaining_info)
        """
        key = f"{user_id}:{operation_type}"

        if key not in AdvancedRateLimiter.attempts:
            AdvancedRateLimiter.attempts[key] = {
                "count": 0,
                "reset_time": datetime.now() + timedelta(
                    seconds=AdvancedRateLimiter.limits[operation_type]["window"]
                )
            }

        attempt = AdvancedRateLimiter.attempts[key]
        limit_config = AdvancedRateLimiter.limits.get(operation_type, {"requests": 100, "window": 60})

        # Resetear si tiempo expiró
        if datetime.now() > attempt['reset_time']:
            attempt['count'] = 0
            attempt['reset_time'] = datetime.now() + timedelta(
                seconds=limit_config["window"]
            )

        allowed = attempt['count'] < limit_config['requests']

        if allowed:
            attempt['count'] += 1

        remaining = limit_config['requests'] - attempt['count']
        reset_in = (attempt['reset_time'] - datetime.now()).total_seconds()

        return allowed, {
            "remaining": max(0, remaining),
            "reset_in_seconds": int(reset_in),
            "limit": limit_config['requests']
        }

# ==================== INSTANCIAS GLOBALES ====================

two_factor_auth = TwoFactorAuth()
oauth2 = OAuth2()
encryption = Encryption()
audit_log = AuditLog()
advanced_rate_limiter = AdvancedRateLimiter()

print("✅ Advanced Security initialized")
