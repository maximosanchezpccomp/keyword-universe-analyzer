"""
Servicio para interactuar con la API de Semrush
"""
import pandas as pd
from typing import List, Dict, Optional
import time

try:
    import requests
except ImportError:
    requests = None


class SemrushService:
    """Servicio para interactuar con la API de Semrush"""
    
    BASE_URL = "https://api.semrush.com/"
    
    def __init__(self, api_key: str):
        if requests is None:
            raise ImportError("La librería 'requests' es requerida para usar SemrushService")
        
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
        
        Returns:
            DataFrame con las keywords
        """
        
        try:
            # Construir parámetros
            params = {
                'type': 'domain_organic',
                'domain': domain,
                'database': database,
                'display_limit': limit,
                'export_columns': 'Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td',
                'display_sort': 'tr_desc'
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
                'Search Volume': 'volume',
                'CPC': 'cpc',
                'URL': 'url',
                'Traffic': 'traffic',
                'Traffic (%)': 'traffic_pct'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Convertir tipos de datos
            numeric_columns = ['position', 'volume', 'cpc', 'traffic', 'traffic_pct']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Filtrar keywords branded si se solicita
            if filter_branded and 'keyword' in df.columns:
                domain_name = domain.split('.')[0].lower()
                df = df[~df['keyword'].str.lower().str.contains(domain_name)]
            
            # Añadir metadata
            df['source'] = domain
            df['database'] = database
            
            return df
            
        except Exception as e:
            raise Exception(f"Error al consultar Semrush API: {str(e)}")
    
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
        
        Returns:
            DataFrame combinado con todas las keywords
        """
        
        all_keywords = []
        
        for domain in domains:
            try:
                keywords = self.get_organic_keywords(domain, limit=limit)
                all_keywords.append(keywords)
                time.sleep(delay)
            except Exception as e:
                print(f"Error con {domain}: {str(e)}")
                continue
        
        if not all_keywords:
            return pd.DataFrame()
        
        return pd.concat(all_keywords, ignore_index=True)
