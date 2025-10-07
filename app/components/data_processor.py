import pandas as pd
import numpy as np
from typing import List, Dict, Any
import io

class DataProcessor:
    """Procesador de datos de keywords desde múltiples fuentes"""
    
    def __init__(self):
        # Mapeo de columnas comunes de diferentes fuentes
        self.column_mapping = {
            # Ahrefs
            'Keyword': 'keyword',
            'Volume': 'volume',
            'Traffic': 'traffic',
            'KD': 'difficulty',
            'CPC': 'cpc',
            
            # Semrush
            'Keyword ': 'keyword',
            'Search Volume': 'volume',
            'Traffic (%)': 'traffic',
            'Keyword Difficulty': 'difficulty',
            'CPC (USD)': 'cpc',
            
            # Google Search Console (posible)
            'query': 'keyword',
            'clicks': 'traffic',
            'impressions': 'volume',
            
            # Otros formatos comunes
            'keyword_text': 'keyword',
            'search_volume': 'volume',
            'monthly_volume': 'volume'
        }
    
    def process_files(self, uploaded_files: List, max_keywords: int = 1000) -> pd.DataFrame:
        """Procesa múltiples archivos cargados y los unifica"""
        
        all_dataframes = []
        
        for file in uploaded_files:
            try:
                # Leer archivo
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Normalizar columnas
                df = self._normalize_columns(df)
                
                # Validar y limpiar datos
                df = self._clean_data(df)
                
                # Añadir origen del archivo
                df['source'] = file.name.split('.')[0]
                
                # Limitar a max_keywords
                if len(df) > max_keywords:
                    df = df.nlargest(max_keywords, 'volume')
                
                all_dataframes.append(df)
                
            except Exception as e:
                print(f"Error procesando {file.name}: {str(e)}")
                continue
        
        if not all_dataframes:
            raise ValueError("No se pudo procesar ningún archivo")
        
        # Combinar todos los dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Deduplicar keywords
        combined_df = self._deduplicate_keywords(combined_df)
        
        # Calcular métricas adicionales
        combined_df = self._calculate_metrics(combined_df)
    
    if 'traffic' not in combined_df.columns:
        # Estimar tráfico como ~30% del volumen (CTR promedio estimado)
        combined_df['traffic'] = (combined_df['volume'] * 0.3).astype(int)
        print("⚠️ Columna 'traffic' no encontrada. Estimada basada en volumen.")
    
    # Validar que traffic no tenga valores nulos
    if combined_df['traffic'].isnull().any():
        combined_df['traffic'] = combined_df['traffic'].fillna(
            (combined_df['volume'] * 0.3).astype(int)
        )
        
        return combined_df
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los nombres de las columnas"""
        
        # Crear un mapeo de columnas actuales a estándar
        rename_dict = {}
        
        for col in df.columns:
            # Limpiar espacios
            col_clean = col.strip()
            
            # Buscar en el mapping
            if col_clean in self.column_mapping:
                rename_dict[col] = self.column_mapping[col_clean]
            else:
                # Normalizar a minúsculas y espacios a guiones bajos
                rename_dict[col] = col_clean.lower().replace(' ', '_')
        
        df = df.rename(columns=rename_dict)
        
        # Asegurar columnas mínimas necesarias
        required_columns = ['keyword', 'volume']
        
        for req_col in required_columns:
            if req_col not in df.columns:
                # Intentar inferir
                if req_col == 'keyword':
                    # Buscar la primera columna de texto
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            df['keyword'] = df[col]
                            break
                elif req_col == 'volume':
                    # Buscar columnas numéricas
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        df['volume'] = df[numeric_cols[0]]
        
        # Añadir columnas opcionales si no existen
        if 'traffic' not in df.columns:
            # Estimar tráfico como % del volumen
            df['traffic'] = df['volume'] * 0.3  # ~30% CTR promedio
        
        if 'difficulty' not in df.columns:
            df['difficulty'] = 50  # Valor medio por defecto
        
        if 'cpc' not in df.columns:
            df['cpc'] = 0
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y valida los datos"""
        
        # Eliminar filas sin keyword
        df = df.dropna(subset=['keyword'])
        
        # Convertir keyword a string y limpiar
        df['keyword'] = df['keyword'].astype(str).str.strip().str.lower()
        
        # Eliminar keywords vacías
        df = df[df['keyword'] != '']
        
        # Convertir volumen a numérico
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
        
        # Convertir tráfico a numérico
        df['traffic'] = pd.to_numeric(df['traffic'], errors='coerce').fillna(0).astype(int)
        
        # Eliminar keywords con volumen 0
        df = df[df['volume'] > 0]
        
        # Eliminar duplicados dentro del mismo archivo
        df = df.drop_duplicates(subset=['keyword'], keep='first')
        
        return df
    
    def _deduplicate_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """Deduplica keywords manteniendo el mayor volumen"""
        
        # Agrupar por keyword y mantener el registro con mayor volumen
        df = df.sort_values('volume', ascending=False)
        df = df.drop_duplicates(subset=['keyword'], keep='first')
        
        return df
    
    def _calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula métricas adicionales"""
        
        # CTR estimado
        df['ctr_estimate'] = (df['traffic'] / df['volume'] * 100).clip(0, 100)
        
        # Longitud de keyword
        df['keyword_length'] = df['keyword'].str.split().str.len()
        
        # Clasificación por longitud
        df['keyword_type'] = df['keyword_length'].apply(
            lambda x: 'short-tail' if x <= 2 else 'mid-tail' if x <= 4 else 'long-tail'
        )
        
        # Score de oportunidad (volumen / dificultad)
        if 'difficulty' in df.columns:
            df['opportunity_score'] = df['volume'] / (df['difficulty'] + 1)
        else:
            df['opportunity_score'] = df['volume']
        
        return df
    
    def filter_branded_keywords(self, df: pd.DataFrame, brand_terms: List[str]) -> pd.DataFrame:
        """Filtra keywords branded"""
        
        if not brand_terms:
            return df
        
        # Convertir brand_terms a minúsculas
        brand_terms_lower = [term.lower() for term in brand_terms]
        
        # Filtrar keywords que contienen términos de marca
        mask = ~df['keyword'].apply(
            lambda x: any(brand in x for brand in brand_terms_lower)
        )
        
        return df[mask]
    
    def get_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Obtiene estadísticas del dataset"""
        
        stats = {
            'total_keywords': len(df),
            'unique_keywords': df['keyword'].nunique(),
            'total_volume': int(df['volume'].sum()),
            'avg_volume': int(df['volume'].mean()),
            'median_volume': int(df['volume'].median()),
            'total_traffic': int(df['traffic'].sum()),
            'avg_traffic': int(df['traffic'].mean()),
            'keyword_types': df['keyword_type'].value_counts().to_dict() if 'keyword_type' in df.columns else {},
            'sources': df['source'].value_counts().to_dict() if 'source' in df.columns else {}
        }
        
        return stats
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = 'keywords_processed.csv') -> str:
        """Exporta el dataframe a CSV"""
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
    
    def sample_keywords(self, df: pd.DataFrame, n: int = 100, method: str = 'top') -> pd.DataFrame:
        """Obtiene una muestra de keywords"""
        
        if method == 'top':
            return df.nlargest(n, 'volume')
        elif method == 'random':
            return df.sample(min(n, len(df)))
        elif method == 'stratified':
            # Muestra estratificada por keyword_type
            if 'keyword_type' in df.columns:
                return df.groupby('keyword_type', group_keys=False).apply(
                    lambda x: x.sample(min(len(x), n // 3))
                )
            else:
                return df.sample(min(n, len(df)))
        else:
            return df.head(n)
