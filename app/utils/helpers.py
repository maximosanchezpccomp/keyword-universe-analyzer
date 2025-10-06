import pandas as pd
import io
from typing import Dict, Any, List
from datetime import datetime
import json

def export_to_excel(keyword_universe: Dict[str, Any], include_visuals: bool = True) -> bytes:
    """
    Exporta el keyword universe a Excel con múltiples hojas y formato
    
    Args:
        keyword_universe: Diccionario con los resultados del análisis
        include_visuals: Si incluir las visualizaciones como imágenes
    
    Returns:
        bytes del archivo Excel
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Resumen Ejecutivo
        summary_data = {
            'Métrica': ['Fecha de Análisis', 'Total Topics', 'Total Keywords', 'Volumen Total'],
            'Valor': [
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                len(keyword_universe.get('topics', [])),
                sum([t['keyword_count'] for t in keyword_universe.get('topics', [])]),
                sum([t['volume'] for t in keyword_universe.get('topics', [])])
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Hoja 2: Topics Completos
        if 'topics' in keyword_universe:
            topics_df = pd.DataFrame(keyword_universe['topics'])
            topics_df = topics_df.sort_values('volume', ascending=False)
            topics_df.to_excel(writer, sheet_name='Topics', index=False)
        
        # Hoja 3: Topics por Tier
        if 'topics' in keyword_universe:
            for tier in sorted(topics_df['tier'].unique()):
                tier_df = topics_df[topics_df['tier'] == tier]
                sheet_name = f'Tier {tier}'
                tier_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Hoja 4: Gaps de Contenido
        if 'gaps' in keyword_universe and keyword_universe['gaps']:
            gaps_df = pd.DataFrame(keyword_universe['gaps'])
            gaps_df.to_excel(writer, sheet_name='Oportunidades', index=False)
        
        # Hoja 5: Tendencias
        if 'trends' in keyword_universe and keyword_universe['trends']:
            trends_df = pd.DataFrame(keyword_universe['trends'])
            trends_df.to_excel(writer, sheet_name='Tendencias', index=False)
        
        # Hoja 6: Resumen Textual
        if 'summary' in keyword_universe:
            summary_text_df = pd.DataFrame({
                'Resumen Ejecutivo': [keyword_universe['summary']]
            })
            summary_text_df.to_excel(writer, sheet_name='Análisis Detallado', index=False)
        
        # Formatear las hojas
        workbook = writer.book
        
        # Aplicar formato a la hoja de resumen
        if 'Resumen' in workbook.sheetnames:
            ws = workbook['Resumen']
            
            # Hacer la primera fila más ancha
            for row in ws.iter_rows(min_row=1, max_row=1):
                for cell in row:
                    cell.font = cell.font.copy(bold=True)
                    cell.fill = cell.fill.copy(fgColor="667eea")
    
    output.seek(0)
    return output.getvalue()


def calculate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula métricas del dataframe de keywords"""
    
    metrics = {
        'total_keywords': len(df),
        'unique_keywords': df['keyword'].nunique(),
        'total_volume': int(df['volume'].sum()),
        'avg_volume': int(df['volume'].mean()),
        'median_volume': int(df['volume'].median()),
        'max_volume': int(df['volume'].max()),
        'min_volume': int(df['volume'].min())
    }
    
    if 'traffic' in df.columns:
        metrics['total_traffic'] = int(df['traffic'].sum())
        metrics['avg_traffic'] = int(df['traffic'].mean())
    
    if 'keyword_length' in df.columns:
        metrics['avg_keyword_length'] = df['keyword_length'].mean()
    
    if 'keyword_type' in df.columns:
        metrics['keyword_distribution'] = df['keyword_type'].value_counts().to_dict()
    
    return metrics


