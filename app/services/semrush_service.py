"""
Servicio optimizado para Semrush API con:
- Caché inteligente
- Rate limiting avanzado
- Retry logic
- Batch optimization
- Monitoreo de créditos
"""

import requests
import pandas as pd
from typing import List, Dict, Optional, Tuple
import time
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
import threading
from collections import deque
import logging

logger = logging.getLogger(__name__)


class SemrushCache:
    """Sistema de caché local para respuestas de Semrush"""
    
    def __init__(self, cache_dir: str = "data/cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.stats = {'hits': 0, 'misses': 0, 'saves': 0}
    
    def _get_cache_key(self, domain: str, params: Dict) -> str:
        """Genera un hash único para la request"""
        key_string = f"{domain}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, domain: str, params: Dict) -> Optional[pd.DataFrame]:
        """Obtiene datos del caché si existen y no han expirado"""
        cache_key = self._get_cache_key(domain, params)
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        
        if cache_file.exists():
            # Verificar expiración
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - file_time < self.ttl:
                try:
                    df = pd.read_parquet(cache_file)
                    self.stats['hits'] += 1
                    logger.info(f"✓ Cache HIT para {domain}")
                    return df
                except Exception as e:
                    logger.warning(f"Error leyendo caché: {e}")
        
        self.stats['misses'] += 1
        return None
    
    def set(self, domain: str, params: Dict, data: pd.DataFrame):
        """Guarda datos en caché"""
        cache_key = self._get_cache_key(domain, params)
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        
        try:
            data.to_parquet(cache_file, compression='gzip')
            self.stats['saves'] += 1
            logger.info(f"✓ Guardado en caché: {domain}")
        except Exception as e:
            logger.warning(f"Error guardando en caché: {e}")
    
    def clear_old(self):
        """Limpia archivos de caché expirados"""
        removed = 0
        for cache_file in self.cache_dir.glob("*.parquet"):
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - file_time > self.ttl:
                cache_file.unlink()
                removed += 1
        
        logger.info(f"✓ Limpiados {removed} archivos de caché expirados")
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas de caché"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.1f}%"
        }


