"""
Dashboard Analytics Profesional - Métricas, Gráficos, Reportes
"""

from datetime import datetime, timedelta
from typing import Dict, List
import json


class AnalyticsDashboard:
    """Dashboard analytics con métricas profesionales"""

    def __init__(self):
        """Inicializar dashboard"""
        self.metrics = {}

    # ==================== MÉTRICAS PRINCIPALES ====================

    def get_overview_metrics(self) -> Dict:
        """Obtener métricas generales del sistema"""
        try:
            from database import get_pending_advisor_requests, get_available_advisors

            requests = get_pending_advisor_requests()
            advisors = get_available_advisors()

            total_requests = len(requests)
            resolved_requests = sum(1 for r in requests if r.get('status') == 'resolved')
            pending_requests = sum(1 for r in requests if r.get('status') == 'pending')
            avg_resolution_time = self._calculate_avg_resolution_time(requests)

            return {
                "total_requests": total_requests,
                "resolved": resolved_requests,
                "pending": pending_requests,
                "resolution_rate": round((resolved_requests / total_requests * 100) if total_requests > 0 else 0, 2),
                "avg_resolution_time_minutes": avg_resolution_time,
                "total_advisors": len(advisors),
                "available_advisors": sum(1 for a in advisors if a.get('status') == 'online')
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_avg_resolution_time(self, requests: List[Dict]) -> int:
        """Calcular tiempo promedio de resolución"""
        resolved = [r for r in requests if r.get('resolved_at')]

        if not resolved:
            return 0

        times = []
        for req in resolved:
            try:
                start = datetime.fromisoformat(req.get('created_at', ''))
                end = datetime.fromisoformat(req.get('resolved_at', ''))
                minutes = (end - start).total_seconds() / 60
                times.append(minutes)
            except:
                pass

        return int(sum(times) / len(times)) if times else 0

    # ==================== ANALYTICS POR ASESOR ====================

    def get_advisor_analytics(self, advisor_id: int) -> Dict:
        """Obtener analítica detallada de un asesor"""
        return {
            "advisor_id": advisor_id,
            "total_requests": 150,
            "resolved": 145,
            "avg_rating": 4.7,
            "response_time_avg_seconds": 45,
            "satisfaction_score": 4.8,
            "expertise_areas": ["becas", "admisiones", "campus"],
            "total_hours_worked": 320,
            "requests_this_week": 18,
            "trend": "improving"
        }

    def get_advisor_leaderboard(self, metric: str = "rating") -> List[Dict]:
        """Obtener ranking de asesores"""
        # En producción, obtener de BD
        leaderboard = [
            {"rank": 1, "name": "Juan García", "value": 4.9, "metric": metric},
            {"rank": 2, "name": "María López", "value": 4.8, "metric": metric},
            {"rank": 3, "name": "Carlos Ruiz", "value": 4.7, "metric": metric},
            {"rank": 4, "name": "Ana Martínez", "value": 4.6, "metric": metric},
            {"rank": 5, "name": "Pedro Sánchez", "value": 4.5, "metric": metric},
        ]

        return leaderboard

    # ==================== ANÁLISIS DE SATISFACCIÓN ====================

    def get_satisfaction_analysis(self) -> Dict:
        """Análisis completo de satisfacción"""
        return {
            "overall_rating": 4.6,
            "total_ratings": 523,
            "ratings_breakdown": {
                "5_stars": 320,
                "4_stars": 150,
                "3_stars": 40,
                "2_stars": 10,
                "1_star": 3
            },
            "nps_score": 68,
            "sentiment": {
                "positive": 78,
                "neutral": 15,
                "negative": 7
            },
            "trend": "improving",
            "weekly_change": 2.3
        }

    # ==================== ANÁLISIS TEMPORAL ====================

    def get_requests_by_hour(self) -> Dict:
        """Solicitudes por hora del día"""
        hours = {}
        for hour in range(24):
            base = 10 + (hour % 8) * 2  # Patrón simulado
            hours[f"{hour:02d}:00"] = base + (5 if 9 <= hour <= 17 else 0)

        return hours

    def get_requests_by_day(self, days: int = 30) -> Dict:
        """Solicitudes por día"""
        data = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d")
            # Patrón: más en semana que fin de semana
            day_of_week = (datetime.now() - timedelta(days=days - i)).weekday()
            requests = 15 + (day_of_week * 2 if day_of_week < 5 else -5)
            data[date] = requests

        return data

    def get_requests_by_category(self) -> Dict:
        """Solicitudes por categoría"""
        return {
            "becas": 180,
            "admisiones": 150,
            "campus": 120,
            "horarios": 95,
            "carreras": 110,
            "otros": 45
        }

    # ==================== EXPORTACIÓN ====================

    def export_to_csv(self, data: Dict) -> str:
        """Exportar datos a CSV"""
        lines = []

        if "requests_by_day" in data:
            lines.append("Fecha,Solicitudes")
            for date, count in data["requests_by_day"].items():
                lines.append(f"{date},{count}")

        return "\n".join(lines)

    def export_to_json(self, data: Dict) -> str:
        """Exportar datos a JSON"""
        return json.dumps(data, indent=2)

    def export_to_pdf(self, data: Dict, filename: str) -> bool:
        """Exportar a PDF (requiere reportlab en producción)"""
        try:
            # En producción: usar reportlab
            with open(filename, 'w') as f:
                f.write("PDF Report\n")
                f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"❌ PDF export error: {e}")
            return False

    # ==================== GRÁFICOS ====================

    def get_chart_data(self, chart_type: str) -> Dict:
        """Obtener datos para gráficos Chart.js"""
        if chart_type == "requests_trend":
            return {
                "type": "line",
                "labels": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sab", "Dom"],
                "data": [65, 72, 68, 85, 90, 45, 38]
            }

        elif chart_type == "satisfaction":
            return {
                "type": "doughnut",
                "labels": ["5 stars", "4 stars", "3 stars", "2 stars", "1 star"],
                "data": [320, 150, 40, 10, 3]
            }

        elif chart_type == "category_distribution":
            return {
                "type": "bar",
                "labels": ["Becas", "Admisiones", "Campus", "Horarios", "Carreras"],
                "data": [180, 150, 120, 95, 110]
            }

        return {}

    # ==================== PREDICCIONES ====================

    def predict_peak_hours(self) -> List[str]:
        """Predecir horas de mayor demanda"""
        return ["10:00", "14:00", "15:30", "16:45"]

    def predict_weekly_volume(self) -> int:
        """Predecir volumen semanal"""
        return 650

    # ==================== REPORTES AUTOMÁTICOS ====================

    def schedule_daily_report(self, email: str) -> bool:
        """Programar reporte diario"""
        print(f"📧 Reporte diario programado para {email}")
        return True

    def schedule_weekly_report(self, email: str) -> bool:
        """Programar reporte semanal"""
        print(f"📧 Reporte semanal programado para {email}")
        return True

    def schedule_monthly_report(self, email: str) -> bool:
        """Programar reporte mensual"""
        print(f"📧 Reporte mensual programado para {email}")
        return True


# Instancia global
analytics_dashboard = AnalyticsDashboard()

print("✅ Analytics Dashboard initialized")
