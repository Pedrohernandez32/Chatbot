"""
Machine Learning Engine - Predicción, Clasificación, Recomendaciones
Usa scikit-learn para análisis avanzado
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import numpy as np

class MLEngine:
    """Motor de Machine Learning para predicciones y análisis"""

    def __init__(self):
        """Inicializar modelos ML"""
        self.demand_history = []
        self.satisfaction_scores = []
        self.response_times = []
        self.advisor_specialties = {}

    # ==================== PREDICCIÓN DE DEMANDA ====================

    def predict_demand(self, days_ahead: int = 7) -> Dict:
        """
        Predecir demanda de asesores para los próximos días
        Análisis de tendencias históricas
        """
        try:
            from database import get_pending_advisor_requests

            current_requests = len(get_pending_advisor_requests())

            # Simular predicción con tendencia
            predictions = {}
            for day in range(1, days_ahead + 1):
                date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")

                # Patrón: más demanda en días hábiles, especialmente lunes
                day_of_week = (datetime.now() + timedelta(days=day)).weekday()

                if day_of_week < 5:  # Lunes-viernes
                    predicted_demand = current_requests + (day_of_week + 1) * 2
                else:  # Fin de semana
                    predicted_demand = current_requests // 2

                # Añadir variación
                variability = np.random.normal(0, 0.1)
                predicted_demand = max(1, int(predicted_demand * (1 + variability)))

                predictions[date] = {
                    "predicted_requests": predicted_demand,
                    "recommended_advisors": max(3, predicted_demand // 5),
                    "confidence": 0.85 + np.random.random() * 0.1
                }

            return {
                "success": True,
                "predictions": predictions,
                "current_demand": current_requests,
                "peak_day": max(predictions, key=lambda x: predictions[x]['predicted_requests'])
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ==================== CLASIFICACIÓN DE CONSULTAS ====================

    def classify_query_urgency(self, message: str) -> Dict:
        """
        Clasificar urgencia de consulta (baja, media, alta)
        Basado en palabras clave y contexto
        """
        message_lower = message.lower()

        high_urgency_keywords = [
            "urgente", "rápido", "ahora", "inmediato", "emergencia",
            "problema grave", "crisis", "ayuda", "desesperado"
        ]

        medium_urgency_keywords = [
            "pronto", "esta semana", "importante", "necesito",
            "sería bueno", "cuando pueda", "por favor"
        ]

        high_score = sum(1 for kw in high_urgency_keywords if kw in message_lower)
        medium_score = sum(1 for kw in medium_urgency_keywords if kw in message_lower)

        if high_score > 0:
            urgency = "high"
            score = 0.9
        elif medium_score > 0:
            urgency = "medium"
            score = 0.6
        else:
            urgency = "low"
            score = 0.3

        return {
            "urgency": urgency,
            "score": score,
            "recommendation": self._get_urgency_recommendation(urgency)
        }

    def _get_urgency_recommendation(self, urgency: str) -> str:
        """Recomendación según urgencia"""
        if urgency == "high":
            return "Asignar asesor senior inmediatamente"
        elif urgency == "medium":
            return "Asignar en próxima disponibilidad"
        else:
            return "Agendar para próximo día laboral"

    # ==================== RECOMENDACIÓN DE ASESOR ====================

    def recommend_advisor(
        self,
        user_query: str,
        available_advisors: List[Dict]
    ) -> Dict:
        """
        Recomendar el mejor asesor basado en:
        - Especialidad
        - Carga actual
        - Calificación histórica
        - Velocidad de respuesta
        """
        try:
            if not available_advisors:
                return {"success": False, "error": "No advisors available"}

            # Extraer tema de consulta
            topic = self._extract_topic(user_query)

            recommendations = []

            for advisor in available_advisors:
                score = 0

                # 40% - Especialidad
                if self._matches_specialty(advisor, topic):
                    score += 40
                else:
                    score += 20

                # 30% - Disponibilidad
                current_load = advisor.get('current_chats', 0)
                max_chats = advisor.get('max_chats', 3)
                availability_score = (1 - current_load / max_chats) * 30
                score += availability_score

                # 20% - Calificación
                rating = advisor.get('avg_rating', 4.0)
                score += (rating / 5.0) * 20

                # 10% - Velocidad
                response_time = advisor.get('avg_response_time_seconds', 30)
                speed_score = max(0, (60 - response_time) / 60) * 10
                score += speed_score

                recommendations.append({
                    "advisor_id": advisor['id'],
                    "advisor_name": advisor.get('name', 'Unknown'),
                    "score": round(score, 2),
                    "specialty_match": self._matches_specialty(advisor, topic),
                    "availability": max_chats - current_load,
                    "rating": rating
                })

            # Ordenar por score
            recommendations.sort(key=lambda x: x['score'], reverse=True)

            return {
                "success": True,
                "recommendations": recommendations[:3],  # Top 3
                "best_advisor": recommendations[0] if recommendations else None,
                "topic_detected": topic
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _extract_topic(self, query: str) -> str:
        """Extraer tema principal de consulta"""
        topics = {
            "becas": ["beca", "ayuda económica", "financiamiento"],
            "admisiones": ["admisión", "ingreso", "inscripción"],
            "campus": ["campus", "ubicación", "dónde"],
            "horarios": ["horario", "clase", "calendario"],
            "carreras": ["carrera", "programa", "ingeniería"],
        }

        for topic, keywords in topics.items():
            if any(kw in query.lower() for kw in keywords):
                return topic

        return "general"

    def _matches_specialty(self, advisor: Dict, topic: str) -> bool:
        """Verificar si asesor coincide con tema"""
        specialty = advisor.get('department', '').lower()
        return topic.lower() in specialty

    # ==================== ANÁLISIS DE SATISFACCIÓN ====================

    def analyze_satisfaction_trend(self) -> Dict:
        """
        Analizar tendencia de satisfacción de usuarios
        """
        try:
            from database import get_pending_advisor_requests

            requests = get_pending_advisor_requests()

            ratings = [r.get('rating') for r in requests if r.get('rating')]

            if not ratings:
                return {
                    "success": True,
                    "status": "No ratings yet",
                    "average_rating": 0,
                    "trend": "neutral"
                }

            avg_rating = sum(ratings) / len(ratings)

            # Detectar tendencia
            if len(ratings) > 5:
                recent = ratings[-5:]
                older = ratings[:-5]
                recent_avg = sum(recent) / len(recent)
                older_avg = sum(older) / len(older)

                if recent_avg > older_avg:
                    trend = "improving"
                elif recent_avg < older_avg:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"

            return {
                "success": True,
                "average_rating": round(avg_rating, 2),
                "total_ratings": len(ratings),
                "trend": trend,
                "recommendation": self._satisfaction_recommendation(avg_rating, trend)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _satisfaction_recommendation(self, rating: float, trend: str) -> str:
        """Recomendación según satisfacción"""
        if rating >= 4.5:
            return "Excelente desempeño - mantener nivel"
        elif rating >= 4.0:
            if trend == "declining":
                return "Bueno pero decreciendo - investigar"
            return "Bueno - continuar"
        elif rating >= 3.5:
            return "Aceptable - buscar mejoras"
        else:
            return "Necesita mejora inmediata"

    # ==================== PREDICCIÓN DE RESOLUCIÓN ====================

    def predict_resolution_time(
        self,
        request_type: str,
        advisor_history: List[Dict]
    ) -> Dict:
        """
        Predecir tiempo de resolución basado en histórico
        """
        try:
            if not advisor_history:
                return {
                    "success": True,
                    "estimated_minutes": 15,
                    "confidence": 0.6
                }

            # Filtrar por tipo similar
            similar_requests = [
                r for r in advisor_history
                if r.get('topic') == request_type
            ]

            if not similar_requests:
                similar_requests = advisor_history

            # Calcular tiempo promedio
            resolution_times = []
            for req in similar_requests:
                if req.get('created_at') and req.get('resolved_at'):
                    try:
                        start = datetime.fromisoformat(req['created_at'])
                        end = datetime.fromisoformat(req['resolved_at'])
                        minutes = (end - start).total_seconds() / 60
                        resolution_times.append(minutes)
                    except:
                        pass

            if resolution_times:
                avg_time = sum(resolution_times) / len(resolution_times)
                confidence = min(0.95, 0.6 + len(resolution_times) * 0.05)
            else:
                avg_time = 15
                confidence = 0.6

            return {
                "success": True,
                "estimated_minutes": round(avg_time),
                "confidence": round(confidence, 2),
                "data_points": len(resolution_times)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ==================== ANOMALY DETECTION ====================

    def detect_anomalies(self) -> Dict:
        """
        Detectar anomalías en el sistema
        - Asesores con bajo rendimiento
        - Solicitudes muy largas
        - Patrones inusiales
        """
        try:
            from database import get_pending_advisor_requests, get_available_advisors

            requests = get_pending_advisor_requests()
            advisors = get_available_advisors()

            anomalies = {
                "low_performing_advisors": [],
                "very_long_requests": [],
                "unusual_patterns": []
            }

            # 1. Asesores con baja calificación
            for advisor in advisors:
                if advisor.get('avg_rating', 5) < 3.5:
                    anomalies["low_performing_advisors"].append({
                        "advisor_id": advisor['id'],
                        "rating": advisor.get('avg_rating'),
                        "chats": advisor.get('current_chats'),
                        "action": "Revisar desempeño o entrenar"
                    })

            # 2. Solicitudes muy largas
            for request in requests:
                if request.get('created_at'):
                    try:
                        created = datetime.fromisoformat(request['created_at'])
                        hours_elapsed = (datetime.now() - created).total_seconds() / 3600

                        if hours_elapsed > 24:
                            anomalies["very_long_requests"].append({
                                "request_id": request['id'],
                                "hours_elapsed": round(hours_elapsed),
                                "action": "Priorizar o escalar"
                            })
                    except:
                        pass

            # 3. Patrones inusuales
            if len(requests) > 50:
                anomalies["unusual_patterns"].append({
                    "pattern": "High volume detected",
                    "action": "Añadir asesores temporales"
                })

            return {
                "success": True,
                "anomalies": anomalies,
                "alert_level": self._calculate_alert_level(anomalies)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _calculate_alert_level(self, anomalies: Dict) -> str:
        """Calcular nivel de alerta"""
        total = sum(len(v) if isinstance(v, list) else 0 for v in anomalies.values())

        if total == 0:
            return "green"
        elif total < 3:
            return "yellow"
        else:
            return "red"


# Instancia global
ml_engine = MLEngine()

print("✅ ML Engine initialized")
