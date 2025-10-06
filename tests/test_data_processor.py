"""
Tests unitarios para el módulo DataProcessor
"""

import pytest
import pandas as pd
import numpy as np
from app.components.data_processor import DataProcessor

@pytest.fixture
def sample_dataframe():
    """Crea un DataFrame de ejemplo para testing"""
    return pd.DataFrame({
        'keyword': ['seo tools', 'keyword research', 'seo audit', 'backlink checker', 
                   'rank tracker', 'seo tools', 'seo software'],
        'volume': [10000, 8000, 5000, 3000, 2000, 10000, 7000],
        'traffic': [3000, 2400, 1500, 900, 600, 3000, 2100],
        'difficulty': [50, 60, 45, 55, 40, 50, 48]
    })

@pytest.fixture
def processor():
    """Crea una instancia de DataProcessor"""
    return DataProcessor()

class TestDataProcessor:
    
    def test_normalize_columns(self, processor):
        """Test normalización de columnas"""
        df = pd.DataFrame({
            'Keyword': ['test'],
            'Volume': [100],
            'Traffic': [30]
        })
        
        result = processor._normalize_columns(df)
        
        assert 'keyword' in result.columns
        assert 'volume' in result.columns
        assert 'traffic' in result.columns
    
    def test_clean_data(self, processor):
        """Test limpieza de datos"""
        df = pd.DataFrame({
            'keyword': ['test1', 'TEST2', ' test3 ', '', None],
            'volume': [100, '200', 'abc', 0, 50],
            'traffic': [30, 60, None, 0, 15]
        })
        
        result = processor._clean_data(df)
        
        # Verificar que se eliminaron filas inválidas
        assert len(result) == 3  # Solo test1, TEST2 y test3
        
        # Verificar que keywords están en minúsculas y sin espacios
        assert all(result['keyword'].str.islower())
        assert all(~result['keyword'].str.contains(' $|^ '))
        
        # Verificar que volumen es numérico
        assert result['volume'].dtype in [np.int64, np.float64]
    
    def test_deduplicate_keywords(self, processor, sample_dataframe):
        """Test deduplicación de keywords"""
        result = processor._deduplicate_keywords(sample_dataframe)
        
        # Debe mantener solo una instancia de 'seo tools'
        seo_tools_count = (result['keyword'] == 'seo tools').sum()
        assert seo_tools_count == 1
        
        # Debe mantener el de mayor volumen
        seo_tools_row = result[result['keyword'] == 'seo tools'].iloc[0]
        assert seo_tools_row['volume'] == 10000
    
    def test_calculate_metrics(self, processor, sample_dataframe):
        """Test cálculo de métricas adicionales"""
        result = processor._calculate_metrics(sample_dataframe)
        
        # Verificar que se añadieron nuevas columnas
        assert 'ctr_estimate' in result.columns
        assert 'keyword_length' in result.columns
        assert 'keyword_type' in result.columns
        assert 'opportunity_score' in result.columns
        
        # Verificar tipos de keyword
        assert result['keyword_type'].isin(['short-tail', 'mid-tail', 'long-tail']).all()
    
    def test_filter_branded_keywords(self, processor):
        """Test filtrado de keywords branded"""
        df = pd.DataFrame({
            'keyword': ['nike shoes', 'running shoes', 'nike store', 'adidas sneakers'],
            'volume': [10000, 8000, 5000, 7000],
            'traffic': [3000, 2400, 1500, 2100]
        })
        
        result = processor.filter_branded_keywords(df, ['nike'])
        
        # No debe incluir keywords con 'nike'
        assert len(result) == 2
        assert 'nike' not in ' '.join(result['keyword'].tolist())
    
    def test_get_stats(self, processor, sample_dataframe):
        """Test obtención de estadísticas"""
        # Primero calcular métricas para tener keyword_type
        df = processor._calculate_metrics(sample_dataframe)
        stats = processor.get_stats(df)
        
        assert 'total_keywords' in stats
        assert 'unique_keywords' in stats
        assert 'total_volume' in stats
        assert 'avg_volume' in stats
        assert 'keyword_types' in stats
        
        assert stats['total_keywords'] == len(df)
        assert stats['total_volume'] == df['volume'].sum()
    
    def test_sample_keywords_top(self, processor, sample_dataframe):
        """Test muestreo de keywords - método top"""
        result = processor.sample_keywords(sample_dataframe, n=3, method='top')
        
        assert len(result) == 3
        # Debe retornar las de mayor volumen
        assert result.iloc[0]['volume'] >= result.iloc[1]['volume']
    
    def test_sample_keywords_random(self, processor, sample_dataframe):
        """Test muestreo de keywords - método random"""
        result = processor.sample_keywords(sample_dataframe, n=3, method='random')
        
        assert len(result) == 3
        assert len(result) <= len(sample_dataframe)
    
    def test_empty_dataframe_handling(self, processor):
        """Test manejo de DataFrame vacío"""
        df = pd.DataFrame()
        
        with pytest.raises(Exception):
            processor._clean_data(df)
    
    def test_missing_required_columns(self, processor):
        """Test manejo de columnas requeridas faltantes"""
        df = pd.DataFrame({
            'some_column': [1, 2, 3]
        })
        
        # Debería intentar inferir o añadir columnas requeridas
        result = processor._normalize_columns(df)
        assert 'keyword' in result.columns or 'volume' in result.columns


class TestDataIntegration:
    """Tests de integración para el procesamiento completo"""
    
    def test_full_processing_pipeline(self, processor):
        """Test del pipeline completo de procesamiento"""
        # Simular datos de múltiples fuentes con diferentes formatos
        df1 = pd.DataFrame({
            'Keyword': ['test1', 'test2'],
            'Volume': [1000, 2000],
            'Traffic': [300, 600]
        })
        
        df2 = pd.DataFrame({
            'keyword': ['test3', 'test1'],  # test1 duplicado
            'search_volume': [3000, 1500],
            'clicks': [900, 450]
        })
        
        # Normalizar cada uno
        df1_norm = processor._normalize_columns(df1)
        df2_norm = processor._normalize_columns(df2)
        
        # Combinar
        combined = pd.concat([df1_norm, df2_norm], ignore_index=True)
        
        # Limpiar
        cleaned = processor._clean_data(combined)
        
        # Deduplicar
        deduped = processor._deduplicate_keywords(cleaned)
        
        # Calcular métricas
        final = processor._calculate_metrics(deduped)
        
        # Verificaciones
        assert len(final) == 3  # test1, test2, test3
        assert 'keyword_type' in final.columns
        assert 'opportunity_score' in final.columns
        assert final['keyword'].nunique() == 3


@pytest.fixture
def sample_csv_content():
    """Contenido CSV de ejemplo"""
    return """Keyword,Volume,Traffic,Difficulty
seo tools,10000,3000,50
keyword research,8000,2400,60
seo audit,5000,1500,45"""


def test_csv_parsing(processor, sample_csv_content, tmp_path):
    """Test parseo de archivos CSV"""
    # Crear archivo temporal
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(sample_csv_content)
    
    # Leer con pandas
    df = pd.read_csv(csv_file)
    
    # Procesar
    result = processor._normalize_columns(df)
    result = processor._clean_data(result)
    
    assert len(result) == 3
    assert 'keyword' in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
