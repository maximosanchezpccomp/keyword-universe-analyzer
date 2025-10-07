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
                
                # Validar que tiene las columnas REQUERIDAS
                required = ['keyword', 'volume', 'difficulty', 'cpc']
                missing = [col for col in required if col not in df.columns or df[col].isnull().all()]
                
                if missing:
                    errors.append(f"{file.name}: Faltan columnas requeridas: {', '.join(missing)}")
                    st.error(f"  ❌ Faltan columnas requeridas: {', '.join(missing)}")
                    continue
                
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
            error_detail = "\n".join(errors) if errors else "Formato de archivo no compatible"
            raise ValueError(
                f"❌ No se pudo procesar ningún archivo.\n\n"
                f"📋 **Columnas REQUERIDAS:**\n"
                f"  • keyword (o 'Keyword', 'query', 'term')\n"
                f"  • volume (o 'Volume', 'Search Volume', 'searches')\n"
                f"  • difficulty (o 'Difficulty', 'KD', '0-100')\n"
                f"  • cpc (o 'CPC', 'Cost Per Click')\n\n"
                f"📝 **Formato mínimo esperado:**\n"
                f"  keyword,volume,difficulty,cpc\n"
                f"  seo tools,10000,67,2.45\n"
                f"  keyword research,8000,63,1.85\n\n"
                f"🔍 **Errores detectados:**\n{error_detail}\n\n"
                f"💡 **Solución:**\n"
                f"  1. Verifica que tu archivo tiene estas 4 columnas\n"
                f"  2. Usa el script de diagnóstico: python test_file_format.py tu_archivo.csv\n"
                f"  3. Prueba con el archivo de ejemplo: data/examples/keywords_example.csv"
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
        
        # Asegurar columnas REQUERIDAS
        required_columns = {
            'keyword': ['keyword', 'query', 'kw', 'term', 'search_term'],
            'volume': ['volume', 'search_volume', 'monthly_volume', 'searches'],
            'difficulty': ['difficulty', 'kd', 'keyword_difficulty', 'competition'],
            'cpc': ['cpc', 'cost_per_click', 'avg_cpc']
        }
        
        for req_col, possible_names in required_columns.items():
            if req_col not in df.columns:
                # Intentar encontrar columna equivalente
                found = False
                for possible_name in possible_names:
                    for col in df.columns:
                        if col.lower() == possible_name.lower():
                            df[req_col] = df[col]
                            st.info(f"  ℹ️ Usando columna '{col}' como '{req_col}'")
                            found = True
                            break
                    if found:
                        break
                
                # Si no se encontró, buscar por contenido parcial
                if not found:
                    for possible_name in possible_names:
                        for col in df.columns:
                            if possible_name.lower() in col.lower():
                                df[req_col] = df[col]
                                st.info(f"  ℹ️ Usando columna '{col}' como '{req_col}'")
                                found = True
                                break
                        if found:
                            break
                
                # Si aún no se encontró, valores por defecto según el tipo
                if not found:
                    if req_col == 'keyword':
                        # Buscar la primera columna de texto
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                df['keyword'] = df[col]
                                st.warning(f"  ⚠️ Usando columna '{col}' como keywords")
                                found = True
                                break
                    elif req_col == 'volume':
                        # Buscar columna numérica más grande
                        numeric_cols = df.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            df['volume'] = df[numeric_cols[0]]
                            st.warning(f"  ⚠️ Usando columna '{numeric_cols[0]}' como volumen")
                            found = True
                        else:
                            st.error(f"  ❌ No se encontró columna de volumen. REQUERIDA.")
                            df['volume'] = 0
                    elif req_col == 'difficulty':
                        st.error(f"  ❌ No se encontró columna de difficulty. REQUERIDA.")
                        df['difficulty'] = 50  # Valor medio por defecto
                    elif req_col == 'cpc':
                        st.error(f"  ❌ No se encontró columna de CPC. REQUERIDA.")
                        df['cpc'] = 0
        
        # Columnas opcionales
        if 'traffic' not in df.columns:
            # Estimar tráfico como % del volumen (CTR aproximado del 30%)
            df['traffic'] = df['volume'] * 0.3
            st.info(f"  ℹ️ Tráfico estimado como 30% del volumen")
        
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
        
        # Convertir difficulty a numérico y normalizar a 0-100
        df['difficulty'] = pd.to_numeric(df['difficulty'], errors='coerce').fillna(50)
        # Asegurar que está entre 0 y 100
        df['difficulty'] = df['difficulty'].clip(0, 100).astype(int)
        
        # Convertir CPC a numérico
        df['cpc'] = pd.to_numeric(df['cpc'], errors='coerce').fillna(0).astype(float)
        
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
