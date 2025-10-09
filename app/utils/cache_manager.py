"""
Sistema de caché inteligente para análisis de keywords

"""

import hashlib
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Gestiona el sistema de caché para análisis de keywords"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.analyses_dir = self.cache_dir / "analyses"
        self.stats_file = self.cache_dir / "cache_stats.json"
        
        # Crear directorios
        self.analyses_dir.mkdir(parents=True, exist_ok=True)
        
        # Cargar o inicializar estadísticas
        self.stats = self._load_stats()
        
        logger.info(f"CacheManager inicializado en: {self.cache_dir}")
    
    def generate_hash(
        self,
        df: pd.DataFrame,
        analysis_type: str,
        num_tiers: int,
        custom_instructions: str = "",
        include_semantic: bool = True,
        include_trends: bool = True,
        include_gaps: bool = True
    ) -> str:
        """
        Genera hash único basado en datos y parámetros del análisis
        
        Args:
            df: DataFrame con keywords
            analysis_type: Tipo de análisis
            num_tiers: Número de tiers
            custom_instructions: Instrucciones personalizadas
            include_semantic: Si incluye análisis semántico
            include_trends: Si incluye detección de tendencias
            include_gaps: Si incluye detección de gaps
            
        Returns:
            Hash MD5 como string
        """
        # Componentes del hash
        components = {
            'keywords': sorted(df['keyword'].tolist()[:1000]),  # Top 1000 keywords ordenadas
            'volumes': df.nlargest(1000, 'volume')['volume'].tolist(),
            'analysis_type': analysis_type,
            'num_tiers': num_tiers,
            'custom_instructions': custom_instructions.strip(),
            'semantic': include_semantic,
            'trends': include_trends,
            'gaps': include_gaps
        }
        
        # Convertir a string determinista
        hash_string = json.dumps(components, sort_keys=True, ensure_ascii=False)
        
        # Generar hash MD5
        hash_md5 = hashlib.md5(hash_string.encode('utf-8')).hexdigest()
        
        logger.debug(f"Hash generado: {hash_md5}")
        return hash_md5
    
    def get_cached_analysis(
        self,
        cache_hash: str,
        ttl_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Recupera un análisis del caché si existe y es válido
        
        Args:
            cache_hash: Hash del análisis
            ttl_hours: Tiempo de vida en horas (0 = sin expiración)
            
        Returns:
            Resultado del análisis o None si no existe/expiró
        """
        result_file = self.analyses_dir / f"{cache_hash}.json"
        meta_file = self.analyses_dir / f"{cache_hash}.meta.json"
        
        # Verificar si existe
        if not result_file.exists() or not meta_file.exists():
            logger.debug(f"Cache miss: {cache_hash}")
            return None
        
        # Cargar metadata
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo metadata del caché: {e}")
            return None
        
        # Verificar TTL
        if ttl_hours > 0:
            cached_time = datetime.fromisoformat(meta['timestamp'])
            expiration_time = cached_time + timedelta(hours=ttl_hours)
            
            if datetime.now() > expiration_time:
                logger.info(f"Cache expirado: {cache_hash} (creado: {cached_time})")
                return None
        
        # Cargar resultado
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            # Actualizar estadísticas
            self.stats['hits'] += 1
            self.stats['credits_saved'] += meta.get('estimated_credits', 0)
            self.stats['cost_saved'] += meta.get('estimated_cost', 0)
            self._save_stats()
            
            logger.info(f"Cache hit: {cache_hash} | Provider: {meta.get('provider', 'unknown')}")
            
            # Añadir metadata al resultado
            result['_cache_metadata'] = {
                'cached': True,
                'timestamp': meta['timestamp'],
                'provider': meta.get('provider'),
                'model': meta.get('model'),
                'age_hours': (datetime.now() - cached_time).total_seconds() / 3600
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error cargando resultado del caché: {e}")
            return None
    
    def save_analysis(
        self,
        cache_hash: str,
        result: Dict[str, Any],
        provider: str,
        model: str,
        estimated_cost: float,
        estimated_credits: float,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Guarda un análisis en el caché
        
        Args:
            cache_hash: Hash del análisis
            result: Resultado del análisis
            provider: Proveedor de IA (Claude/OpenAI)
            model: Modelo usado
            estimated_cost: Costo estimado en $
            estimated_credits: Créditos estimados usados
            parameters: Parámetros del análisis
            
        Returns:
            True si se guardó exitosamente
        """
        result_file = self.analyses_dir / f"{cache_hash}.json"
        meta_file = self.analyses_dir / f"{cache_hash}.meta.json"
        
        # Metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'estimated_cost': estimated_cost,
            'estimated_credits': estimated_credits,
            'parameters': parameters,
            'hash': cache_hash
        }
        
        try:
            # Guardar resultado (sin metadata de caché)
            result_clean = {k: v for k, v in result.items() if not k.startswith('_cache')}
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_clean, f, ensure_ascii=False, indent=2)
            
            # Guardar metadata
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # Actualizar estadísticas
            self.stats['total_analyses'] += 1
            self.stats['total_cached'] += 1
            self.stats['last_save'] = datetime.now().isoformat()
            self._save_stats()
            
            logger.info(f"Análisis guardado en caché: {cache_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando en caché: {e}")
            return False
    
    def clear_cache(self, older_than_hours: Optional[int] = None) -> int:
        """
        Limpia el caché completamente o archivos antiguos
        
        Args:
            older_than_hours: Si se especifica, solo borra archivos más antiguos
            
        Returns:
            Número de archivos eliminados
        """
        deleted = 0
        
        for meta_file in self.analyses_dir.glob("*.meta.json"):
            should_delete = False
            
            if older_than_hours is None:
                should_delete = True
            else:
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    
                    cached_time = datetime.fromisoformat(meta['timestamp'])
                    age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                    
                    if age_hours > older_than_hours:
                        should_delete = True
                        
                except Exception as e:
                    logger.warning(f"Error leyendo {meta_file}: {e}")
                    should_delete = True  # Eliminar archivos corruptos
            
            if should_delete:
                cache_hash = meta_file.stem.replace('.meta', '')
                result_file = self.analyses_dir / f"{cache_hash}.json"
                
                try:
                    meta_file.unlink()
                    if result_file.exists():
                        result_file.unlink()
                    deleted += 1
                except Exception as e:
                    logger.error(f"Error eliminando archivos de caché: {e}")
        
        logger.info(f"Caché limpiado: {deleted} análisis eliminados")
        return deleted
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el estado del caché
        
        Returns:
            Diccionario con estadísticas del caché
        """
        # Contar archivos
        cached_files = list(self.analyses_dir.glob("*.json"))
        cached_analyses = len([f for f in cached_files if not f.name.endswith('.meta.json')])
        
        # Calcular tamaño
        total_size = sum(f.stat().st_size for f in cached_files)
        size_mb = total_size / (1024 * 1024)
        
        # Análisis más antiguo y más reciente
        meta_files = list(self.analyses_dir.glob("*.meta.json"))
        timestamps = []
        
        for meta_file in meta_files:
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    timestamps.append(datetime.fromisoformat(meta['timestamp']))
            except:
                continue
        
        oldest = min(timestamps) if timestamps else None
        newest = max(timestamps) if timestamps else None
        
        return {
            'total_analyses': self.stats.get('total_analyses', 0),
            'cached_analyses': cached_analyses,
            'cache_hits': self.stats.get('hits', 0),
            'hit_rate': (self.stats.get('hits', 0) / max(self.stats.get('total_analyses', 1), 1)) * 100,
            'credits_saved': self.stats.get('credits_saved', 0),
            'cost_saved': self.stats.get('cost_saved', 0),
            'size_mb': round(size_mb, 2),
            'oldest_cache': oldest.isoformat() if oldest else None,
            'newest_cache': newest.isoformat() if newest else None,
            'cache_directory': str(self.cache_dir)
        }
    
    def list_cached_analyses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lista los análisis en caché
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de análisis con metadata
        """
        analyses = []
        
        for meta_file in sorted(
            self.analyses_dir.glob("*.meta.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:limit]:
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                # Calcular edad
                cached_time = datetime.fromisoformat(meta['timestamp'])
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                
                analyses.append({
                    'hash': meta['hash'],
                    'timestamp': meta['timestamp'],
                    'age_hours': round(age_hours, 1),
                    'provider': meta.get('provider', 'unknown'),
                    'model': meta.get('model', 'unknown'),
                    'cost': meta.get('estimated_cost', 0),
                    'parameters': meta.get('parameters', {})
                })
                
            except Exception as e:
                logger.warning(f"Error leyendo metadata: {e}")
                continue
        
        return analyses
    
    def _load_stats(self) -> Dict[str, Any]:
        """Carga estadísticas del caché"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error cargando estadísticas: {e}")
        
        # Estadísticas por defecto
        return {
            'total_analyses': 0,
            'total_cached': 0,
            'hits': 0,
            'credits_saved': 0,
            'cost_saved': 0,
            'created': datetime.now().isoformat(),
            'last_save': None
        }
    
    def _save_stats(self):
        """Guarda estadísticas del caché"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")


# Instancia global del cache manager
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Obtiene la instancia global del cache manager"""
    global _cache_manager
    
    if _cache_manager is None:
        from config import CACHE_CONFIG
        cache_dir = CACHE_CONFIG.get('cache_dir', 'cache')
        _cache_manager = CacheManager(cache_dir)
    
    return _cache_manager
