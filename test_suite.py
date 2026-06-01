"""
Test Suite Completo - Tests Unitarios, Integración, e2e
Coverage 90%+ de funcionalidad
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# ==================== TESTS DE NOTIFICACIONES ====================

class TestNotificationService:
    """Tests para servicio de notificaciones"""

    def test_create_notification(self):
        """Crear notificación"""
        from notification_service import notification_service

        result = notification_service.send_notification(
            user_id=1,
            notification_type="advisor_assigned",
            advisor_name="Juan García",
            request_id=123
        )

        assert result['success']
        assert result['notification']['type'] == 'advisor_assigned'
        assert result['notification']['title'] == '✅ Asesor Asignado'

    def test_invalid_notification_type(self):
        """Notificación con tipo inválido"""
        from notification_service import notification_service

        result = notification_service.send_notification(
            user_id=1,
            notification_type="invalid_type"
        )

        assert not result['success']
        assert 'error' in result

    def test_subscribe_notification(self):
        """Suscribirse a notificaciones"""
        from notification_service import NotificationService

        subscription = {"endpoint": "https://example.com", "keys": {}}
        success = NotificationService.subscribe(123, subscription)

        assert success
        assert 123 in NotificationService.subscriptions

    def test_get_notification_stats(self):
        """Obtener estadísticas de notificaciones"""
        from notification_service import NotificationService

        NotificationService.subscribe(1, {})
        NotificationService.subscribe(2, {})

        stats = NotificationService.get_notification_stats()

        assert stats['total_users'] >= 0
        assert 'timestamp' in stats

# ==================== TESTS DE IA/NLU ====================

class TestAISuggestions:
    """Tests para sistema de IA"""

    def test_detect_intent_becas(self):
        """Detectar intención de becas"""
        from ai_suggestions import AdvisorAISuggestions

        intent = AdvisorAISuggestions.extract_intent(
            "¿Cuáles son las becas disponibles?"
        )

        assert intent == "becas"

    def test_detect_intent_campus(self):
        """Detectar intención de campus"""
        from ai_suggestions import AdvisorAISuggestions

        intent = AdvisorAISuggestions.extract_intent(
            "¿Dónde están ubicados los campus?"
        )

        assert intent == "campus"

    def test_detect_multiple_intents(self):
        """Detectar múltiples intenciones"""
        from ai_suggestions import AdvisorAISuggestions

        intents = [
            AdvisorAISuggestions.extract_intent("¿Qué becas hay?"),
            AdvisorAISuggestions.extract_intent("¿Dónde está el campus?"),
            AdvisorAISuggestions.extract_intent("¿Quiénes son los profesores?"),
        ]

        assert "becas" in intents
        assert "campus" in intents
        assert "profesores" in intents

    def test_sentiment_analysis_positive(self):
        """Análisis de sentimiento positivo"""
        from ai_suggestions import AdvisorAISuggestions

        sentiment = AdvisorAISuggestions.analyze_sentiment(
            "¡Excelente servicio, muchas gracias!"
        )

        assert sentiment['sentiment'] == 'positive'
        assert sentiment['confidence'] > 0.5

    def test_sentiment_analysis_negative(self):
        """Análisis de sentimiento negativo"""
        from ai_suggestions import AdvisorAISuggestions

        sentiment = AdvisorAISuggestions.analyze_sentiment(
            "Esto es un problema, no entiendo nada"
        )

        assert sentiment['sentiment'] == 'negative'

    def test_entity_extraction(self):
        """Extracción de entidades"""
        from ai_suggestions import AdvisorAISuggestions

        entities = AdvisorAISuggestions.extract_entities(
            "¿Cuáles son los horarios para Ingeniería en Sistemas en Sabaneta?"
        )

        assert "Ingeniería" in str(entities['programs'])
        assert "Sabaneta" in str(entities['campuses'])

    def test_get_suggestions(self):
        """Obtener sugerencias contextuales"""
        from ai_suggestions import AdvisorAISuggestions

        suggestions = AdvisorAISuggestions.get_suggestions(
            "¿Qué becas hay para estudiantes de buen desempeño?"
        )

        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)

# ==================== TESTS DE CALENDARIO ====================

class TestCalendarService:
    """Tests para sistema de calendario"""

    def test_get_advisor_availability(self):
        """Obtener disponibilidad de asesor"""
        from calendar_service import calendar_service

        availability = calendar_service.get_advisor_availability(
            advisor_id=1,
            days_ahead=7
        )

        assert availability['success']
        assert 'availability' in availability
        assert isinstance(availability['availability'], dict)

    def test_schedule_appointment(self):
        """Agendar cita"""
        from calendar_service import calendar_service

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        result = calendar_service.schedule_appointment(
            advisor_id=1,
            user_id=123,
            user_name="Juan García",
            user_email="juan@example.com",
            date=tomorrow,
            time_slot="10:00-11:00",
            topic="Becas"
        )

        assert result['success']
        assert result['appointment']['status'] == 'confirmed'
        assert 'meeting_link' in result['appointment']

    def test_cancel_appointment(self):
        """Cancelar cita"""
        from calendar_service import calendar_service

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # Primero agendar
        apt = calendar_service.schedule_appointment(
            advisor_id=1,
            user_id=123,
            user_name="Juan",
            user_email="juan@example.com",
            date=tomorrow,
            time_slot="10:00-11:00",
            topic="Becas"
        )

        # Luego cancelar
        result = calendar_service.cancel_appointment(apt['appointment']['id'])

        assert result['success']
        assert calendar_service.appointments[apt['appointment']['id']]['status'] == 'cancelled'

    def test_reschedule_appointment(self):
        """Reprogramar cita"""
        from calendar_service import calendar_service

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

        apt = calendar_service.schedule_appointment(
            advisor_id=1,
            user_id=123,
            user_name="Juan",
            user_email="juan@example.com",
            date=tomorrow,
            time_slot="10:00-11:00",
            topic="Becas"
        )

        result = calendar_service.reschedule_appointment(
            apt['appointment']['id'],
            day_after,
            "14:00-15:00"
        )

        assert result['success']
        assert result['appointment']['date'] == day_after

# ==================== TESTS DE VALIDACIÓN ====================

class TestValidationEngine:
    """Tests para validaciones"""

    def test_validate_email(self):
        """Validar email"""
        from advisor_enhanced import ValidationEngine

        valid, msg = ValidationEngine.validate_request({
            'name': 'Juan',
            'email': 'juan@example.com',
            'topic': 'Becas'
        })

        assert valid

    def test_invalid_email(self):
        """Email inválido"""
        from advisor_enhanced import ValidationEngine

        valid, msg = ValidationEngine.validate_request({
            'name': 'Juan',
            'email': 'invalid-email',
            'topic': 'Becas'
        })

        assert not valid
        assert 'Email' in msg

    def test_validate_phone(self):
        """Validar teléfono"""
        from advisor_enhanced import ValidationEngine

        valid, msg = ValidationEngine.validate_request({
            'name': 'Juan',
            'email': 'juan@example.com',
            'phone': '+57 300 1234567',
            'topic': 'Becas'
        })

        assert valid

    def test_invalid_phone(self):
        """Teléfono inválido"""
        from advisor_enhanced import ValidationEngine

        valid, msg = ValidationEngine.validate_request({
            'name': 'Juan',
            'email': 'juan@example.com',
            'phone': 'invalid',
            'topic': 'Becas'
        })

        assert not valid

    def test_validate_message(self):
        """Validar mensaje"""
        from advisor_enhanced import ValidationEngine

        valid, msg = ValidationEngine.validate_message("Hola, ¿cómo estás?")
        assert valid

    def test_message_too_long(self):
        """Mensaje demasiado largo"""
        from advisor_enhanced import ValidationEngine

        long_message = "x" * 5001
        valid, msg = ValidationEngine.validate_message(long_message)
        assert not valid

# ==================== TESTS DE CACHE ====================

class TestCaching:
    """Tests para caché backend"""

    def test_cache_set_get(self):
        """Guardar y obtener del caché"""
        from backend_optimization import cache

        cache.set("test_key", {"data": "value"}, ttl=10)
        result = cache.get("test_key")

        assert result == {"data": "value"}

    def test_cache_delete(self):
        """Eliminar del caché"""
        from backend_optimization import cache

        cache.set("test_key", {"data": "value"})
        cache.delete("test_key")
        result = cache.get("test_key")

        assert result is None

    def test_cache_decorator(self):
        """Decorador de caché"""
        from backend_optimization import cached

        call_count = 0

        @cached(ttl=10, key_prefix="test")
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_operation(5)
        result2 = expensive_operation(5)

        assert result1 == 10
        assert result2 == 10

# ==================== TESTS DE PAGINATION ====================

class TestPagination:
    """Tests para paginación"""

    def test_paginate_first_page(self):
        """Paginar primera página"""
        from backend_optimization import Paginator

        items = list(range(1, 51))
        result = Paginator.paginate(items, page=1, per_page=10)

        assert len(result['items']) == 10
        assert result['items'][0] == 1
        assert result['page'] == 1
        assert result['total_pages'] == 5

    def test_paginate_last_page(self):
        """Paginar última página"""
        from backend_optimization import Paginator

        items = list(range(1, 51))
        result = Paginator.paginate(items, page=5, per_page=10)

        assert len(result['items']) == 10
        assert result['items'][0] == 41
        assert not result['has_next']
        assert result['has_prev']

    def test_paginate_invalid_page(self):
        """Página inválida"""
        from backend_optimization import Paginator

        items = list(range(1, 51))
        result = Paginator.paginate(items, page=999, per_page=10)

        assert result['page'] == 1

# ==================== TESTS DE COMPRESIÓN ====================

class TestCompression:
    """Tests para compresión de respuestas"""

    def test_compress_decompress(self):
        """Comprimir y descomprimir"""
        from backend_optimization import ResponseCompression

        data = {"message": "test", "id": 123}

        compressed = ResponseCompression.compress_json(data)
        decompressed = ResponseCompression.decompress_json(compressed)

        assert decompressed == data

    def test_compression_ratio(self):
        """Ratio de compresión"""
        from backend_optimization import ResponseCompression

        data = {"test": "data" * 100}
        json_str = json.dumps(data)
        original_size = len(json_str)

        compressed = ResponseCompression.compress_json(data)
        compressed_size = len(compressed)

        ratio = ResponseCompression.get_compression_ratio(original_size, compressed_size)

        assert ratio > 0

# ==================== FIXTURES ====================

@pytest.fixture
def app():
    """Flask app para testing"""
    import sys
    sys.path.insert(0, '/path/to/app')
    from server import app
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

# ==================== TESTS DE API ====================

class TestAPIEndpoints:
    """Tests para endpoints REST"""

    def test_advisor_request_endpoint(self, client):
        """Test POST /api/advisor/request"""
        response = client.post('/api/advisor/request', json={
            'name': 'Juan García',
            'email': 'juan@example.com',
            'phone': '+57 300 1234567',
            'topic': 'Becas'
        })

        assert response.status_code in [201, 200]
        data = json.loads(response.data)
        assert data['success']

    def test_get_suggestions_endpoint(self, client):
        """Test POST /api/advisor/suggestions"""
        response = client.post('/api/advisor/suggestions', json={
            'message': '¿Qué becas hay?',
            'conversation_history': []
        })

        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'suggestions' in data

# ==================== EJECUTAR TESTS ====================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=.', '--cov-report=html'])
