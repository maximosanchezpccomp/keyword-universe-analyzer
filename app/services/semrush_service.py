import requests
import pandas as pd
from typing import List, Dict, Optional, Literal
import time
from urllib.parse import urlparse

class SemrushService:
    """Servicio para interactuar con la API de Semrush"""
    
    BASE_URL = "https://api.semrush.com/"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.params = {'key': self.api_key}
    
    def get_organic_keywords(
        self, 
        target: str,
        target_type: Literal['domain', 'url', 'directory'] = 'domain',
        limit: int = 1000,
        database: str = "us",
        filter_branded: bool = True
    ) -> pd.DataFrame:
        """
        Obtiene keywords orgánicas desde Semrush
        
        Args:
            target: Dominio, URL o directorio a analizar
            target_type: Tipo de análisis ('domain', 'url', 'directory')
            limit: Número máximo de keywords a obtener
            database: Base de datos de Semrush (us, uk, es, etc)
            filter_branded: Filtrar keywords con el nombre del dominio
        
        Returns:
            DataFrame con las keywords
        """
        
        try:
            # Normalizar el target según el tipo
            normalized_target = self._normalize_target(target, target_type)
            
            # Seleccionar endpoint según tipo
            if target_type == 'domain':
                return self._get_domain_keywords(normalized_target, limit, database, filter_branded)
            elif target_type == 'url':
                return self._get_url_keywords(normalized_target, limit, database, filter_branded)
            elif target_type == 'directory':
                return self._get_directory_keywords(normalized_target, limit, database, filter_branded)
            else:
                raise ValueError(f"Tipo no soportado: {target_type}")
                
        except Exception as e:
            raise Exception(f"Error al obtener keywords de {target}: {str(e)}")
    
    def _normalize_target(self, target: str, target_type: str) -> str:
        """Normaliza el formato del target según el tipo"""
        
        target = target.strip()
        
        if target_type == 'domain':
            # Eliminar protocolo y paths
            parsed = urlparse(target if '://' in target else f'http://{target}')
            return parsed.netloc or parsed.path.split('/')[0]
        
        elif target_type == 'url':
            # Asegurar que tiene protocolo
            if not target.startswith(('http://', 'https://')):
                target = f'https://{target}'
            return target
        
        elif target_type == 'directory':
            # Formato: domain.com/directory/
            if target.startswith(('http://', 'https://')):
                parsed = urlparse(target)
                domain = parsed.netloc
                path = parsed.path.rstrip('/')
                return f"{domain}{path}" if path else domain
            return target
        
        return target
    
    def _get_domain_keywords(
        self, 
        domain: str, 
        limit: int, 
        database: str,
        filter_branded: bool
    ) -> pd.DataFrame:
        """Obtiene keywords de un dominio completo"""
        
        params = {
            'type': 'domain_organic',
            'domain': domain,
            'database': database,
            'display_limit': limit,
            'export_columns': 'Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td',
            'display_sort': 'tr_desc'
        }
        
        df = self._make_request_and_parse(params)
        df['source_type'] = 'domain'
        df['source'] = domain
        
        if filter_branded:
            domain_name = domain.split('.')[0].lower()
            df = df[~df['keyword'].str.lower().str.contains(domain_name, na=False)]
        
        return df
    
    def _get_url_keywords(
        self, 
        url: str, 
        limit: int, 
        database: str,
        filter_branded: bool
    ) -> pd.DataFrame:
        """Obtiene keywords de una URL específica"""
        
        params = {
            'type': 'url_organic',
            'url': url,
            'database': database,
            'display_limit': limit,
            'export_columns': 'Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td',
            'display_sort': 'tr_desc'
        }
        
        df = self._make_request_and_parse(params)
        df['source_type'] = 'url'
        df['source'] = url
        
        if filter_branded:
            domain = urlparse(url).netloc.split('.')[0].lower()
            df = df[~df['keyword'].str.lower().str.contains(domain, na=False)]
        
        return df
    
    def _get_directory_keywords(
        self, 
        directory: str, 
        limit: int, 
        database: str,
        filter_branded: bool
    ) -> pd.DataFrame:
        """
        Obtiene keywords de un directorio específico
        
        Nota: Semrush no tiene un endpoint directo para directorios,
        así que obtenemos keywords del dominio y filtramos por URL
        """
        
        # Separar dominio y path
        if '/' in directory:
            parts = directory.split('/', 1)
            domain = parts[0]
            path_filter = f"/{parts[1]}"
        else:
            domain = directory
            path_filter = ""
        
        # Obtener keywords del dominio
        params = {
            'type': 'domain_organic',
            'domain': domain,
            'database': database,
            'display_limit': limit * 3,  # Obtener más para filtrar después
            'export_columns': 'Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td',
            'display_sort': 'tr_desc'
        }
        
        df = self._make_request_and_parse(params)
        
        # Filtrar por directorio si hay path
        if path_filter:
            df = df[df['url'].str.contains(path_filter, na=False, regex=False)]
        
        # Limitar al número solicitado
        df = df.head(limit)
        
        df['source_type'] = 'directory'
        df['source'] = directory
        
        if filter_branded:
            domain_name = domain.split('.')[0].lower()
            df = df[~df['keyword'].str.lower().str.contains(domain_name, na=False)]
        
        return df
    
    def _make_request_and_parse(self, params: Dict) -> pd.DataFrame:
        """Hace el request a Semrush y parsea la respuesta"""
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        
        if len(lines) < 2:
            return pd.DataFrame()
        
        # Parsear CSV
        header = lines[0].split(';')
        data = [line.split(';') for line in lines[1:]]
        
        df = pd.DataFrame(data, columns=header)
        
        # Renombrar columnas
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
        numeric_columns = ['position', 'prev_position', 'position_diff', 
                         'volume', 'cpc', 'traffic', 'traffic_pct', 
                         'traffic_cost', 'serp_results']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Asegurar columnas básicas existen
        if 'traffic' not in df.columns:
            # Estimar traffic como 30% del volumen si no existe
            df['traffic'] = (df['volume'] * 0.3).astype(int) if 'volume' in df.columns else 0
        
        if 'cpc' not in df.columns:
            df['cpc'] = 0
        
        if 'difficulty' not in df.columns:
            df['difficulty'] = 50
        
        return df
    
    def batch_get_keywords(
        self, 
        targets: List[Dict[str, str]], 
        limit: int = 1000,
        delay: float = 1.0,
        database: str = "us"
    ) -> pd.DataFrame:
        """
        Obtiene keywords de múltiples targets con rate limiting
        
        Args:
            targets: Lista de dicts con 'target' y 'type'
                    Ej: [{'target': 'example.com', 'type': 'domain'}]
            limit: Keywords por target
            delay: Delay entre requests en segundos
            database: Base de datos de Semrush
        
        Returns:
            DataFrame combinado con todas las keywords
        """
        
        all_keywords = []
        
        for item in targets:
            try:
                target = item['target']
                target_type = item.get('type', 'domain')
                
                print(f"📥 Obteniendo keywords de {target} ({target_type})...")
                
                keywords = self.get_organic_keywords(
                    target=target,
                    target_type=target_type,
                    limit=limit,
                    database=database
                )
                
                all_keywords.append(keywords)
                print(f"✓ {target}: {len(keywords)} keywords")
                
                # Rate limiting
                time.sleep(delay)
                
            except Exception as e:
                print(f"✗ Error con {target}: {str(e)}")
                continue
        
        if not all_keywords:
            return pd.DataFrame()
        
        return pd.concat(all_keywords, ignore_index=True)
    
    def get_url_rank(self, url: str, database: str = "us") -> Dict:
        """Obtiene el ranking de una URL específica"""
        
        try:
            params = {
                'type': 'url_organic',
                'url': url,
                'database': database,
                'display_limit': 1,
                'export_columns': 'Ph,Po,Nq,Tr'
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
                'url': url,
                'top_keyword': info.get('Keyword', ''),
                'position': int(info.get('Position', 0)),
                'volume': int(info.get('Search Volume', 0)),
                'traffic': int(info.get('Traffic', 0))
            }
            
        except Exception as e:
            print(f"Error obteniendo rank de URL: {str(e)}")
            return {}
    
    # Métodos existentes que se mantienen igual
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
            
            numeric_cols = ['relevance', 'common_keywords', 'organic_keywords', 
                          'organic_traffic', 'organic_cost', 'adwords_keywords']
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            return df
            
        except Exception as e:
            print(f"Error obteniendo competidores de {domain}: {str(e)}")
            return pd.DataFrame()
