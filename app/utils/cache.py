"""
Sistema de caché persistente para evitar llamadas duplicadas a la API

Este módulo permite guardar resultados de análisis en disco para reutilizarlos
sin gastar créditos de API cuando se realizan análisis idénticos.
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd


class AnalysisCache:
    """Gestiona caché de análisis para evitar gastos innecesarios de API"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Inicializa el sistema de caché
        
        Args:
            cache_dir: Directorio donde guardar el caché
            ttl_hours: Tiempo de vida del caché en horas (por defecto 24h)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_hours = ttl_hours
    
    def _generate_cache_key(
        self, 
        df: pd.DataFrame, 
        analysis_type: str,
        num_tiers: int,
        custom_instructions: str
    ) -> str:
        """
        Genera un hash único para esta consulta específica
        
        Args:
            df: DataFrame con las keywords
            analysis_type: Tipo de análisis (Temática, Intención, Funnel)
            num_tiers: Número de tiers solicitados
            custom_instructions: Instrucciones personalizadas del usuario
        
        Returns:
            Hash MD5 único que identifica esta consulta
        """
        
        # Crear string representativo de la consulta
        cache_data = {
            'keywords_hash': hashlib.md5(
                ''.join(sorted(df['keyword'].head(100))).encode()
            ).hexdigest(),
            'total_keywords': len(df),
            'total_volume': int(df['volume'].sum()),
            'analysis_type': analysis_type,
            'num_tiers': num_tiers,
            'custom_instructions': custom_instructions
        }
        
        # Generar hash único
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(
        self,
        df: pd.DataFrame,
        analysis_type: str,
        num_tiers: int,
        custom_instructions: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Intenta recuperar resultado del caché
        
        Args:
            df: DataFrame con las keywords
            analysis_type: Tipo de análisis
            num_tiers: Número de tiers
            custom_instructions: Instrucciones personalizadas
        
        Returns:
            Diccionario con el resultado si existe, None si no está en caché
        """
        
        cache_key = self._generate_cache_key(
            df, analysis_type, num_tiers, custom_instructions
        )
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Verificar si existe
        if not cache_file.exists():
            return None
        
        # Verificar TTL (Time To Live)
        file_age = datetime.now() - datetime.fromtimestamp(
            cache_file.stat().st_mtime
        )
        
        if file_age > timedelta(hours=self.ttl_hours):
            # Caché expirado - eliminarlo
            cache_file.unlink()
            return None
        
        # Leer caché
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            print(f"✅ Resultado encontrado en caché (guardado hace {file_age})")
            return cached_data
            
        except Exception as e:
            print(f"⚠️ Error leyendo caché: {e}")
            return None
    
    def set(
        self,
        df: pd.DataFrame,
        analysis_type: str,
        num_tiers: int,
        custom_instructions: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Guarda resultado en caché
        
        Args:
            df: DataFrame con las keywords
            analysis_type: Tipo de análisis
            num_tiers: Número de tiers
            custom_instructions: Instrucciones personalizadas
            result: Resultado del análisis a guardar
        """
        
        cache_key = self._generate_cache_key(
            df, analysis_type, num_tiers, custom_instructions
        )
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Añadir metadata
        cached_data = {
            'cached_at': datetime.now().isoformat(),
            'ttl_hours': self.ttl_hours,
            'result': result
        }
        
        # Guardar
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Resultado guardado en caché: {cache_key}")
            
        except Exception as e:
            print(f"⚠️ Error guardando caché: {e}")
    
    def clear(self, older_than_hours: Optional[int] = None) -> int:
        """
        Limpia caché antiguo
        
        Args:
            older_than_hours: Si se especifica, solo elimina caché más antiguo que esto.
                            Si es None, elimina todo el caché.
        
        Returns:
            Número de archivos eliminados
        """
        
        deleted = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            file_age = datetime.now() - datetime.fromtimestamp(
                cache_file.stat().st_mtime
            )
            
            should_delete = (
                older_than_hours is None or 
                file_age > timedelta(hours=older_than_hours)
            )
            
            if should_delete:
                cache_file.unlink()
                deleted += 1
        
        return deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché
        
        Returns:
            Diccionario con estadísticas del caché
        """
        
        cache_files = list(self.cache_dir.glob("*.json"))
        
        if not cache_files:
            return {
                'total_cached': 0,
                'total_size_mb': 0,
                'oldest_cache': None,
                'newest_cache': None
            }
        
        # Calcular tamaño total
        total_size = sum(f.stat().st_size for f in cache_files)
        
        # Fechas
        oldest = min(f.stat().st_mtime for f in cache_files)
        newest = max(f.stat().st_mtime for f in cache_files)
        
        return {
            'total_cached': len(cache_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'oldest_cache': datetime.fromtimestamp(oldest).isoformat(),
            'newest_cache': datetime.fromtimestamp(newest).isoformat()
        }


# ============================================
# EJEMPLO DE USO
# ============================================

def example_usage():
    """Ejemplo de cómo usar el sistema de caché"""
    
    # Crear instancia de caché
    cache = AnalysisCache(cache_dir="cache", ttl_hours=24)
    
    # Datos de ejemplo
    df = pd.DataFrame({
        'keyword': ['seo tools', 'keyword research', 'backlink checker'],
        'volume': [10000, 8000, 5000]
    })
    
    # Intentar recuperar del caché
    result = cache.get(
        df=df,
        analysis_type="Temática (Topics)",
        num_tiers=3,
        custom_instructions=""
    )
    
    if result:
        print("✅ ¡Encontrado en caché! No se gastaron créditos.")
        print(f"Resultado: {result['result']}")
    else:
        print("❌ No en caché. Realizar análisis nuevo...")
        
        # Simular análisis con IA
        result = {
            'summary': 'Análisis de ejemplo',
            'topics': [
                {'topic': 'SEO Tools', 'tier': 1, 'volume': 10000}
            ]
        }
        
        # Guardar en caché para próxima vez
        cache.set(
            df=df,
            analysis_type="Temática (Topics)",
            num_tiers=3,
            custom_instructions="",
            result=result
        )
        print("💾 Guardado en caché")
    
    # Ver estadísticas
    stats = cache.get_stats()
    print(f"\n📊 Estadísticas del caché:")
    print(f"  - Análisis guardados: {stats['total_cached']}")
    print(f"  - Espacio usado: {stats['total_size_mb']} MB")
    
    # Limpiar caché antiguo (>24h)
    deleted = cache.clear(older_than_hours=24)
    print(f"\n🗑️ Archivos eliminados: {deleted}")


if __name__ == "__main__":
    example_usage()
