"""
Backend Optimization - Redis, Caching, Query Optimization, Compression
Mejora de velocidad y escalabilidad
"""

import redis
import json
import gzip
import time
from functools import wraps
from typing import Optional, Any, Dict
import hashlib

# ==================== REDIS CACHE ====================

class RedisCache:
    """Gestor de caché con Redis"""

    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            self.available = True
            print("✅ Redis conectado")
        except Exception as e:
            print(f"⚠️ Redis no disponible: {e}")
            self.available = False
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché"""
        if not self.available:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"❌ Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Guardar valor en caché con TTL"""
        if not self.available:
            return False

        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"❌ Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Eliminar clave del caché"""
        if not self.available:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"❌ Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str):
        """Limpiar todas las claves que coincidan con patrón"""
        if not self.available:
            return

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                print(f"🗑️ Cleared {len(keys)} cache keys")
        except Exception as e:
            print(f"❌ Cache clear error: {e}")

    def get_stats(self) -> Dict:
        """Obtener estadísticas de Redis"""
        if not self.available:
            return {"status": "unavailable"}

        try:
            info = self.redis_client.info()
            return {
                "status": "available",
                "memory_used": info.get('used_memory_human'),
                "connected_clients": info.get('connected_clients'),
                "total_commands": info.get('total_commands_processed'),
            }
        except:
            return {"status": "unavailable"}


# ==================== DECORADOR DE CACHÉ ====================

cache = RedisCache()

