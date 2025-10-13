"""
Gestor de caché para análisis de keywords
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class CacheManager:
    """Gestiona el caché de análisis de keywords"""
    
    def __init__(self, cache_dir: str = "data/cache", ttl_hours: int = 24):
        """
        Inicializa el gestor de caché
        
        Args:
            cache_dir: Directorio donde guardar el caché
            ttl_hours: Tiempo de vida del caché en horas
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_cache_key(self, data: Any) -> str:
        """Genera una clave única para el caché"""
        # Convertir data a string JSON y hashear
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Dict]:
        """
        Obtiene un análisis del caché
        
        Args:
            key: Clave del caché
            
        Returns:
            Análisis cacheado o None si no existe o expiró
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Verificar si expiró
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                # Expiró, eliminar
                cache_file.unlink()
                return None
            
            return cached_data['data']
            
        except Exception as e:
            print(f"Error leyendo caché: {e}")
            return None
    
    def set(self, key: str, data: Dict) -> bool:
        """
        Guarda un análisis en el caché
        
        Args:
            key: Clave del caché
            data: Datos a guardar
            
        Returns:
            True si se guardó correctamente
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'key': key,
                'data': data
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error guardando en caché: {e}")
            return False
    
    def list_analyses(self) -> List[Dict]:
        """
        Lista todos los análisis cacheados
        
        Returns:
            Lista de análisis con metadata
        """
        analyses = []
        
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    # Verificar si expiró
                    cached_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cached_time > self.ttl:
                        # Expiró, skip
                        continue
                    
                    # Extraer metadata
                    data = cached_data.get('data', {})
                    
                    analyses.append({
                        'key': cached_data.get('key', cache_file.stem),
                        'timestamp': cached_data.get('timestamp'),
                        'topics_count': len(data.get('topics', [])),
                        'provider': data.get('provider', 'unknown'),
                        'summary_preview': data.get('summary', '')[:100] + '...' if data.get('summary') else ''
                    })
                    
                except Exception as e:
                    print(f"Error procesando {cache_file}: {e}")
                    continue
            
            # Ordenar por timestamp descendente (más recientes primero)
            analyses.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            print(f"Error listando análisis: {e}")
        
        return analyses
    
    def delete(self, key: str) -> bool:
        """
        Elimina un análisis del caché
        
        Args:
            key: Clave del caché a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            if cache_file.exists():
                cache_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error eliminando caché: {e}")
            return False
    
    def clear_all(self) -> int:
        """
        Elimina todos los análisis cacheados
        
        Returns:
            Número de archivos eliminados
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
        except Exception as e:
            print(f"Error limpiando caché: {e}")
        
        return count
    
    def clear_expired(self) -> int:
        """
        Elimina solo los análisis expirados
        
        Returns:
            Número de archivos eliminados
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cached_time > self.ttl:
                        cache_file.unlink()
                        count += 1
                        
                except Exception:
                    # Si hay error leyendo, eliminar también
                    cache_file.unlink()
                    count += 1
                    
        except Exception as e:
            print(f"Error limpiando caché expirado: {e}")
        
        return count
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del caché
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            valid_count = 0
            expired_count = 0
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cached_time > self.ttl:
                        expired_count += 1
                    else:
                        valid_count += 1
                        
                except Exception:
                    expired_count += 1
            
            return {
                'total_analyses': len(cache_files),
                'valid_analyses': valid_count,
                'expired_analyses': expired_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': str(self.cache_dir.absolute())
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                'total_analyses': 0,
                'valid_analyses': 0,
                'expired_analyses': 0,
                'total_size_mb': 0,
                'cache_dir': str(self.cache_dir.absolute())
            }
    
    def get_cache_info(self) -> Dict:
        """
        Obtiene información resumida del caché para mostrar en UI
        
        Returns:
            Diccionario con métricas del caché para la interfaz
        """
        stats = self.get_stats()
        
        # Calcular hit rate (análisis válidos vs total)
        total = stats.get('total_analyses', 0)
        valid = stats.get('valid_analyses', 0)
        hit_rate = (valid / total * 100) if total > 0 else 0
        
        # Estimar costo ahorrado
        # Asumiendo ~$0.20 por análisis promedio
        cost_saved = valid * 0.20
        
        return {
            'cached_analyses': valid,
            'hit_rate': hit_rate,
            'cost_saved': cost_saved,
            'size_mb': stats.get('total_size_mb', 0),
            'total_analyses': total,
            'expired_analyses': stats.get('expired_analyses', 0)
        }


# Función helper para obtener instancia singleton (opcional)
_cache_manager_instance = None

def get_cache_manager(cache_dir: str = "data/cache", ttl_hours: int = 24) -> CacheManager:
    """
    Obtiene una instancia singleton del CacheManager
    
    Args:
        cache_dir: Directorio del caché
        ttl_hours: Tiempo de vida en horas
        
    Returns:
        Instancia de CacheManager
    """
    global _cache_manager_instance
    
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager(cache_dir, ttl_hours)
    
    return _cache_manager_instance