class RateLimiter:
    """Rate limiter inteligente con sliding window"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = deque()
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Espera si se ha alcanzado el límite de rate"""
        with self.lock:
            now = time.time()
            
            # Limpiar requests fuera de la ventana
            while self.requests and self.requests[0] < now - self.window:
                self.requests.popleft()
            
            # Si hemos alcanzado el límite, esperar
            if len(self.requests) >= self.max_requests:
                sleep_time = self.requests[0] + self.window - now + 0.1
                if sleep_time > 0:
                    logger.info(f"⏳ Rate limit alcanzado. Esperando {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                    # Limpiar de nuevo después de esperar
                    self.requests.clear()
            
            # Registrar esta request
            self.requests.append(now)


class SemrushServiceOptimized:
    """Servicio optimizado para Semrush API"""
    
    BASE_URL = "https://api.semrush.com/"
    
    def __init__(
        self, 
        api_key: str,
        enable_cache: bool = True,
        cache_ttl_hours: int = 24,
        max_requests_per_minute: int = 10,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.params = {'key': self.api_key}
        
        # Cache
        self.cache = SemrushCache(ttl_hours=cache_ttl_hours) if enable_cache else None
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            max_requests=max_requests_per_minute,
            window_seconds=60
        )
        
        # Retry configuration
        self.max_retries = max_retries
        self.retry_delay = 2  # segundos base
        
        # Stats
        self.stats = {
            'requests_made': 0,
            'requests_cached': 0,
            'requests_failed': 0,
            'total_keywords_fetched': 0,
            'credits_used_estimate': 0
        }
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Ejecuta función con retry exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"⚠️ Intento {attempt + 1} falló: {e}. Reintentando en {wait_time}s...")
                time.sleep(wait_time)
    
    def get_organic_keywords(
        self, 
        domain: str, 
        limit: int = 5000,
        database: str = "us",
        filter_branded: bool = True,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Obtiene keywords orgánicas con caché y optimizaciones
        
        Args:
            domain: Dominio a analizar
            limit: Número máximo (hasta 10,000 para aprovechar el límite)
            database: Base de datos de Semrush
            filter_branded: Filtrar keywords con nombre del dominio
            force_refresh: Forzar consulta sin usar caché
        """
        
        # Limitar al máximo permitido por Semrush
        limit = min(limit, 10000)
        
        params = {
            'type': 'domain_organic',
            'database': database,
            'display_limit': limit,
            'filter_branded': filter_branded
        }
        
        # Intentar obtener del caché primero
        if self.cache and not force_refresh:
            cached_data = self.cache.get(domain, params)
            if cached_data is not None:
                self.stats['requests_cached'] += 1
                return cached_data
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Hacer request con retry
        try:
            df = self._retry_with_backoff(
                self._fetch_organic_keywords,
                domain, params
            )
            
            # Guardar en caché
            if self.cache:
                self.cache.set(domain, params, df)
            
            # Stats
            self.stats['requests_made'] += 1
            self.stats['total_keywords_fetched'] += len(df)
            self.stats['credits_used_estimate'] += self._estimate_credits(limit)
            
            return df
            
        except Exception as e:
            self.stats['requests_failed'] += 1
            logger.error(f"❌ Error obteniendo keywords de {domain}: {str(e)}")
            raise
    
    def _fetch_organic_keywords(self, domain: str, params: Dict) -> pd.DataFrame:
        """Realiza la request HTTP a Semrush"""
        request_params = {
            **params,
            'domain': domain,
            'export_columns': 'Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td',
            'display_sort': 'tr_desc'
        }
        
        response = self.session.get(self.BASE_URL, params=request_params, timeout=30)
        response.raise_for_status()
        
        # Parsear respuesta
        lines = response.text.strip().split('\n')
        
        if len(lines) < 2:
            raise ValueError(f"No se encontraron datos para {domain}")
        
        header = lines[0].split(';')
        data = [line.split(';') for line in lines[1:]]
        
        df = pd.DataFrame(data, columns=header)
        
        # Normalizar columnas
        df = self._normalize_columns(df)
        
        # Filtrar branded si es necesario
        if params.get('filter_branded'):
            domain_name = domain.split('.')[0].lower()
            df = df[~df['keyword'].str.lower().str.contains(domain_name)]
        
        # Añadir metadata
        df['source'] = domain
        df['database'] = params.get('database', 'us')
        df['fetched_at'] = datetime.now()
        
        return df
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza columnas y tipos de datos"""
        column_mapping = {
            'Keyword': 'keyword',
            'Position': 'position',
            'Previous Position': 'prev_position',
            'Position Difference': 'position_diff',
            'Search Volume': 'volume',
            'CPC': 'cpc',
            'URL': 'url',
            'Traffic': 'traffic',
            'Traffic (%)': 'traffic_pct',
            'Traffic Cost': 'traffic_cost',
            'Number of Results': 'serp_results',
            'Trends': 'trends'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Convertir tipos
        numeric_columns = [
            'position', 'prev_position', 'position_diff', 
            'volume', 'cpc', 'traffic', 'traffic_pct', 
            'traffic_cost', 'serp_results'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    
    def batch_get_keywords(
        self, 
        domains: List[str], 
        limit: int = 5000,
        delay: float = 1.0
    ) -> pd.DataFrame:
        """
        Obtiene keywords de múltiples dominios (versión secuencial compatible)
        
        Este método mantiene compatibilidad con código existente pero usa
        internamente las optimizaciones del servicio (caché, rate limiting, etc)
        
        Args:
            domains: Lista de dominios
            limit: Keywords por dominio
            delay: Delay entre requests (ignorado, usamos rate limiter interno)
        
        Returns:
            DataFrame con todas las keywords combinadas y deduplicadas
        """
        all_keywords = []
        failed_domains = []
        
        for domain in domains:
            try:
                logger.info(f"🔍 Obteniendo keywords de {domain}...")
                keywords = self.get_organic_keywords(domain, limit=limit)
                all_keywords.append(keywords)
                logger.info(f"✓ {domain}: {len(keywords)} keywords")
                
            except Exception as e:
                logger.error(f"✗ Error con {domain}: {str(e)}")
                failed_domains.append(domain)
                continue
        
        if failed_domains:
            logger.warning(f"⚠️ Dominios fallidos: {', '.join(failed_domains)}")
        
        if not all_keywords:
            raise ValueError("No se pudieron obtener keywords de ningún dominio")
        
        # Combinar todos los DataFrames
        combined = pd.concat(all_keywords, ignore_index=True)
        
        # Deduplicar keywords manteniendo la de mayor volumen
        combined = combined.sort_values('volume', ascending=False)
        combined = combined.drop_duplicates(subset=['keyword'], keep='first')
        
        logger.info(f"✅ Total: {len(combined)} keywords únicas de {len(domains)} dominios")
        
        return combined
    
    def batch_get_keywords_parallel(
        self, 
        domains: List[str], 
        limit: int = 5000,
        max_workers: int = 3
    ) -> pd.DataFrame:
        """
        Obtiene keywords de múltiples dominios en paralelo (respetando rate limits)
        
        Args:
            domains: Lista de dominios
            limit: Keywords por dominio
            max_workers: Número máximo de workers paralelos
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        all_keywords = []
        failed_domains = []
        
        # Limitar workers para respetar rate limits
        max_workers = min(max_workers, 3)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submitir todos los dominios
            future_to_domain = {
                executor.submit(self.get_organic_keywords, domain, limit): domain
                for domain in domains
            }
            
            # Procesar resultados a medida que completan
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    keywords = future.result()
                    all_keywords.append(keywords)
                    logger.info(f"✓ {domain}: {len(keywords)} keywords")
                except Exception as e:
                    logger.error(f"✗ Error con {domain}: {str(e)}")
                    failed_domains.append(domain)
        
        if failed_domains:
            logger.warning(f"⚠️ Dominios fallidos: {', '.join(failed_domains)}")
        
        if not all_keywords:
            raise ValueError("No se pudieron obtener keywords de ningún dominio")
        
        # Combinar y deduplicar
        combined = pd.concat(all_keywords, ignore_index=True)
        
        # Deduplicar keywords manteniendo la de mayor volumen
        combined = combined.sort_values('volume', ascending=False)
        combined = combined.drop_duplicates(subset=['keyword'], keep='first')
        
        return combined
    
    def get_domain_overview(self, domain: str, database: str = "us") -> Dict:
        """Obtiene overview del dominio (versión simple sin caché)"""
        
        self.rate_limiter.wait_if_needed()
        
        params = {
            'type': 'domain_ranks',
            'domain': domain,
            'database': database,
            'export_columns': 'Dn,Rk,Or,Ot,Oc,Ad,At,Ac'
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return {}
            
            header = lines[0].split(';')
            data = lines[1].split(';')
            overview = dict(zip(header, data))
            
            result = {
                'domain': overview.get('Domain', domain),
                'rank': int(overview.get('Rank', 0)),
                'organic_keywords': int(overview.get('Organic Keywords', 0)),
                'organic_traffic': int(overview.get('Organic Traffic', 0)),
                'organic_cost': float(overview.get('Organic Cost', 0)),
            }
            
            self.stats['requests_made'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo overview de {domain}: {str(e)}")
            return {}
    
    def get_domain_overview_cached(
        self, 
        domain: str, 
        database: str = "us"
    ) -> Dict:
        """Overview del dominio con caché agresivo (cambia raramente)"""
        
        cache_key = f"overview_{domain}_{database}"
        
        # Intentar caché primero (TTL de 7 días para overviews)
        if self.cache:
            cache_file = self.cache.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if datetime.now() - file_time < timedelta(days=7):
                    with open(cache_file, 'r') as f:
                        return json.load(f)
        
        # Obtener fresh data
        result = self.get_domain_overview(domain, database)
        
        if result:
            result['fetched_at'] = datetime.now().isoformat()
            
            # Guardar en caché
            if self.cache:
                cache_file = self.cache.cache_dir / f"{cache_key}.json"
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
        
        return result
    
    def get_keyword_overview(self, keyword: str, database: str = "us") -> Dict:
        """Obtiene información detallada de una keyword"""
        
        self.rate_limiter.wait_if_needed()
        
        try:
            params = {
                'type': 'phrase_this',
                'phrase': keyword,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co,Nr,Td'
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return {}
            
            header = lines[0].split(';')
            data = lines[1].split(';')
            
            info = dict(zip(header, data))
            
            return {
                'keyword': info.get('Keyword', keyword),
                'volume': int(info.get('Search Volume', 0)),
                'cpc': float(info.get('CPC', 0)),
                'competition': float(info.get('Competition', 0)),
                'results': int(info.get('Number of Results', 0)),
                'trends': info.get('Trends', '')
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo info de keyword '{keyword}': {str(e)}")
            return {}
    
    def get_competitors(
        self, 
        domain: str, 
        database: str = "us",
        limit: int = 10
    ) -> pd.DataFrame:
        """Obtiene competidores orgánicos del dominio"""
        
        self.rate_limiter.wait_if_needed()
        
        try:
            params = {
                'type': 'domain_organic_organic',
                'domain': domain,
                'database': database,
                'display_limit': limit,
                'export_columns': 'Dn,Cr,Np,Or,Ot,Oc,Ad'
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return pd.DataFrame()
            
            header = lines[0].split(';')
            data = [line.split(';') for line in lines[1:]]
            
            df = pd.DataFrame(data, columns=header)
            
            # Renombrar columnas
            column_mapping = {
                'Domain': 'competitor',
                'Competition Relevance': 'relevance',
                'Common Keywords': 'common_keywords',
                'Organic Keywords': 'organic_keywords',
                'Organic Traffic': 'organic_traffic',
                'Organic Cost': 'organic_cost',
                'Adwords Keywords': 'adwords_keywords'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Convertir tipos
            numeric_cols = ['relevance', 'common_keywords', 'organic_keywords', 
                          'organic_traffic', 'organic_cost', 'adwords_keywords']
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            self.stats['requests_made'] += 1
            
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo competidores de {domain}: {str(e)}")
            return pd.DataFrame()
    
    def _estimate_credits(self, keywords_count: int) -> int:
        """Estima créditos usados (Semrush cobra por 10 rows)"""
        return max(1, keywords_count // 10)
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas de uso"""
        stats = {
            **self.stats,
            'cache_stats': self.cache.get_stats() if self.cache else None
        }
        
        if self.cache:
            cache_stats = self.cache.get_stats()
            stats['cache_hit_rate'] = cache_stats['hit_rate']
            stats['cache_saves_credits'] = cache_stats['hits'] * 10  # Estimado
        
        return stats
    
    def clear_cache(self):
        """Limpia el caché completamente"""
        if self.cache:
            for cache_file in self.cache.cache_dir.glob("*"):
                cache_file.unlink()
            logger.info("✓ Caché limpiado completamente")
    
    def optimize_batch_requests(
        self, 
        domains: List[str],
        target_keywords: int = 5000
    ) -> Tuple[List[str], int]:
        """
        Optimiza el número de keywords a pedir por dominio para no exceder target
        
        Returns:
            (domains_to_fetch, keywords_per_domain)
        """
        # Obtener overviews primero (rápido con caché)
        overviews = []
        for domain in domains:
            try:
                overview = self.get_domain_overview_cached(domain)
                if overview:
                    overviews.append({
                        'domain': domain,
                        'keywords': overview.get('organic_keywords', 0)
                    })
            except Exception as e:
                logger.warning(f"No se pudo obtener overview de {domain}: {e}")
        
        if not overviews:
            # Fallback: dividir equitativamente
            keywords_per_domain = target_keywords // len(domains)
            return domains, keywords_per_domain
        
        # Ordenar por número de keywords (obtener más de los que tienen menos)
        overviews.sort(key=lambda x: x['keywords'])
        
        # Calcular cuántos keywords pedir de cada uno
        total_available = sum(o['keywords'] for o in overviews)
        
        if total_available <= target_keywords:
            # Obtener todos
            return domains, 10000
        else:
            # Distribuir proporcionalmente
            keywords_per_domain = target_keywords // len(domains)
            return [o['domain'] for o in overviews], keywords_per_domain


# Alias para mantener compatibilidad con código existente
SemrushService = SemrushServiceOptimized


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar servicio optimizado
    semrush = SemrushServiceOptimized(
        api_key="YOUR_API_KEY",
        enable_cache=True,
        cache_ttl_hours=24,
        max_requests_per_minute=10
    )
    
    # Ejemplo 1: Keywords de un dominio (con caché)
    keywords = semrush.get_organic_keywords(
        domain="ahrefs.com",
        limit=5000
    )
    print(f"Obtenidas {len(keywords)} keywords de ahrefs.com")
    
    # Ejemplo 2: Batch secuencial (compatible)
    domains = ["ahrefs.com", "semrush.com", "moz.com"]
    all_keywords = semrush.batch_get_keywords(
        domains=domains,
        limit=3000
    )
    print(f"Total keywords (secuencial): {len(all_keywords)}")
    
    # Ejemplo 3: Batch paralelo (más rápido)
    all_keywords_parallel = semrush.batch_get_keywords_parallel(
        domains=domains,
        limit=3000,
        max_workers=3
    )
    print(f"Total keywords (paralelo): {len(all_keywords_parallel)}")
    
    # Ejemplo 4: Ver estadísticas
    stats = semrush.get_stats()
    print("\nEstadísticas de uso:")
    print(f"Requests hechos: {stats['requests_made']}")
    print(f"Requests desde caché: {stats['requests_cached']}")
    print(f"Cache hit rate: {stats.get('cache_hit_rate', 'N/A')}")
    print(f"Keywords totales: {stats['total_keywords_fetched']}")
    print(f"Créditos estimados: {stats['credits_used_estimate']}")
