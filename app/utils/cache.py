"""
Sistema de caché persistente para evitar llamadas duplicadas a la API

Añade este archivo como: app/utils/cache.py
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd

class AnalysisCache:
    """Gestiona caché de análisis para evitar gastos innecesarios"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
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
        """Genera un hash único para esta consulta"""
        
        # Crear string representativo
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
        
        # Generar hash
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(
        self,
        df: pd.DataFrame,
        analysis_type: str,
        num_tiers: int,
        custom_instructions: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Intenta recuperar resultado del caché"""
        
        cache_key = self._generate_cache_key(
            df, analysis_type, num_tiers, custom_instructions
        )
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Verificar si existe
        if not cache_file.exists():
            return None
        
        # Verificar TTL
        file_age = datetime.now() - datetime.fromtimestamp(
            cache_file.stat().st_mtime
        )
        
        if file_age > timedelta(hours=self.ttl_hours):
            # Caché expirado
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
        """Guarda resultado en caché"""
        
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
        """Limpia caché antiguo"""
        
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
        """Obtiene estadísticas del caché"""
        
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
# CÓMO USAR EN app/main.py
# ============================================

"""
# 1. Importar al inicio de app/main.py
from app.utils.cache import AnalysisCache

# 2. Inicializar (después de st.set_page_config)
if 'cache' not in st.session_state:
    st.session_state.cache = AnalysisCache(
        cache_dir="cache",
        ttl_hours=24  # Caché válido por 24 horas
    )

# 3. En la sidebar, añadir stats de caché
with st.sidebar:
    with st.expander("💾 Estado del Caché"):
        stats = st.session_state.cache.get_stats()
        st.metric("Análisis guardados", stats['total_cached'])
        st.metric("Espacio usado", f"{stats['total_size_mb']} MB")
        
        if st.button("🗑️ Limpiar caché antiguo"):
            deleted = st.session_state.cache.clear(older_than_hours=24)
            st.success(f"✅ {deleted} análisis eliminados")

# 4. ANTES de llamar a la API, buscar en caché
if st.button("🚀 Analizar con IA"):
    
    # Intentar recuperar del caché
    cached_result = st.session_state.cache.get(
        df=df,
        analysis_type=analysis_type,
        num_tiers=num_tiers,
        custom_instructions=custom_instructions
    )
    
    if cached_result:
        # ¡Encontrado! No gastar créditos
        st.info("💾 Resultado recuperado del caché (no se gastaron créditos)")
        result = cached_result['result']
        
    else:
        # No en caché, hacer análisis nuevo
        with st.spinner("🧠 Analizando..."):
            # ... tu código actual de análisis ...
            result = anthropic_service.analyze_keywords(prompt, df)
            
            # Guardar en caché para próxima vez
            st.session_state.cache.set(
                df=df,
                analysis_type=analysis_type,
                num_tiers=num_tiers,
                custom_instructions=custom_instructions,
                result=result
            )
    
    # Continuar normalmente...
    st.session_state.keyword_universe = result
"""


# ============================================
# EJEMPLO DE USO STANDALONE
# ============================================

def example_usage():
    """Ejemplo de cómo usar el caché"""
    
    # Crear caché
    cache = AnalysisCache(cache_dir="cache", ttl_hours=24)
    
    # Datos de ejemplo
    df = pd.DataFrame({
        'keyword': ['seo tools', 'keyword research'],
        'volume': [10000, 8000]
    })
    
    # Intentar recuperar
    result = cache.get(
        df=df,
        analysis_type="Temática",
        num_tiers=3,
        custom_instructions=""
    )
    
    if result:
        print("✅ Encontrado en caché!")
    else:
        print("❌ No en caché, hacer análisis...")
        
        # Simular análisis
        result = {
            'summary': 'Análisis de ejemplo',
            'topics': []
        }
        
        # Guardar
        cache.set(
            df=df,
            analysis_type="Temática",
            num_tiers=3,
            custom_instructions="",
            result=result
        )
        print("💾 Guardado en caché")
    
    # Ver stats
    stats = cache.get_stats()
    print(f"\n📊 Stats: {stats}")


if __name__ == "__main__":
    example_usage()
