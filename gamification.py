"""
Sistema de Gamification - Puntos, Badges, Leaderboards
"""

from datetime import datetime, timedelta
from typing import Dict, List


class GamificationEngine:
    """Motor de gamification para engagement"""

    # Definición de badges
    BADGES = {
        "first_chat": {"name": "Primer Chat", "icon": "🎯", "points": 10},
        "top_advisor": {"name": "Top Asesor", "icon": "⭐", "points": 100},
        "speed_demon": {"name": "Rápido", "icon": "⚡", "points": 50},
        "helpful": {"name": "Servicial", "icon": "💪", "points": 75},
        "consistent": {"name": "Consistente", "icon": "📈", "points": 80},
        "night_owl": {"name": "Nocturno", "icon": "🌙", "points": 40},
        "workaholic": {"name": "Trabajador", "icon": "💼", "points": 90},
        "team_player": {"name": "Trabajo en equipo", "icon": "👥", "points": 85},
    }

    def __init__(self):
        """Inicializar motor de gamification"""
        self.user_points = {}
        self.user_badges = {}
        self.leaderboards = {
            "daily": [],
            "weekly": [],
            "monthly": [],
            "all_time": []
        }

    # ==================== SISTEMA DE PUNTOS ====================

    def add_points(
        self,
        user_id: int,
        points: int,
        reason: str,
        metadata: Dict = None
    ) -> Dict:
        """Añadir puntos a usuario"""
        if user_id not in self.user_points:
            self.user_points[user_id] = {
                "total": 0,
                "transactions": [],
                "level": 1
            }

        transaction = {
            "timestamp": datetime.now().isoformat(),
            "points": points,
            "reason": reason,
            "metadata": metadata or {}
        }

        self.user_points[user_id]["total"] += points
        self.user_points[user_id]["transactions"].append(transaction)

        # Calcular nivel
        total = self.user_points[user_id]["total"]
        level = 1 + (total // 500)  # Cada 500 puntos = nuevo nivel
        self.user_points[user_id]["level"] = level

        print(f"🎯 {points} puntos para usuario {user_id}: {reason}")

        return {
            "user_id": user_id,
            "points_added": points,
            "total_points": self.user_points[user_id]["total"],
            "level": level,
            "reason": reason
        }

    def remove_points(self, user_id: int, points: int, reason: str) -> bool:
        """Remover puntos (castigo/ajuste)"""
        if user_id in self.user_points:
            self.user_points[user_id]["total"] = max(0, self.user_points[user_id]["total"] - points)
            print(f"⛔ {points} puntos removidos de usuario {user_id}: {reason}")
            return True

        return False

    def get_user_points(self, user_id: int) -> Dict:
        """Obtener información de puntos de usuario"""
        if user_id not in self.user_points:
            return {
                "user_id": user_id,
                "total": 0,
                "level": 1,
                "progress_to_next_level": 0
            }

        data = self.user_points[user_id]
        current_level = data["level"]
        current_total = data["total"]
        points_for_level = (current_level - 1) * 500
        points_to_next = (current_level * 500) - current_total

        return {
            "user_id": user_id,
            "total": current_total,
            "level": current_level,
            "progress_to_next_level": max(0, points_to_next),
            "rank": self._calculate_rank(user_id),
            "recent_transactions": data["transactions"][-5:]
        }

    # ==================== SISTEMA DE BADGES ====================

    def award_badge(self, user_id: int, badge_id: str) -> Dict:
        """Otorgar badge a usuario"""
        if badge_id not in self.BADGES:
            return {"success": False, "error": f"Badge {badge_id} not found"}

        if user_id not in self.user_badges:
            self.user_badges[user_id] = {
                "earned_badges": [],
                "total_badge_points": 0
            }

        badge_info = self.BADGES[badge_id]

        # Verificar si ya lo tiene
        if any(b["id"] == badge_id for b in self.user_badges[user_id]["earned_badges"]):
            return {
                "success": False,
                "message": f"Usuario ya tiene el badge {badge_id}"
            }

        badge_data = {
            "id": badge_id,
            "name": badge_info["name"],
            "icon": badge_info["icon"],
            "earned_at": datetime.now().isoformat(),
            "points": badge_info["points"]
        }

        self.user_badges[user_id]["earned_badges"].append(badge_data)
        self.user_badges[user_id]["total_badge_points"] += badge_info["points"]

        # Sumar puntos
        self.add_points(
            user_id,
            badge_info["points"],
            f"Badge earned: {badge_info['name']}"
        )

        print(f"🏆 Badge {badge_info['icon']} {badge_info['name']} otorgado a usuario {user_id}")

        return {
            "success": True,
            "badge": badge_data,
            "total_badges": len(self.user_badges[user_id]["earned_badges"])
        }

    def get_user_badges(self, user_id: int) -> Dict:
        """Obtener badges del usuario"""
        if user_id not in self.user_badges:
            return {
                "user_id": user_id,
                "earned_badges": [],
                "total_badge_points": 0
            }

        return {
            "user_id": user_id,
            "earned_badges": self.user_badges[user_id]["earned_badges"],
            "total_badge_points": self.user_badges[user_id]["total_badge_points"]
        }

    def check_badges_earned(self, user_id: int) -> List[str]:
        """Verificar badges que el usuario debería tener"""
        badges_to_earn = []

        # Badge: Primer chat
        if user_id in self.user_points and self.user_points[user_id]["total"] > 0:
            if not any(b["id"] == "first_chat" for b in self.user_badges.get(user_id, {}).get("earned_badges", [])):
                badges_to_earn.append("first_chat")

        # Badge: Workaholic (1000 puntos)
        if user_id in self.user_points and self.user_points[user_id]["total"] >= 1000:
            badges_to_earn.append("workaholic")

        # Badge: Top Advisor (4.8+ rating)
        # (Se verifica en contexto de aplicación)

        return badges_to_earn

    # ==================== LEADERBOARDS ====================

    def get_leaderboard(self, period: str = "monthly", limit: int = 10) -> List[Dict]:
        """Obtener leaderboard"""
        # En producción, obtener de BD con filtros temporales

        sorted_users = sorted(
            self.user_points.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )

        leaderboard = []
        for rank, (user_id, data) in enumerate(sorted_users[:limit], 1):
            badges = self.user_badges.get(user_id, {}).get("earned_badges", [])

            leaderboard.append({
                "rank": rank,
                "user_id": user_id,
                "points": data["total"],
                "level": data["level"],
                "badges_count": len(badges),
                "period": period
            })

        return leaderboard

    def get_user_rank(self, user_id: int, period: str = "monthly") -> Dict:
        """Obtener posición del usuario en leaderboard"""
        if user_id not in self.user_points:
            return {"rank": None, "message": "Usuario no tiene puntos"}

        leaderboard = self.get_leaderboard(period, limit=10000)

        for entry in leaderboard:
            if entry["user_id"] == user_id:
                return {
                    "rank": entry["rank"],
                    "total_users": len(leaderboard),
                    "points": entry["points"],
                    "level": entry["level"]
                }

        return {"rank": None, "message": "Usuario no en leaderboard"}

    # ==================== DESAFÍOS ====================

    def create_challenge(
        self,
        name: str,
        description: str,
        goal: int,
        reward_points: int,
        duration_days: int = 7
    ) -> Dict:
        """Crear desafío mensual/semanal"""
        challenge = {
            "id": f"CHALLENGE-{datetime.now().timestamp()}",
            "name": name,
            "description": description,
            "goal": goal,
            "reward_points": reward_points,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=duration_days)).isoformat(),
            "participants": []
        }

        print(f"🎯 Desafío creado: {name}")

        return challenge

    def get_active_challenges(self) -> List[Dict]:
        """Obtener desafíos activos"""
        return [
            {
                "id": "CH-001",
                "name": "Resuelve 50 Solicitudes",
                "description": "Resuelve 50 solicitudes en una semana",
                "goal": 50,
                "reward_points": 500,
                "progress": 35,
                "days_left": 3,
                "participants": 12
            },
            {
                "id": "CH-002",
                "name": "Rating 4.8+",
                "description": "Mantén un rating superior a 4.8",
                "goal": 4.8,
                "reward_points": 300,
                "progress": 4.6,
                "days_left": 7,
                "participants": 25
            },
            {
                "id": "CH-003",
                "name": "Rápido como el Rayo",
                "description": "Tiempo de respuesta promedio <30 segundos",
                "goal": 30,
                "reward_points": 250,
                "progress": 45,
                "days_left": 5,
                "participants": 8
            }
        ]

    def complete_challenge(self, user_id: int, challenge_id: str) -> bool:
        """Marcar desafío como completado"""
        print(f"✅ Desafío {challenge_id} completado por usuario {user_id}")

        # Otorgar recompensa
        self.add_points(user_id, 300, f"Challenge completed: {challenge_id}")

        return True

    # ==================== UTILIDADES ====================

    def _calculate_rank(self, user_id: int) -> int:
        """Calcular posición del usuario"""
        if user_id not in self.user_points:
            return None

        user_points = self.user_points[user_id]["total"]

        rank = 1
        for uid, data in self.user_points.items():
            if uid != user_id and data["total"] > user_points:
                rank += 1

        return rank

    def get_gamification_stats(self) -> Dict:
        """Obtener estadísticas de gamification"""
        total_users = len(self.user_points)
        total_points = sum(data["total"] for data in self.user_points.values())
        total_badges = sum(
            len(data.get("earned_badges", []))
            for data in self.user_badges.values()
        )

        return {
            "total_users": total_users,
            "total_points_distributed": total_points,
            "total_badges_earned": total_badges,
            "avg_points_per_user": round(total_points / total_users) if total_users > 0 else 0,
            "avg_badges_per_user": round(total_badges / total_users) if total_users > 0 else 0
        }


# Instancia global
gamification_engine = GamificationEngine()

print("✅ Gamification Engine initialized")