def cached(ttl: int = 3600, key_prefix: str = "cache"):
    """Decorador para cachear resultados de funciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave única
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Intentar obtener del caché
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                print(f"💾 Cache hit: {cache_key}")
                return cached_value

            # Ejecutar función
            result = func(*args, **kwargs)

            # Guardar en caché
            cache.set(cache_key, result, ttl)
            print(f"💾 Cache set: {cache_key}")

            return result
        return wrapper
    return decorator

# ==================== COMPRESIÓN DE RESPUESTAS ====================

class ResponseCompression:
    """Comprimir respuestas HTTP para menor ancho de banda"""

    @staticmethod
    def compress_json(data: Dict) -> bytes:
        """Comprimir datos JSON con gzip"""
        json_str = json.dumps(data)
        return gzip.compress(json_str.encode('utf-8'))

    @staticmethod
    def decompress_json(compressed_data: bytes) -> Dict:
        """Descomprimir datos JSON"""
        return json.loads(gzip.decompress(compressed_data).decode('utf-8'))

    @staticmethod
    def get_compression_ratio(original_size: int, compressed_size: int) -> float:
        """Calcular ratio de compresión"""
        return (1 - compressed_size / original_size) * 100

# ==================== QUERY OPTIMIZATION ====================

class DatabaseOptimizer:
    """Optimizar queries a la base de datos"""

    @staticmethod
    @cached(ttl=300, key_prefix="advisor")
    def get_available_advisors_optimized():
        """Obtener asesores disponibles (caché 5 min)"""
        from database import get_available_advisors
        return get_available_advisors()

    @staticmethod
    @cached(ttl=600, key_prefix="requests")
    def get_pending_requests_optimized():
        """Obtener solicitudes pendientes (caché 10 min)"""
        from database import get_pending_advisor_requests
        return get_pending_advisor_requests()

    @staticmethod
    @cached(ttl=3600, key_prefix="stats")
    def get_analytics_optimized():
        """Obtener analytics (caché 1 hora)"""
        from advisor_enhanced import AdvancedAnalytics
        requests = DatabaseOptimizer.get_pending_requests_optimized()
        advisors = DatabaseOptimizer.get_available_advisors_optimized()
        return AdvancedAnalytics.get_system_analytics(requests, [], advisors)

    @staticmethod
    def invalidate_cache_on_update():
        """Limpiar caché cuando hay actualizaciones"""
        cache.clear_pattern("advisor:*")
        cache.clear_pattern("requests:*")
        cache.clear_pattern("stats:*")

# ==================== PAGINATION ====================

class Paginator:
    """Paginación inteligente para resultados"""

    @staticmethod
    def paginate(items: list, page: int = 1, per_page: int = 20) -> Dict:
        """Paginar lista de items"""
        total = len(items)
        total_pages = (total + per_page - 1) // per_page

        if page < 1 or page > total_pages:
            page = 1

        start = (page - 1) * per_page
        end = start + per_page
        items_page = items[start:end]

        return {
            "items": items_page,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

# ==================== LAZY LOADING ====================

class LazyLoader:
    """Cargar datos bajo demanda"""

    @staticmethod
    def get_advisor_profile_lazy(advisor_id: int, include_stats: bool = False):
        """Cargar perfil de asesor (sin stats por defecto)"""
        from database import get_user_by_id

        profile = get_user_by_id(advisor_id)

        if include_stats:
            # Cargar stats solo si se solicita
            profile['stats'] = DatabaseOptimizer.get_analytics_optimized()

        return profile

    @staticmethod
    def get_request_with_messages(request_id: int, limit: int = 50):
        """Obtener solicitud con últimos mensajes (lazy)"""
        from database import get_advisor_request, get_advisor_messages

        request_data = get_advisor_request(request_id)
        messages = get_advisor_messages(request_id)[-limit:]

        return {
            "request": request_data,
            "messages": messages,
            "total_messages": len(get_advisor_messages(request_id))
        }

# ==================== BATCH PROCESSING ====================

class BatchProcessor:
    """Procesar múltiples operaciones en batch"""

    @staticmethod
    def send_notifications_batch(user_ids: list, message: Dict) -> Dict:
        """Enviar notificaciones en batch (más eficiente)"""
        from notification_service import notification_service

        results = {
            "success": 0,
            "failed": 0,
            "details": []
        }

        for user_id in user_ids:
            try:
                result = notification_service.send_notification(
                    user_id,
                    message.get('type'),
                    **message.get('params', {})
                )
                if result.get('success'):
                    results["success"] += 1
                else:
                    results["failed"] += 1
                results["details"].append(result)
            except Exception as e:
                results["failed"] += 1
                results["details"].append({"error": str(e)})

        return results

    @staticmethod
    def create_appointments_batch(appointments_data: list) -> Dict:
        """Agendar múltiples citas en batch"""
        from calendar_service import calendar_service

        results = {
            "created": 0,
            "failed": 0,
            "appointments": []
        }

        for apt_data in appointments_data:
            result = calendar_service.schedule_appointment(**apt_data)
            if result.get('success'):
                results["created"] += 1
                results["appointments"].append(result['appointment'])
            else:
                results["failed"] += 1

        # Invalidar caché después de cambios
        DatabaseOptimizer.invalidate_cache_on_update()

        return results

# ==================== CONNECTION POOLING ====================

class ConnectionPool:
    """Pool de conexiones para BD"""

    _instance = None
    _connections = []
    _max_connections = 10

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._create_connections()

    def _create_connections(self):
        """Crear pool de conexiones"""
        for _ in range(self._max_connections):
            try:
                from database import get_db
                conn = get_db()
                self._connections.append({
                    'connection': conn,
                    'in_use': False,
                    'created_at': time.time()
                })
            except Exception as e:
                print(f"❌ Error creating connection: {e}")

    def get_connection(self):
        """Obtener conexión disponible del pool"""
        for conn_obj in self._connections:
            if not conn_obj['in_use']:
                conn_obj['in_use'] = True
                return conn_obj['connection']

        # Si no hay disponibles, crear una temporal
        from database import get_db
        return get_db()

    def return_connection(self, connection):
        """Devolver conexión al pool"""
        for conn_obj in self._connections:
            if conn_obj['connection'] == connection:
                conn_obj['in_use'] = False
                return True
        return False

    def get_stats(self) -> Dict:
        """Estadísticas del pool"""
        in_use = sum(1 for c in self._connections if c['in_use'])
        return {
            "total": len(self._connections),
            "in_use": in_use,
            "available": len(self._connections) - in_use
        }

# ==================== PERFORMANCE MONITORING ====================

class PerformanceMonitor:
    """Monitorear performance de operaciones"""

    _metrics = {}

    @staticmethod
    def measure(operation_name: str):
        """Decorador para medir tiempo de ejecución"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    # Registrar métrica
                    if operation_name not in PerformanceMonitor._metrics:
                        PerformanceMonitor._metrics[operation_name] = []

                    PerformanceMonitor._metrics[operation_name].append({
                        "time": execution_time,
                        "timestamp": time.time(),
                        "success": True
                    })

                    if execution_time > 1:
                        print(f"⚠️ Slow operation: {operation_name} took {execution_time:.2f}s")

                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    PerformanceMonitor._metrics[operation_name].append({
                        "time": execution_time,
                        "timestamp": time.time(),
                        "success": False,
                        "error": str(e)
                    })
                    raise
            return wrapper
        return decorator

    @staticmethod
    def get_metrics(operation_name: str = None) -> Dict:
        """Obtener métricas de performance"""
        if operation_name:
            metrics = PerformanceMonitor._metrics.get(operation_name, [])
        else:
            metrics = PerformanceMonitor._metrics

        # Calcular estadísticas
        stats = {}
        for op, measurements in (
            {operation_name: PerformanceMonitor._metrics.get(operation_name, [])}.items()
            if operation_name
            else metrics.items()
        ):
            if measurements:
                times = [m['time'] for m in measurements]
                stats[op] = {
                    "count": len(measurements),
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "total_time": sum(times),
                    "success_rate": sum(1 for m in measurements if m['success']) / len(measurements) * 100
                }

        return stats

# ==================== INSTANCIAS GLOBALES ====================

connection_pool = ConnectionPool.get_instance()
performance_monitor = PerformanceMonitor()

print("✅ Backend Optimization loaded")
