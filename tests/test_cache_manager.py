"""
Tests unitarios para el sistema de caché
"""

import pytest
import pandas as pd
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.utils.cache_manager import CacheManager


@pytest.fixture
def sample_df():
    """DataFrame de ejemplo para tests"""
    return pd.DataFrame({
        'keyword': ['seo tools', 'keyword research', 'seo audit', 'backlink checker'],
        'volume': [10000, 8000, 5000, 3000],
        'traffic': [3000, 2400, 1500, 900]
    })


@pytest.fixture
def test_cache_dir(tmp_path):
    """Directorio temporal para tests"""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def cache_manager(test_cache_dir):
    """Instancia de CacheManager para tests"""
    return CacheManager(cache_dir=str(test_cache_dir))


class TestCacheManager:
    """Tests para CacheManager"""
    
    def test_initialization(self, cache_manager, test_cache_dir):
        """Test inicialización del cache manager"""
        assert cache_manager.cache_dir == test_cache_dir
        assert cache_manager.analyses_dir.exists()
        assert cache_manager.stats_file.exists()
    
    def test_generate_hash_consistency(self, cache_manager, sample_df):
        """Test que el hash es consistente para los mismos datos"""
        hash1 = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Temática (Topics)",
            num_tiers=3,
            custom_instructions="",
            include_semantic=True,
            include_trends=True,
            include_gaps=True
        )
        
        hash2 = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Temática (Topics)",
            num_tiers=3,
            custom_instructions="",
            include_semantic=True,
            include_trends=True,
            include_gaps=True
        )
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
    
    def test_generate_hash_different_params(self, cache_manager, sample_df):
        """Test que parámetros diferentes generan hashes diferentes"""
        hash1 = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Temática (Topics)",
            num_tiers=3
        )
        
        hash2 = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Intención de búsqueda",
            num_tiers=3
        )
        
        hash3 = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Temática (Topics)",
            num_tiers=5
        )
        
        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3
    
    def test_save_and_get_analysis(self, cache_manager, sample_df):
        """Test guardar y recuperar análisis del caché"""
        # Generar hash
        cache_hash = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Temática (Topics)",
            num_tiers=3
        )
        
        # Resultado de ejemplo
        result = {
            'summary': 'Análisis de ejemplo',
            'topics': [
                {
                    'topic': 'SEO Tools',
                    'tier': 1,
                    'keyword_count': 4,
                    'volume': 26000,
                    'traffic': 7800
                }
            ]
        }
        
        # Guardar
        saved = cache_manager.save_analysis(
            cache_hash=cache_hash,
            result=result,
            provider='Claude',
            model='claude-sonnet-4-5-20250929',
            estimated_cost=0.15,
            estimated_credits=15000,
            parameters={
                'analysis_type': 'Temática (Topics)',
                'num_tiers': 3
            }
        )
        
        assert saved is True
        
        # Recuperar
        cached_result = cache_manager.get_cached_analysis(cache_hash, ttl_hours=24)
        
        assert cached_result is not None
        assert cached_result['summary'] == result['summary']
        assert len(cached_result['topics']) == 1
        assert cached_result['topics'][0]['topic'] == 'SEO Tools'
        
        # Verificar metadata
        assert '_cache_metadata' in cached_result
        assert cached_result['_cache_metadata']['cached'] is True
        assert cached_result['_cache_metadata']['provider'] == 'Claude'
    
    def test_cache_miss(self, cache_manager):
        """Test cache miss cuando no existe el análisis"""
        fake_hash = "nonexistent_hash_123456"
        result = cache_manager.get_cached_analysis(fake_hash, ttl_hours=24)
        
        assert result is None
    
    def test_cache_expiration(self, cache_manager, sample_df, test_cache_dir):
        """Test expiración del caché por TTL"""
        cache_hash = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Temática (Topics)",
            num_tiers=3
        )
        
        result = {'summary': 'Test expiration'}
        
        # Guardar
        cache_manager.save_analysis(
            cache_hash=cache_hash,
            result=result,
            provider='Claude',
            model='test',
            estimated_cost=0.1,
            estimated_credits=1000,
            parameters={}
        )
        
        # Modificar timestamp para simular antigüedad
        meta_file = test_cache_dir / "analyses" / f"{cache_hash}.meta.json"
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        
        # Hacer que sea de hace 2 días
        old_timestamp = (datetime.now() - timedelta(days=2)).isoformat()
        meta['timestamp'] = old_timestamp
        
        with open(meta_file, 'w') as f:
            json.dump(meta, f)
        
        # Intentar recuperar con TTL de 24 horas (debería fallar)
        cached = cache_manager.get_cached_analysis(cache_hash, ttl_hours=24)
        assert cached is None
        
        # Intentar recuperar con TTL de 72 horas (debería funcionar)
        cached = cache_manager.get_cached_analysis(cache_hash, ttl_hours=72)
        assert cached is not None
    
    def test_clear_cache_all(self, cache_manager, sample_df):
        """Test limpiar todo el caché"""
        # Crear varios análisis
        for i in range(3):
            cache_hash = cache_manager.generate_hash(
                df=sample_df,
                analysis_type=f"Type {i}",
                num_tiers=i+1
            )
            
            cache_manager.save_analysis(
                cache_hash=cache_hash,
                result={'summary': f'Analysis {i}'},
                provider='Claude',
                model='test',
                estimated_cost=0.1,
                estimated_credits=1000,
                parameters={}
            )
        
        # Verificar que existen
        info = cache_manager.get_cache_info()
        assert info['cached_analyses'] == 3
        
        # Limpiar todo
        deleted = cache_manager.clear_cache()
        assert deleted == 3
        
        # Verificar que se eliminaron
        info = cache_manager.get_cache_info()
        assert info['cached_analyses'] == 0
    
    def test_clear_cache_older_than(self, cache_manager, sample_df, test_cache_dir):
        """Test limpiar solo archivos antiguos"""
        # Crear análisis reciente
        hash_recent = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Recent",
            num_tiers=3
        )
        
        cache_manager.save_analysis(
            cache_hash=hash_recent,
            result={'summary': 'Recent'},
            provider='Claude',
            model='test',
            estimated_cost=0.1,
            estimated_credits=1000,
            parameters={}
        )
        
        # Crear análisis antiguo
        hash_old = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Old",
            num_tiers=3
        )
        
        cache_manager.save_analysis(
            cache_hash=hash_old,
            result={'summary': 'Old'},
            provider='Claude',
            model='test',
            estimated_cost=0.1,
            estimated_credits=1000,
            parameters={}
        )
        
        # Hacer que el segundo sea antiguo
        meta_file = test_cache_dir / "analyses" / f"{hash_old}.meta.json"
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        
        old_timestamp = (datetime.now() - timedelta(days=10)).isoformat()
        meta['timestamp'] = old_timestamp
        
        with open(meta_file, 'w') as f:
            json.dump(meta, f)
        
        # Limpiar archivos con más de 7 días
        deleted = cache_manager.clear_cache(older_than_hours=168)
        assert deleted == 1
        
        # Verificar que solo queda el reciente
        info = cache_manager.get_cache_info()
        assert info['cached_analyses'] == 1
    
    def test_get_cache_info(self, cache_manager, sample_df):
        """Test obtener información del caché"""
        # Crear algunos análisis
        for i in range(2):
            cache_hash = cache_manager.generate_hash(
                df=sample_df,
                analysis_type=f"Type {i}",
                num_tiers=3
            )
            
            cache_manager.save_analysis(
                cache_hash=cache_hash,
                result={'summary': f'Analysis {i}'},
                provider='Claude',
                model='test',
                estimated_cost=0.15,
                estimated_credits=15000,
                parameters={}
            )
        
        # Simular un cache hit
        cache_hash = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Type 0",
            num_tiers=3
        )
        cache_manager.get_cached_analysis(cache_hash, ttl_hours=24)
        
        # Obtener info
        info = cache_manager.get_cache_info()
        
        assert info['cached_analyses'] == 2
        assert info['cache_hits'] >= 1
        assert info['cost_saved'] >= 0.15
        assert info['size_mb'] > 0
    
    def test_list_cached_analyses(self, cache_manager, sample_df):
        """Test listar análisis en caché"""
        # Crear análisis
        for i in range(5):
            cache_hash = cache_manager.generate_hash(
                df=sample_df,
                analysis_type=f"Type {i}",
                num_tiers=i+1
            )
            
            cache_manager.save_analysis(
                cache_hash=cache_hash,
                result={'summary': f'Analysis {i}'},
                provider='Claude' if i % 2 == 0 else 'OpenAI',
                model='test',
                estimated_cost=0.10 * (i+1),
                estimated_credits=10000 * (i+1),
                parameters={'num_tiers': i+1}
            )
        
        # Listar
        analyses = cache_manager.list_cached_analyses(limit=10)
        
        assert len(analyses) == 5
        assert all('hash' in a for a in analyses)
        assert all('timestamp' in a for a in analyses)
        assert all('provider' in a for a in analyses)
        
        # Verificar ordenamiento (más reciente primero)
        timestamps = [datetime.fromisoformat(a['timestamp']) for a in analyses]
        assert timestamps == sorted(timestamps, reverse=True)
    
    def test_stats_persistence(self, cache_manager, sample_df, test_cache_dir):
        """Test que las estadísticas persisten entre instancias"""
        # Crear análisis y cache hit
        cache_hash = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Test",
            num_tiers=3
        )
        
        cache_manager.save_analysis(
            cache_hash=cache_hash,
            result={'summary': 'Test'},
            provider='Claude',
            model='test',
            estimated_cost=0.15,
            estimated_credits=15000,
            parameters={}
        )
        
        cache_manager.get_cached_analysis(cache_hash, ttl_hours=24)
        
        # Obtener estadísticas
        info1 = cache_manager.get_cache_info()
        
        # Crear nueva instancia
        cache_manager2 = CacheManager(cache_dir=str(test_cache_dir))
        info2 = cache_manager2.get_cache_info()
        
        # Las estadísticas deben ser las mismas
        assert info1['cache_hits'] == info2['cache_hits']
        assert info1['cost_saved'] == info2['cost_saved']


