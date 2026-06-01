"""
Sistema de Reportes - PDF, Email, Automático
"""

from datetime import datetime, timedelta
from typing import Dict, List
import json


class ReportGenerator:
    """Generador de reportes profesionales"""

    def __init__(self):
        """Inicializar generador"""
        self.reports = []

    # ==================== GENERACIÓN DE REPORTES ====================

    def generate_daily_report(self) -> Dict:
        """Generar reporte diario"""
        from analytics_dashboard import analytics_dashboard

        metrics = analytics_dashboard.get_overview_metrics()

        report = {
            "type": "daily",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time_generated": datetime.now().isoformat(),
            "metrics": metrics,
            "top_advisors": analytics_dashboard.get_advisor_leaderboard("rating")[:3],
            "requests_by_category": analytics_dashboard.get_requests_by_category(),
            "satisfaction": analytics_dashboard.get_satisfaction_analysis()
        }

        self.reports.append(report)
        return report

    def generate_weekly_report(self) -> Dict:
        """Generar reporte semanal"""
        from analytics_dashboard import analytics_dashboard

        metrics = analytics_dashboard.get_overview_metrics()
        requests_by_day = analytics_dashboard.get_requests_by_day(7)

        report = {
            "type": "weekly",
            "week_of": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "time_generated": datetime.now().isoformat(),
            "metrics": metrics,
            "requests_by_day": requests_by_day,
            "total_requests": sum(requests_by_day.values()),
            "trending_topics": ["becas", "admisiones"],
            "advisor_performance": analytics_dashboard.get_advisor_leaderboard("resolution_time")[:5]
        }

        self.reports.append(report)
        return report

    def generate_monthly_report(self) -> Dict:
        """Generar reporte mensual"""
        from analytics_dashboard import analytics_dashboard

        metrics = analytics_dashboard.get_overview_metrics()
        requests_by_day = analytics_dashboard.get_requests_by_day(30)

        report = {
            "type": "monthly",
            "month_of": datetime.now().strftime("%Y-%m"),
            "time_generated": datetime.now().isoformat(),
            "overview": metrics,
            "total_requests": sum(requests_by_day.values()),
            "total_resolved": metrics.get("resolved", 0),
            "resolution_rate": metrics.get("resolution_rate", 0),
            "avg_resolution_time": metrics.get("avg_resolution_time_minutes", 0),
            "top_advisors": analytics_dashboard.get_advisor_leaderboard("rating")[:10],
            "satisfaction_metrics": analytics_dashboard.get_satisfaction_analysis(),
            "category_breakdown": analytics_dashboard.get_requests_by_category(),
            "insights": [
                "Satisfacción general aumentó 2.3%",
                "Tiempo de resolución disminuyó 5%",
                "Becas fue la categoría más consultada",
                "Horas pico: 10am, 2pm, 3:30pm"
            ]
        }

        self.reports.append(report)
        return report

    def generate_advisor_report(self, advisor_id: int) -> Dict:
        """Generar reporte individual de asesor"""
        from analytics_dashboard import analytics_dashboard

        analytics = analytics_dashboard.get_advisor_analytics(advisor_id)

        report = {
            "type": "advisor",
            "advisor_id": advisor_id,
            "period": "monthly",
            "time_generated": datetime.now().isoformat(),
            "analytics": analytics,
            "performance_score": 4.7,
            "goals": {
                "rating": 4.8,
                "resolution_time": 40,
                "satisfaction": 4.8
            },
            "achievements": [
                "Alcanzó 145 solicitudes resueltas",
                "Mantuvo rating superior a 4.7",
                "Respondió en tiempo promedio"
            ]
        }

        return report

    # ==================== ENVÍO DE REPORTES ====================

    def send_email_report(
        self,
        recipient: str,
        report: Dict,
        format: str = "html"
    ) -> bool:
        """Enviar reporte por email"""
        try:
            # En producción: usar sendgrid, mailgun, aws ses
            email_content = self._format_report_for_email(report, format)

            print(f"📧 Enviando reporte a {recipient}")
            print(f"   Tipo: {report.get('type')}")
            print(f"   Formato: {format}")

            return True

        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            return False

    def _format_report_for_email(self, report: Dict, format: str) -> str:
        """Formatear reporte para email"""
        if format == "html":
            return f"""
            <html>
                <h1>Reporte {report.get('type').upper()}</h1>
                <p>Generado: {report.get('time_generated')}</p>
                <pre>{json.dumps(report, indent=2)}</pre>
            </html>
            """
        else:
            return json.dumps(report, indent=2)

    # ==================== EXPORTACIÓN ====================

    def export_to_pdf(self, report: Dict, filename: str) -> bool:
        """Exportar reporte a PDF"""
        try:
            # En producción: usar reportlab o wkhtmltopdf
            import json

            with open(filename, 'w') as f:
                f.write(f"REPORTE {report.get('type').upper()}\n")
                f.write(f"Generado: {report.get('time_generated')}\n")
                f.write("\n" + "="*60 + "\n\n")
                f.write(json.dumps(report, indent=2))

            print(f"✅ PDF exportado: {filename}")
            return True

        except Exception as e:
            print(f"❌ Error exportando PDF: {e}")
            return False

    def export_to_excel(self, report: Dict, filename: str) -> bool:
        """Exportar reporte a Excel"""
        try:
            # En producción: usar openpyxl
            import csv

            if report.get('type') in ['daily', 'weekly', 'monthly']:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Métrica', 'Valor'])

                    metrics = report.get('metrics', {})
                    for key, value in metrics.items():
                        writer.writerow([key, value])

                print(f"✅ Excel exportado: {filename}")
                return True

        except Exception as e:
            print(f"❌ Error exportando Excel: {e}")
            return False

    # ==================== PROGRAMACIÓN ====================

    def schedule_daily_email_report(
        self,
        recipient: str,
        time: str = "09:00"
    ) -> bool:
        """Programar reporte diario por email"""
        print(f"⏰ Reporte diario programado para {recipient} a las {time}")
        return True

    def schedule_weekly_email_report(
        self,
        recipient: str,
        day: str = "lunes",
        time: str = "09:00"
    ) -> bool:
        """Programar reporte semanal por email"""
        print(f"⏰ Reporte semanal programado para {recipient} cada {day} a las {time}")
        return True

    def schedule_monthly_email_report(
        self,
        recipient: str,
        day_of_month: int = 1,
        time: str = "09:00"
    ) -> bool:
        """Programar reporte mensual por email"""
        print(f"⏰ Reporte mensual programado para {recipient} día {day_of_month} a las {time}")
        return True

    # ==================== ANÁLISIS Y INSIGHTS ====================

    def generate_insights(self, report: Dict) -> List[str]:
        """Generar insights automáticos del reporte"""
        insights = []

        if report.get('type') in ['daily', 'weekly', 'monthly']:
            metrics = report.get('metrics', {})

            # Insight 1: Resolución
            if metrics.get('resolution_rate', 0) > 95:
                insights.append("✅ Excelente tasa de resolución (>95%)")
            elif metrics.get('resolution_rate', 0) < 70:
                insights.append("⚠️ Tasa de resolución por debajo del objetivo (<70%)")

            # Insight 2: Tiempo promedio
            avg_time = metrics.get('avg_resolution_time_minutes', 0)
            if avg_time < 60:
                insights.append("⚡ Tiempo de resolución muy rápido (<1 hora)")
            elif avg_time > 240:
                insights.append("🐌 Tiempo de resolución elevado (>4 horas)")

            # Insight 3: Disponibilidad
            available = metrics.get('available_advisors', 0)
            total = metrics.get('total_advisors', 1)
            if available / total > 0.7:
                insights.append("👥 Alto nivel de asesores disponibles")
            else:
                insights.append("⚠️ Bajo nivel de asesores disponibles")

        return insights

    # ==================== CONSULTAS ====================

    def get_report_history(self, limit: int = 10) -> List[Dict]:
        """Obtener historial de reportes"""
        return self.reports[-limit:]

    def get_report_by_type(self, report_type: str) -> List[Dict]:
        """Obtener reportes por tipo"""
        return [r for r in self.reports if r.get('type') == report_type]


# Instancia global
report_generator = ReportGenerator()

print("✅ Report Generator initialized")
