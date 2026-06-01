"""
Rutas para Sugerencias de IA para Asesores
"""

from flask import request, jsonify
from ai_suggestions import AdvisorAISuggestions


def register_ai_suggestions_routes(app):
    """Registrar rutas de sugerencias de IA"""

    @app.route('/api/advisor/suggestions', methods=['POST'])
    def get_ai_suggestions():
        """
        Obtener sugerencias de IA basadas en el mensaje del usuario

        Request:
        {
            "message": "Usuario pregunta sobre becas",
            "conversation_history": [{"role": "user", "content": "..."}]
        }

        Response:
        {
            "suggestions": ["Sugerencia 1", "Sugerencia 2", "Sugerencia 3"],
            "quick_actions": [{"label": "...", "action": "..."}],
            "followup_questions": ["Pregunta 1", "Pregunta 2"],
            "sentiment": {"sentiment": "positive", "confidence": 0.8}
        }
        """
        try:
            data = request.get_json()
            message = data.get('message', '').strip()

            if not message:
                return jsonify({'error': 'Mensaje requerido'}), 400

            conversation_history = data.get('conversation_history', [])

            # Obtener sugerencias contextualizadas
            response = AdvisorAISuggestions.get_contextualized_response(
                message,
                conversation_history
            )

            return jsonify({
                'success': True,
                'suggestions': response['suggestions'],
                'quick_actions': response['quick_actions'],
                'followup_questions': response['followup_questions'],
                'sentiment': response['sentiment'],
                'intent': response['intent']
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/advisor/intent', methods=['POST'])
    def detect_intent():
        """Detectar la intención del usuario"""
        try:
            data = request.get_json()
            message = data.get('message', '').strip()

            if not message:
                return jsonify({'error': 'Mensaje requerido'}), 400

            intent = AdvisorAISuggestions.extract_intent(message)
            sentiment = AdvisorAISuggestions.analyze_sentiment(message)

            return jsonify({
                'success': True,
                'intent': intent,
                'sentiment': sentiment
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/advisor/quick-actions/<intent>', methods=['GET'])
    def get_quick_actions(intent):
        """Obtener acciones rápidas para una intención"""
        try:
            actions = AdvisorAISuggestions.get_quick_actions(intent)

            return jsonify({
                'success': True,
                'intent': intent,
                'actions': actions
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/advisor/followup/<intent>', methods=['GET'])
    def get_followup_questions(intent):
        """Obtener preguntas de seguimiento para una intención"""
        try:
            questions = AdvisorAISuggestions.generate_followup_questions(intent, '')

            return jsonify({
                'success': True,
                'intent': intent,
                'questions': questions
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/advisor/sentiment', methods=['POST'])
    def analyze_sentiment():
        """Analizar sentimiento del mensaje"""
        try:
            data = request.get_json()
            message = data.get('message', '').strip()

            if not message:
                return jsonify({'error': 'Mensaje requerido'}), 400

            sentiment = AdvisorAISuggestions.analyze_sentiment(message)

            return jsonify({
                'success': True,
                'sentiment': sentiment
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400
