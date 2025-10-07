import requests
import pandas as pd
from typing import List, Dict, Optional
import time
from urllib.parse import urlparse

class SemrushService:
    """Servicio para interactuar con la API de Semrush"""
    
    BASE_URL = "https://api.semrush.com/"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.params = {'key': self.api_key}
    
    def _detect_target_type(self, target: str) -> tuple:
        """
        Detecta si el target es un dominio, directorio o URL específica
        
        Returns:
            tuple: (tipo, target_limpio)
            - tipo: 'domain', 'directory', 'url'
            - target_limpio: URL normalizada
        """
        # Limpiar el target
        target = target.strip()
        
        # Añadir https:// si no tiene protocolo
        if not target.startswith(('http://', 'https://')):
            target = f'https://{target}'
        
        parsed = urlparse(target)
        domain = parsed.netloc or parsed.path.split('/')[0]
        path = parsed.path
        
        # Determinar tipo
        if not path or path == '/':
            # Dominio raíz: example.com o example.com/
            return 'domain', domain
        elif path.endswith('/'):
            # Directorio: example.com/blog/ o example.com/products/shoes/
            return 'directory', f'{domain}{path}'
        else:
            # URL específica: example.com/blog/post-title
            return 'url', f'{domain}{path}'
    
    def get_organic_keywords(
        self, 
        target: str, 
        limit: int = 1000,
        database: str = "us",
        filter_branded: bool = True
    ) -> pd.DataFrame:
        """
        Obtiene keywords orgánicas de un dominio, directorio o URL desde Semrush
        
        Args:
            target: Puede ser:
                - Dominio: "example.com"
                - Directorio: "example.com/blog/" o "https://example.com/products/"
                - URL: "example.com/blog/post-title" o "https://example.com/page.html"
            limit: Número máximo de keywords a obtener
            database: Base de datos de Semrush (us, uk, es, etc)
            filter_branded: Filtrar keywords con el nombre del dominio
        
        Returns:
            DataFrame con las keywords encontradas
        """
        
        try:
            # Detectar tipo de target
            target_type, normalized_target = self._detect_target_type(target)
            
            # Seleccionar tipo de reporte según el target
            if target_type == 'domain':
                report_type = 'domain_organic'
                target_param = normalized_target
            else:
                # Para URLs y directorios usa url_organic
                report_type = 'url_organic'
                target_param = normalized_target
            
            # Log del análisis
            print(f"📊 Analizando {target_type}: {normalized_target}")
            
            # Construir parámetros
            params = {
                'type': report_type,
                'display_limit': limit,
                'export_columns': 'Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td',
                'display_sort': 'tr_desc',  # Ordenar por tráfico descendente
                'database': database
            }
            
            # Añadir el target según el tipo
            if target_type == 'domain':
                params['domain'] = target_param
            else:
                params['url'] = target_param
            
            # Hacer request
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            # Parsear respuesta
            lines = response.text.strip().split('\n')
            
            if len(lines) < 2:
                raise ValueError(f"No se encontraron datos para {target}")
            
            # Separar header y datos
            header = lines[0].split(';')
            data = [line.split(';') for line in lines[1:]]
            
            # Crear DataFrame
            df = pd.DataFrame(data, columns=header)
            
            # Renombrar columnas a formato estándar
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
            
            # Convertir tipos de datos
            numeric_columns = ['position', 'prev_position', 'position_diff', 
                             'volume', 'cpc', 'traffic', 'traffic_pct', 
                             'traffic_cost', 'serp_results']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Filtrar keywords branded si se solicita
            if filter_branded:
                # Extraer el dominio base para filtrar
                domain_base = normalized_target.split('/')[0].split('.')[0].lower()
                df = df[~df['keyword'].str.lower().str.contains(domain_base)]
            
            # Añadir metadata
            df['source'] = target
            df['source_type'] = target_type
            df['database'] = database
            
            return df
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al consultar Semrush API: {str(e)}")
        except Exception as e:
            raise Exception(f"Error procesando datos de Semrush: {str(e)}")
    
    def get_domain_overview(self, domain: str, database: str = "us") -> Dict:
        """Obtiene overview del dominio"""
        
        try:
            params = {
                'type': 'domain_ranks',
                'domain': domain,
                'database': database,
                'export_columns': 'Dn,Rk,Or,Ot,Oc,Ad,At,Ac'
            }
            
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return {}
            
            header = lines[0].split(';')
            data = lines[1].split(';')
            
            overview = dict(zip(header, data))
            
            # Convertir a formato legible
            return {
                'domain': overview.get('Domain', domain),
                'rank': int(overview.get('Rank', 0)),
                'organic_keywords': int(overview.get('Organic Keywords', 0)),
                'organic_traffic': int(overview.get('Organic Traffic', 0)),
                'organic_cost': float(overview.get('Organic Cost', 0)),
                'adwords_keywords': int(overview.get('Adwords Keywords', 0)),
                'adwords_traffic': int(overview.get('Adwords Traffic', 0)),
                'adwords_cost': float(overview.get('Adwords Cost', 0))
            }
            
        except Exception as e:
            print(f"Error obteniendo overview de {domain}: {str(e)}")
            return {}
    
    def get_keyword_overview(self, keyword: str, database: str = "us") -> Dict:
        """Obtiene información detallada de una keyword"""
        
        try:
            params = {
                'type': 'phrase_this',
                'phrase': keyword,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co,Nr,Td'
            }
            
            response = self.session.get(self.BASE_URL, params=params)
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
            print(f"Error obteniendo info de keyword '{keyword}': {str(e)}")
            return {}
    
    def get_competitors(
        self, 
        domain: str, 
        database: str = "us",
        limit: int = 10
    ) -> pd.DataFrame:
        """Obtiene competidores orgánicos del dominio"""
        
        try:
            params = {
                'type': 'domain_organic_organic',
                'domain': domain,
                'database': database,
                'display_limit': limit,
                'export_columns': 'Dn,Cr,Np,Or,Ot,Oc,Ad'
            }
            
            response = self.session.get(self.BASE_URL, params=params)
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
            
            return df
            
        except Exception as e:
            print(f"Error obteniendo competidores de {domain}: {str(e)}")
            return pd.DataFrame()
    
    def batch_get_keywords(
        self, 
        targets: List[str], 
        limit: int = 1000,
        delay: float = 1.0
    ) -> pd.DataFrame:
        """
        Obtiene keywords de múltiples targets (dominios, directorios o URLs) con rate limiting
        
        Args:
            targets: Lista de targets (pueden ser dominios, directorios o URLs mezclados)
            limit: Keywords por target
            delay: Delay entre requests en segundos
        """
        
        all_keywords = []
        
        for target in targets:
            try:
                # Detectar tipo para mejor logging
                target_type, normalized = self._detect_target_type(target)
                
                print(f"🔍 Obteniendo keywords de {target_type}: {target}...")
                keywords = self.get_organic_keywords(target, limit=limit)
                
                if not keywords.empty:
                    all_keywords.append(keywords)
                    print(f"✓ {target}: {len(keywords)} keywords obtenidas")
                else:
                    print(f"⚠️  {target}: No se encontraron keywords")
                
                # Rate limiting
                time.sleep(delay)
                
            except Exception as e:
                print(f"✗ Error con {target}: {str(e)}")
                continue
        
        if not all_keywords:
            return pd.DataFrame()
        
        return pd.concat(all_keywords, ignore_index=True)
    
    def compare_urls(
        self,
        url1: str,
        url2: str,
        database: str = "us"
    ) -> Dict:
        """
        Compara dos URLs para ver keywords comunes y únicas
        
        Args:
            url1: Primera URL
            url2: Segunda URL
            database: Base de datos de Semrush
        
        Returns:
            Diccionario con análisis comparativo
        """
        
        try:
            print(f"📊 Comparando URLs...")
            
            # Obtener keywords de ambas URLs
            kw1 = self.get_organic_keywords(url1, limit=10000, database=database)
            kw2 = self.get_organic_keywords(url2, limit=10000, database=database)
            
            # Keywords únicas y comunes
            keywords1 = set(kw1['keyword'].tolist())
            keywords2 = set(kw2['keyword'].tolist())
            
            common = keywords1.intersection(keywords2)
            unique1 = keywords1 - keywords2
            unique2 = keywords2 - keywords1
            
            return {
                'url1': url1,
                'url2': url2,
                'url1_keywords': len(keywords1),
                'url2_keywords': len(keywords2),
                'common_keywords': len(common),
                'unique_to_url1': len(unique1),
                'unique_to_url2': len(unique2),
                'overlap_percentage': (len(common) / len(keywords1) * 100) if keywords1 else 0,
                'common_keywords_list': list(common)[:50],  # Top 50
                'unique_to_url1_list': list(unique1)[:50],
                'unique_to_url2_list': list(unique2)[:50]
            }
            
        except Exception as e:
            print(f"Error comparando URLs: {str(e)}")
            return {}
