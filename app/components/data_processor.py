import pandas as pd
import numpy as np
from typing import List, Dict, Any
import io
import streamlit as st

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
            'Position': 'position',
            
            # Semrush
            'Keyword ': 'keyword',
            'Search Volume': 'volume',
            'Traffic (%)': 'traffic',
            'Keyword Difficulty': 'difficulty',
            'CPC (USD)': 'cpc',
            
            # Google Search Console
            'query': 'keyword',
            'clicks': 'traffic',
            'impressions': 'volume',
            
            # Otros formatos comunes
            'keyword_text': 'keyword',
            'search_volume': 'volume',
            'monthly_volume': 'volume',
            'kw': 'keyword',
            'term': 'keyword',
            'search_term': 'keyword',
        }
    
    def process_files(self, uploaded_files: List, max_keywords: int = 1000) -> pd.DataFrame:
        """Procesa múltiples archivos cargados y los unifica"""
        
        all_dataframes = []
        errors = []
        
        for file in uploaded_files:
            try:
                st.info(f"📂 Procesando: {file.name}")
                
                # Resetear el puntero del archivo
                file.seek(0)
                
                # Leer archivo según extensión
                if file.name.endswith('.csv'):
                    # Intentar diferentes encodings
                    df = self._read_csv_safe(file)
                elif file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file)
                else:
                    errors.append(f"{file.name}: Formato no soportado")
                    continue
                
                if df is None or df.empty:
                    errors.append(f"{file.name}: Archivo vacío")
                    continue
                
                st.write(f"  ✓ Leído: {len(df)} filas, {len(df.columns)} columnas")
                st.write(f"  📋 Columnas detectadas: {', '.join(df.columns[:5])}...")
                
                # Normalizar columnas
                df = self._normalize_columns(df)
                
                # Validar que tiene las columnas mínimas necesarias
                if 'keyword' not in df.columns:
                    errors.append(f"{file.name}: No se encontró columna de keywords")
                    continue
                
                if 'volume' not in df.columns:
                    st.warning(f"  ⚠️ {file.name}: No tiene columna de volumen, se usará valor 0")
                    df['volume'] = 0
                
                # Validar y limpiar datos
                df = self._clean_data(df)
                
                if df.empty:
                    errors.append(f"{file.name}: No quedaron datos válidos después de limpiar")
                    continue
                
                # Añadir origen del archivo
                df['source'] = file.name.split('.')[0]
                
                # Limitar a max_keywords
                if len(df) > max_keywords:
                    st.warning(f"  ⚠️ Limitando a {max_keywords} keywords (de {len(df)})")
                    df = df.nlargest(max_keywords, 'volume')
                
                all_dataframes.append(df)
                st.success(f"  ✅ {file.name}: {len(df)} keywords procesadas")
                
            except Exception as e:
                error_msg = f"{file.name}: {str(e)}"
                errors.append(error_msg)
                st.error(f"  ❌ Error: {str(e)}")
                continue
        
        # Mostrar resumen de errores si los hay
        if errors:
            with st.expander("⚠️ Ver errores detallados", expanded=False):
                for error in errors:
                    st.write(f"- {error}")
        
        # Verificar que se procesó al menos un archivo
        if not all_dataframes:
            # Mensaje de error más descriptivo
            error_detail = "\n".join(errors) if errors else "Formato de archivo no compatible"
            raise ValueError(
                f"No se pudo procesar ningún archivo.\n\n"
                f"Posibles causas:\n"
                f"1. El archivo no tiene columnas 'keyword' o 'volume'\n"
                f"2. El formato no es CSV o Excel válido\n"
                f"3. El archivo está vacío\n\n"
                f"Detalles:\n{error_detail}\n\n"
                f"💡 Tip: Asegúrate de que tu archivo tiene al menos una columna llamada "
                f"'Keyword' o 'keyword' y opcionalmente 'Volume' o 'volume'"
            )
        
        # Combinar todos los dataframes
        st.info("🔄 Combinando archivos...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Deduplicar keywords
        combined_df = self._deduplicate_keywords(combined_df)
        
        # Calcular métricas adicionales
        combined_df = self._calculate_metrics(combined_df)
        
        st.success(f"✅ Procesamiento completado: {len(combined_df)} keywords únicas")
        
        return combined_df
    
    def _read_csv_safe(self, file) -> pd.DataFrame:
        """Lee CSV intentando diferentes encodings"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=encoding)
                if not df.empty:
                    return df
            except Exception:
                continue
        
        # Si todo falla, intentar con engine python
        try:
            file.seek(0)
            return pd.read_csv(file, engine='python')
        except Exception as e:
            st.error(f"No se pudo leer el CSV: {str(e)}")
            return None
    
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
                normalized = col_clean.lower().replace(' ', '_')
                rename_dict[col] = normalized
        
        df = df.rename(columns=rename_dict)
        
        # Asegurar columnas mínimas necesarias
        required_columns = ['keyword']
        
        for req_col in required_columns:
            if req_col not in df.columns:
                # Intentar inferir
                if req_col == 'keyword':
                    # Buscar la primera columna de texto que no sea URL
                    for col in df.columns:
                        if df[col].dtype == 'object' and not col.startswith('url'):
                            df['keyword'] = df[col]
                            st.info(f"  ℹ️ Usando columna '{col}' como keywords")
                            break
        
        # Añadir columnas opcionales si no existen
        if 'volume' not in df.columns:
            # Buscar columnas numéricas que puedan ser volumen
            for col in df.columns:
                if 'volume' in col.lower() or 'search' in col.lower():
                    df['volume'] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    st.info(f"  ℹ️ Usando columna '{col}' como volumen")
                    break
            
            # Si no se encontró, usar columna numérica más grande
            if 'volume' not in df.columns:
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    df['volume'] = df[numeric_cols[0]]
                    st.info(f"  ℹ️ Usando columna '{numeric_cols[0]}' como volumen")
                else:
                    df['volume'] = 0
        
        if 'traffic' not in df.columns:
            # Estimar tráfico como % del volumen
            df['traffic'] = df['volume'] * 0.3
        
        if 'difficulty' not in df.columns:
            df['difficulty'] = 50
        
        if 'cpc' not in df.columns:
            df['cpc'] = 0
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y valida los datos"""
        
        initial_count = len(df)
        
        # Eliminar filas sin keyword
        df = df.dropna(subset=['keyword'])
        
        # Convertir keyword a string y limpiar
        df['keyword'] = df['keyword'].astype(str).str.strip().str.lower()
        
        # Eliminar keywords vacías o muy cortas
        df = df[df['keyword'].str.len() > 1]
        
        # Convertir volumen a numérico
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
        
        # Convertir tráfico a numérico
        df['traffic'] = pd.to_numeric(df['traffic'], errors='coerce').fillna(0).astype(int)
        
        # Eliminar keywords con volumen negativo
        df = df[df['volume'] >= 0]
        
        # Eliminar duplicados dentro del mismo archivo
        df = df.drop_duplicates(subset=['keyword'], keep='first')
        
        cleaned_count = len(df)
        removed = initial_count - cleaned_count
        
        if removed > 0:
            st.info(f"  ℹ️ Eliminadas {removed} filas inválidas")
        
        return df
    
    def _deduplicate_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """Deduplica keywords manteniendo el mayor volumen"""
        
        initial_count = len(df)
        
        # Agrupar por keyword y mantener el registro con mayor volumen
        df = df.sort_values('volume', ascending=False)
        df = df.drop_duplicates(subset=['keyword'], keep='first')
        
        deduped_count = len(df)
        removed = initial_count - deduped_count
        
        if removed > 0:
            st.info(f"  ℹ️ Eliminados {removed} duplicados")
        
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