def format_number(num: int) -> str:
    """Formatea números grandes con separadores"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)


def categorize_keyword_intent(keyword: str, df: pd.DataFrame = None) -> str:
    """
    Categoriza la intención de búsqueda de una keyword
    
    Args:
        keyword: La keyword a categorizar
        df: DataFrame opcional con datos adicionales
    
    Returns:
        Categoría de intención: informational, navigational, commercial, transactional
    """
    keyword_lower = keyword.lower()
    
    # Transaccional
    transactional_indicators = [
        'buy', 'comprar', 'precio', 'price', 'order', 'ordenar',
        'purchase', 'discount', 'descuento', 'deal', 'oferta',
        'cheap', 'barato', 'affordable', 'shop', 'tienda'
    ]
    
    # Comercial
    commercial_indicators = [
        'best', 'mejor', 'top', 'review', 'reseña', 'compare',
        'comparar', 'vs', 'alternative', 'alternativa',
        'tool', 'herramienta', 'software', 'app'
    ]
    
    # Navegacional
    navigational_indicators = [
        'login', 'sign in', 'iniciar sesion', 'download', 'descargar',
        'official', 'oficial', 'website', 'sitio web'
    ]
    
    # Informacional (por defecto)
    informational_indicators = [
        'how to', 'como', 'what is', 'que es', 'why', 'por que',
        'when', 'cuando', 'where', 'donde', 'guide', 'guia',
        'tutorial', 'learn', 'aprender', 'tips', 'consejos'
    ]
    
    # Verificar en orden de prioridad
    if any(indicator in keyword_lower for indicator in transactional_indicators):
        return 'transactional'
    elif any(indicator in keyword_lower for indicator in commercial_indicators):
        return 'commercial'
    elif any(indicator in keyword_lower for indicator in navigational_indicators):
        return 'navigational'
    elif any(indicator in keyword_lower for indicator in informational_indicators):
        return 'informational'
    else:
        # Por defecto, si tiene 1-2 palabras es más probable que sea navegacional
        word_count = len(keyword_lower.split())
        if word_count <= 2:
            return 'navigational'
        else:
            return 'informational'


def filter_keywords_by_intent(df: pd.DataFrame, intent: str) -> pd.DataFrame:
    """Filtra keywords por tipo de intención"""
    
    df['intent'] = df['keyword'].apply(categorize_keyword_intent)
    return df[df['intent'] == intent]


def detect_keyword_patterns(df: pd.DataFrame, min_frequency: int = 5) -> List[Dict]:
    """
    Detecta patrones comunes en keywords
    
    Returns:
        Lista de patrones encontrados con su frecuencia
    """
    patterns = []
    
    # Extraer todas las palabras
    all_words = []
    for keyword in df['keyword']:
        words = str(keyword).lower().split()
        all_words.extend(words)
    
    # Contar frecuencias
    from collections import Counter
    word_freq = Counter(all_words)
    
    # Filtrar palabras comunes (stopwords básicas)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 
                'el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'en', 'de'}
    
    for word, freq in word_freq.most_common(50):
        if freq >= min_frequency and word not in stopwords and len(word) > 2:
            patterns.append({
                'pattern': word,
                'frequency': freq,
                'percentage': (freq / len(df)) * 100
            })
    
    return patterns


def create_content_calendar(topics_df: pd.DataFrame, weeks: int = 12) -> pd.DataFrame:
    """
    Crea un calendario de contenido basado en los topics
    
    Args:
        topics_df: DataFrame con los topics
        weeks: Número de semanas para planificar
    
    Returns:
        DataFrame con el calendario de contenido
    """
    # Ordenar por prioridad y volumen
    topics_sorted = topics_df.sort_values(['tier', 'volume'], ascending=[True, False])
    
    # Distribuir en semanas
    topics_per_week = len(topics_sorted) // weeks
    if topics_per_week == 0:
        topics_per_week = 1
    
    calendar = []
    
    for i, (idx, topic) in enumerate(topics_sorted.iterrows()):
        week_num = (i // topics_per_week) + 1
        if week_num > weeks:
            week_num = weeks
        
        calendar.append({
            'week': week_num,
            'topic': topic['topic'],
            'tier': topic['tier'],
            'priority': topic.get('priority', 'medium'),
            'target_keywords': topic['keyword_count'],
            'expected_volume': topic['volume'],
            'content_type': _suggest_content_type(topic),
            'estimated_effort': _estimate_effort(topic)
        })
    
    return pd.DataFrame(calendar)


def _suggest_content_type(topic: pd.Series) -> str:
    """Sugiere el tipo de contenido basado en el topic"""
    
    volume = topic.get('volume', 0)
    keyword_count = topic.get('keyword_count', 0)
    
    if volume > 100000:
        return 'Pilar Content / Hub Page'
    elif volume > 50000:
        return 'In-depth Guide'
    elif keyword_count > 50:
        return 'Comprehensive Article'
    elif keyword_count > 20:
        return 'Standard Article'
    else:
        return 'Blog Post'


def _estimate_effort(topic: pd.Series) -> str:
    """Estima el esfuerzo necesario"""
    
    keyword_count = topic.get('keyword_count', 0)
    
    if keyword_count > 100:
        return 'High (8-12 hours)'
    elif keyword_count > 50:
        return 'Medium (4-8 hours)'
    elif keyword_count > 20:
        return 'Medium-Low (2-4 hours)'
    else:
        return 'Low (1-2 hours)'


def export_to_json(keyword_universe: Dict[str, Any], pretty: bool = True) -> str:
    """Exporta el keyword universe a JSON"""
    
    if pretty:
        return json.dumps(keyword_universe, indent=2, ensure_ascii=False)
    else:
        return json.dumps(keyword_universe, ensure_ascii=False)


def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Valida un DataFrame de keywords y retorna un reporte
    
    Returns:
        Diccionario con el resultado de la validación
    """
    issues = []
    warnings = []
    
    # Verificar columnas requeridas
    required_cols = ['keyword', 'volume']
    for col in required_cols:
        if col not in df.columns:
            issues.append(f"Columna requerida '{col}' no encontrada")
    
    # Verificar datos nulos
    if df['keyword'].isnull().any():
        null_count = df['keyword'].isnull().sum()
        warnings.append(f"{null_count} keywords nulas encontradas")
    
    # Verificar volúmenes negativos o cero
    if 'volume' in df.columns:
        zero_volume = (df['volume'] <= 0).sum()
        if zero_volume > 0:
            warnings.append(f"{zero_volume} keywords con volumen 0 o negativo")
    
    # Verificar duplicados
    duplicates = df['keyword'].duplicated().sum()
    if duplicates > 0:
        warnings.append(f"{duplicates} keywords duplicadas encontradas")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'row_count': len(df),
        'column_count': len(df.columns)
    }
