"""
Servicio para analizar URLs y directorios específicos
Soporta múltiples fuentes: Semrush, GSC, scraping directo
"""

import requests
import pandas as pd
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin
import time
from bs4 import BeautifulSoup
import re


class URLAnalyzerService:
    """Servicio para analizar URLs y directorios de un sitio"""
    
    def __init__(self, semrush_api_key: Optional[str] = None):
        self.semrush_api_key = semrush_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def analyze_url_with_semrush(
        self, 
        url: str, 
        database: str = "us"
    ) -> pd.DataFrame:
        """
        Obtiene keywords que rankean para una URL específica usando Semrush
        
        Args:
            url: URL completa a analizar
            database: Base de datos Semrush (us, uk, es, etc)
        
        Returns:
            DataFrame con keywords de la URL
        """
        if not self.semrush_api_key:
            raise ValueError("Se requiere API key de Semrush")
        
        try:
            params = {
                'type': 'url_organic',
                'key': self.semrush_api_key,
                'url': url,
                'database': database,
                'display_limit': 1000,
                'export_columns': 'Ph,Po,Nq,Cp,Co,Tr,Tc,Ur'
            }
            
            response = requests.get(
                "https://api.semrush.com/",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            
            if len(lines) < 2:
                return pd.DataFrame()
            
            header = lines[0].split(';')
            data = [line.split(';') for line in lines[1:]]
            
            df = pd.DataFrame(data, columns=header)
            
            # Normalizar columnas
            column_mapping = {
                'Keyword': 'keyword',
                'Position': 'position',
                'Search Volume': 'volume',
                'CPC': 'cpc',
                'Competition': 'competition',
                'Traffic': 'traffic',
                'Traffic Cost': 'traffic_cost',
                'Url': 'url'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Convertir tipos
            numeric_cols = ['position', 'volume', 'cpc', 'competition', 'traffic', 'traffic_cost']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            df['analyzed_url'] = url
            
            return df
            
        except Exception as e:
            raise Exception(f"Error analizando URL con Semrush: {str(e)}")
    
    def analyze_directory_with_semrush(
        self,
        domain: str,
        directory: str,
        database: str = "us",
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Analiza todas las URLs de un directorio específico
        
        Args:
            domain: Dominio base (ej: "example.com")
            directory: Directorio a analizar (ej: "/blog/")
            database: Base de datos Semrush
            limit: Límite de keywords
        
        Returns:
            DataFrame con keywords del directorio
        """
        if not self.semrush_api_key:
            raise ValueError("Se requiere API key de Semrush")
        
        try:
            # Primero obtener todas las URLs del directorio
            params = {
                'type': 'domain_organic',
                'key': self.semrush_api_key,
                'domain': domain,
                'database': database,
                'display_limit': limit,
                'export_columns': 'Ph,Po,Nq,Cp,Ur,Tr',
                'display_filter': f'+|Ur|Co|{directory}'
            }
            
            response = requests.get(
                "https://api.semrush.com/",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            
            if len(lines) < 2:
                return pd.DataFrame()
            
            header = lines[0].split(';')
            data = [line.split(';') for line in lines[1:]]
            
            df = pd.DataFrame(data, columns=header)
            
            # Normalizar
            column_mapping = {
                'Keyword': 'keyword',
                'Position': 'position',
                'Search Volume': 'volume',
                'CPC': 'cpc',
                'Url': 'url',
                'Traffic': 'traffic'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Convertir tipos
            numeric_cols = ['position', 'volume', 'cpc', 'traffic']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            df['directory'] = directory
            
            return df
            
        except Exception as e:
            raise Exception(f"Error analizando directorio: {str(e)}")
    
    def get_sitemap_urls(self, domain: str) -> List[str]:
        """
        Obtiene URLs desde el sitemap.xml
        
        Args:
            domain: Dominio (ej: "example.com")
        
        Returns:
            Lista de URLs encontradas
        """
        sitemap_urls = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"http://{domain}/sitemap.xml"
        ]
        
        urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'xml')
                
                # Buscar URLs en sitemap
                loc_tags = soup.find_all('loc')
                urls.extend([tag.text for tag in loc_tags])
                
                # Si es un sitemap index, obtener sitemaps individuales
                if soup.find('sitemap'):
                    for sitemap_tag in soup.find_all('sitemap'):
                        loc = sitemap_tag.find('loc')
                        if loc:
                            try:
                                sub_response = self.session.get(loc.text, timeout=10)
                                sub_soup = BeautifulSoup(sub_response.content, 'xml')
                                sub_urls = sub_soup.find_all('loc')
                                urls.extend([tag.text for tag in sub_urls])
                            except:
                                continue
                
                if urls:
                    break
                    
            except Exception as e:
                continue
        
        return list(set(urls))
    
    def filter_urls_by_directory(
        self, 
        urls: List[str], 
        directory: str
    ) -> List[str]:
        """Filtra URLs que pertenecen a un directorio específico"""
        
        filtered = []
        directory = directory.strip('/')
        
        for url in urls:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            if path.startswith(directory):
                filtered.append(url)
        
        return filtered
    
    def scrape_page_content(self, url: str) -> Dict:
        """
        Extrae contenido de una página para análisis
        
        Returns:
            Dict con title, h1, meta description, content, word_count
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer elementos clave
            title = soup.find('title')
            title_text = title.text.strip() if title else ""
            
            h1 = soup.find('h1')
            h1_text = h1.text.strip() if h1 else ""
            
            meta_desc = soup.find('meta', {'name': 'description'})
            meta_desc_text = meta_desc.get('content', '') if meta_desc else ""
            
            # Extraer contenido del body (sin scripts/styles)
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            words = text.split()
            word_count = len(words)
            
            return {
                'url': url,
                'title': title_text,
                'h1': h1_text,
                'meta_description': meta_desc_text,
                'word_count': word_count,
                'content_preview': text[:500]
            }
            
        except Exception as e:
            return {
                'url': url,
                'title': '',
                'h1': '',
                'meta_description': '',
                'word_count': 0,
                'content_preview': '',
                'error': str(e)
            }
    
    def analyze_multiple_urls(
        self,
        urls: List[str],
        use_semrush: bool = True,
        scrape_content: bool = True
    ) -> pd.DataFrame:
        """
        Analiza múltiples URLs
        
        Args:
            urls: Lista de URLs a analizar
            use_semrush: Si usar Semrush para obtener keywords
            scrape_content: Si extraer contenido de las páginas
        
        Returns:
            DataFrame con análisis completo
        """
        results = []
        
        for i, url in enumerate(urls):
            print(f"Analizando {i+1}/{len(urls)}: {url}")
            
            result = {'url': url}
            
            # Obtener keywords con Semrush
            if use_semrush and self.semrush_api_key:
                try:
                    keywords_df = self.analyze_url_with_semrush(url)
                    
                    result['total_keywords'] = len(keywords_df)
                    result['total_volume'] = keywords_df['volume'].sum()
                    result['total_traffic'] = keywords_df['traffic'].sum()
                    result['avg_position'] = keywords_df['position'].mean()
                    result['top_keywords'] = ', '.join(keywords_df.nlargest(5, 'volume')['keyword'].tolist())
                    
                except Exception as e:
                    result['total_keywords'] = 0
                    result['error_semrush'] = str(e)
            
            # Scrape contenido
            if scrape_content:
                try:
                    content = self.scrape_page_content(url)
                    result.update(content)
                except Exception as e:
                    result['error_scrape'] = str(e)
            
            results.append(result)
            
            # Rate limiting
            time.sleep(1)
        
        return pd.DataFrame(results)
    
    def detect_cannibalization(
        self,
        domain: str,
        min_common_keywords: int = 5
    ) -> pd.DataFrame:
        """
        Detecta canibalización de keywords entre URLs
        
        Args:
            domain: Dominio a analizar
            min_common_keywords: Mínimo de keywords en común para considerar canibalización
        
        Returns:
            DataFrame con pares de URLs que canibalizan
        """
        if not self.semrush_api_key:
            raise ValueError("Se requiere API key de Semrush")
        
        # Obtener todas las URLs con keywords
        params = {
            'type': 'domain_organic',
            'key': self.semrush_api_key,
            'domain': domain,
            'database': 'us',
            'display_limit': 5000,
            'export_columns': 'Ph,Ur'
        }
        
        response = requests.get("https://api.semrush.com/", params=params)
        lines = response.text.strip().split('\n')
        
        if len(lines) < 2:
            return pd.DataFrame()
        
        header = lines[0].split(';')
        data = [line.split(';') for line in lines[1:]]
        
        df = pd.DataFrame(data, columns=header)
        df.columns = ['keyword', 'url']
        
        # Agrupar por URL
        url_keywords = df.groupby('url')['keyword'].apply(list).to_dict()
        
        # Detectar canibalización
        cannibalization = []
        
        urls = list(url_keywords.keys())
        for i in range(len(urls)):
            for j in range(i + 1, len(urls)):
                url1 = urls[i]
                url2 = urls[j]
                
                keywords1 = set(url_keywords[url1])
                keywords2 = set(url_keywords[url2])
                
                common = keywords1.intersection(keywords2)
                
                if len(common) >= min_common_keywords:
                    cannibalization.append({
                        'url_1': url1,
                        'url_2': url2,
                        'common_keywords_count': len(common),
                        'common_keywords': ', '.join(list(common)[:10])
                    })
        
        return pd.DataFrame(cannibalization).sort_values(
            'common_keywords_count', 
            ascending=False
        )
    
    def compare_directories(
        self,
        domain: str,
        directories: List[str]
    ) -> pd.DataFrame:
        """
        Compara el rendimiento de diferentes directorios
        
        Args:
            domain: Dominio base
            directories: Lista de directorios (ej: ['/blog/', '/productos/'])
        
        Returns:
            DataFrame comparativo
        """
        results = []
        
        for directory in directories:
            print(f"Analizando directorio: {directory}")
            
            try:
                df = self.analyze_directory_with_semrush(domain, directory)
                
                if not df.empty:
                    result = {
                        'directory': directory,
                        'total_keywords': len(df),
                        'total_volume': df['volume'].sum(),
                        'total_traffic': df['traffic'].sum(),
                        'avg_position': df['position'].mean(),
                        'unique_urls': df['url'].nunique()
                    }
                    results.append(result)
                    
            except Exception as e:
                print(f"Error con {directory}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
