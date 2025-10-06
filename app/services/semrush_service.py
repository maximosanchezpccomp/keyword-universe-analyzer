import requests
import pandas as pd
from typing import List, Dict, Optional
import time

class SemrushService:
    """Servicio para interactuar con la API de Semrush"""
    
    BASE_URL = "https://api.semrush.com/"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.params = {'key': self.api_key}
    
    def get_organic_keywords(
        self, 
        domain: str, 
        limit: int = 1000,
        database: str = "us",
        filter_branded: bool = True
    ) -> pd.DataFrame:
        """
        Obtiene keywords orgánicas de un dominio desde Semrush
        
        Args:
            domain: Dominio a analizar (ej: "example.com")
            limit: Número máximo de keywords a obtener
            database: Base de datos de Semrush (us, uk, es, etc)
            filter_branded: Filtrar keywords con el nombre del dominio
        """
        
        try:
            # Construir parámetros
            params = {
                'type': 'domain_organic',
                'domain': domain,
                'database': database,
                'display_limit': limit,
                'export_columns': 'Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td',
                'display_sort': 'tr_desc'  # Ordenar por tráfico descendente
            }
            
            # Hacer request
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            # Parsear respuesta
            lines = response.text.strip().split('\n')
            
            if len(lines) < 2:
                raise ValueError(f"No se encontraron datos para {domain}")
            
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
                domain_name = domain.split('.')[0].lower()
                df = df[~df['keyword'].str.lower().str.contains(domain_name)]
            
            # Añadir metadata
            df['source'] = domain
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
        domains: List[str], 
        limit: int = 1000,
        delay: float = 1.0
    ) -> pd.DataFrame:
        """
        Obtiene keywords de múltiples dominios con rate limiting
        
        Args:
            domains: Lista de dominios
            limit: Keywords por dominio
            delay: Delay entre requests en segundos
        """
        
        all_keywords = []
        
        for domain in domains:
            try:
                print(f"Obteniendo keywords de {domain}...")
                keywords = self.get_organic_keywords(domain, limit=limit)
                all_keywords.append(keywords)
                print(f"✓ {domain}: {len(keywords)} keywords")
                
                # Rate limiting
                time.sleep(delay)
                
            except Exception as e:
                print(f"✗ Error con {domain}: {str(e)}")
                continue
        
        if not all_keywords:
            return pd.DataFrame()
        
        return pd.concat(all_keywords, ignore_index=True)