class TestIntegration:
    """Tests de integración"""
    
    def test_full_workflow(self, cache_manager, sample_df):
        """Test del flujo completo: guardar, recuperar, limpiar"""
        # 1. Generar hash
        cache_hash = cache_manager.generate_hash(
            df=sample_df,
            analysis_type="Temática (Topics)",
            num_tiers=3,
            include_gaps=True
        )
        
        # 2. Verificar cache miss
        result = cache_manager.get_cached_analysis(cache_hash, ttl_hours=24)
        assert result is None
        
        # 3. Guardar análisis
        analysis_result = {
            'summary': 'Análisis completo',
            'topics': [
                {'topic': 'SEO', 'tier': 1, 'volume': 20000}
            ],
            'gaps': [
                {'topic': 'Link Building', 'volume': 5000}
            ]
        }
        
        saved = cache_manager.save_analysis(
            cache_hash=cache_hash,
            result=analysis_result,
            provider='Claude',
            model='claude-sonnet-4-5-20250929',
            estimated_cost=0.18,
            estimated_credits=18000,
            parameters={
                'analysis_type': 'Temática (Topics)',
                'num_tiers': 3,
                'include_gaps': True
            }
        )
        
        assert saved is True
        
        # 4. Verificar cache hit
        cached_result = cache_manager.get_cached_analysis(cache_hash, ttl_hours=24)
        assert cached_result is not None
        assert cached_result['summary'] == analysis_result['summary']
        assert '_cache_metadata' in cached_result
        
        # 5. Verificar estadísticas
        info = cache_manager.get_cache_info()
        assert info['cached_analyses'] >= 1
        assert info['cache_hits'] >= 1
        assert info['cost_saved'] >= 0.18
        
        # 6. Limpiar
        deleted = cache_manager.clear_cache()
        assert deleted >= 1
        
        # 7. Verificar que se limpió
        info = cache_manager.get_cache_info()
        assert info['cached_analyses'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
