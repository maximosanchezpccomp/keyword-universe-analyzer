"""
Ejemplo de uso de Keyword Universe Analyzer de forma programática

Este script muestra cómo usar la herramienta sin la interfaz de Streamlit,
útil para automatización, scripts, o integración con otros sistemas.
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.services.anthropic_service import AnthropicService
from app.services.semrush_service import SemrushService
from app.components.data_processor import DataProcessor
from app.components.visualizer import KeywordVisualizer
from app.utils.helpers import export_to_excel, calculate_metrics

# Cargar variables de entorno
load_dotenv()

def example_basic_analysis():
    """Ejemplo básico: Analizar un CSV local"""
    
    print("📊 Ejemplo 1: Análisis básico de CSV\n")
    
    # 1. Cargar datos desde CSV
    print("1. Cargando datos...")
    df = pd.read_csv('data/raw/keywords_example.csv')
    print(f"   ✓ {len(df)} keywords cargadas\n")
    
    # 2. Procesar datos
    print("2. Procesando datos...")
    processor = DataProcessor()
    df_clean = processor._normalize_columns(df)
    df_clean = processor._clean_data(df_clean)
    df_clean = processor._calculate_metrics(df_clean)
    print(f"   ✓ {len(df_clean)} keywords procesadas\n")
    
    # 3. Obtener estadísticas
    print("3. Estadísticas:")
    stats = calculate_metrics(df_clean)
    print(f"   - Total keywords: {stats['total_keywords']:,}")
    print(f"   - Volumen total: {stats['total_volume']:,}")
    print(f"   - Volumen promedio: {stats['avg_volume']:,}\n")
    
    # 4. Analizar con Claude
    print("4. Analizando con Claude...")
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not anthropic_key:
        print("   ⚠️  ANTHROPIC_API_KEY no configurada")
        return
    
    claude = AnthropicService(anthropic_key)
    prompt = claude.create_universe_prompt(
        df_clean,
        analysis_type="Temática (Topics)",
        num_tiers=3,
        include_gaps=True,
        include_trends=True
    )
    
    result = claude.analyze_keywords(prompt, df_clean)
    print(f"   ✓ Análisis completado\n")
    
    # 5. Mostrar resultados
    print("5. Resultados:")
    print(f"\n{result['summary']}\n")
    
    if 'topics' in result:
        print(f"Topics identificados: {len(result['topics'])}")
        for topic in result['topics'][:5]:
            print(f"   - {topic['topic']} (Tier {topic['tier']}): {topic['volume']:,} búsquedas")
    
    print("\n✅ Ejemplo completado\n")
    return result


def example_semrush_api():
    """Ejemplo: Obtener keywords directamente de Semrush"""
    
    print("🔍 Ejemplo 2: Obtener keywords desde Semrush API\n")
    
    semrush_key = os.getenv('SEMRUSH_API_KEY')
    
    if not semrush_key:
        print("⚠️  SEMRUSH_API_KEY no configurada")
        return
    
    # 1. Conectar con Semrush
    print("1. Conectando con Semrush...")
    semrush = SemrushService(semrush_key)
    
    # 2. Obtener keywords de un dominio
    domain = "ahrefs.com"
    print(f"2. Obteniendo keywords de {domain}...")
    
    try:
        keywords_df = semrush.get_organic_keywords(
            domain=domain,
            limit=500,
            filter_branded=True
        )
        print(f"   ✓ {len(keywords_df)} keywords obtenidas\n")
        
        # 3. Mostrar muestra
        print("3. Muestra de keywords:")
        print(keywords_df.head(10)[['keyword', 'volume', 'traffic', 'position']].to_string())
        
        print("\n✅ Ejemplo completado\n")
        return keywords_df
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}\n")
        return None


def example_multiple_competitors():
    """Ejemplo: Analizar múltiples competidores"""
    
    print("🏆 Ejemplo 3: Análisis de múltiples competidores\n")
    
    # Lista de competidores
    competitors = [
        "ahrefs.com",
        "semrush.com",
        "moz.com"
    ]
    
    semrush_key = os.getenv('SEMRUSH_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not semrush_key or not anthropic_key:
        print("⚠️  API keys no configuradas")
        return
    
    # 1. Obtener keywords de todos los competidores
    print("1. Obteniendo keywords de competidores...")
    semrush = SemrushService(semrush_key)
    
    all_keywords = []
    for competitor in competitors:
        try:
            print(f"   - {competitor}...", end=" ")
            kw_df = semrush.get_organic_keywords(
                domain=competitor,
                limit=300,
                filter_branded=True
            )
            all_keywords.append(kw_df)
            print(f"✓ {len(kw_df)} keywords")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    if not all_keywords:
        print("\n⚠️  No se obtuvieron keywords")
        return
    
    # 2. Combinar y deduplicar
    print("\n2. Combinando datos...")
    combined_df = pd.concat(all_keywords, ignore_index=True)
    processor = DataProcessor()
    combined_df = processor._deduplicate_keywords(combined_df)
    print(f"   ✓ {len(combined_df)} keywords únicas\n")
    
    # 3. Analizar con Claude
    print("3. Analizando con Claude...")
    claude = AnthropicService(anthropic_key)
    prompt = claude.create_universe_prompt(
        combined_df,
        analysis_type="Competitivo",
        num_tiers=3,
        custom_instructions=f"Analiza keywords de {len(competitors)} competidores en el espacio de herramientas SEO"
    )
    
    result = claude.analyze_keywords(prompt, combined_df)
    print("   ✓ Análisis completado\n")
    
    # 4. Exportar resultados
    print("4. Exportando resultados...")
    excel_data = export_to_excel(result, include_visuals=True)
    
    output_path = ROOT_DIR / 'outputs' / 'competitor_analysis.xlsx'
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(excel_data)
    
    print(f"   ✓ Exportado a: {output_path}\n")
    print("✅ Ejemplo completado\n")
    
    return result


def example_visualizations():
    """Ejemplo: Crear visualizaciones"""
    
    print("📈 Ejemplo 4: Crear visualizaciones\n")
    
    # Datos de ejemplo
    topics_data = {
        'topic': ['SEO Tools', 'Keyword Research', 'Backlinks', 'Rank Tracking', 'Technical SEO'],
        'tier': [1, 1, 2, 2, 3],
        'keyword_count': [150, 120, 80, 60, 40],
        'volume': [500000, 350000, 150000, 100000, 50000],
        'traffic': [150000, 105000, 45000, 30000, 15000],
        'priority': ['high', 'high', 'medium', 'medium', 'low']
    }
    
    topics_df = pd.DataFrame(topics_data)
    
    print("1. Creando visualizaciones...")
    visualizer = KeywordVisualizer()
    
    # Bubble chart
    fig_bubble = visualizer.create_bubble_chart(topics_df)
    fig_bubble.write_html(ROOT_DIR / 'outputs' / 'bubble_chart.html')
    print("   ✓ Bubble chart guardado")
    
    # Treemap
    fig_treemap = visualizer.create_treemap(topics_df)
    fig_treemap.write_html(ROOT_DIR / 'outputs' / 'treemap.html')
    print("   ✓ Treemap guardado")
    
    # Bar chart
    fig_bar = visualizer.create_bar_chart(topics_df)
    fig_bar.write_html(ROOT_DIR / 'outputs' / 'bar_chart.html')
    print("   ✓ Bar chart guardado")
    
    print("\n✅ Visualizaciones guardadas en outputs/\n")


def example_content_calendar():
    """Ejemplo: Generar calendario de contenido"""
    
    print("📅 Ejemplo 5: Generar calendario de contenido\n")
    
    from app.utils.helpers import create_content_calendar
    
    # Datos de ejemplo de topics
    topics_data = {
        'topic': ['SEO Basics', 'Link Building', 'Technical SEO', 'Content Strategy', 
                 'Local SEO', 'E-commerce SEO', 'Mobile SEO', 'SEO Tools'],
        'tier': [1, 1, 2, 1, 2, 2, 3, 1],
        'keyword_count': [150, 120, 80, 200, 60, 90, 40, 180],
        'volume': [500000, 350000, 150000, 600000, 100000, 200000, 50000, 450000],
        'priority': ['high', 'high', 'medium', 'high', 'medium', 'medium', 'low', 'high']
    }
    
    topics_df = pd.DataFrame(topics_data)
    
    print("1. Generando calendario de contenido para 12 semanas...")
    calendar_df = create_content_calendar(topics_df, weeks=12)
    
    print("\n2. Calendario generado:\n")
    print(calendar_df.to_string(index=False))
    
    # Exportar
    output_path = ROOT_DIR / 'outputs' / 'content_calendar.csv'
    calendar_df.to_csv(output_path, index=False)
    print(f"\n3. ✓ Calendario exportado a: {output_path}\n")
    
    print("✅ Ejemplo completado\n")


def main():
    """Ejecutar todos los ejemplos"""
    
    print("=" * 60)
    print("  KEYWORD UNIVERSE ANALYZER - EJEMPLOS DE USO")
    print("=" * 60)
    print()
    
    # Verificar que existen las API keys
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  ANTHROPIC_API_KEY no está configurada en .env")
        print("   Algunos ejemplos no funcionarán.\n")
    
    # Menú
    print("Selecciona un ejemplo:")
    print("1. Análisis básico de CSV")
    print("2. Obtener keywords desde Semrush")
    print("3. Análisis de múltiples competidores")
    print("4. Crear visualizaciones")
    print("5. Generar calendario de contenido")
    print("6. Ejecutar todos")
    print("0. Salir")
    
    choice = input("\nOpción: ").strip()
    
    print()
    
    examples = {
        '1': example_basic_analysis,
        '2': example_semrush_api,
        '3': example_multiple_competitors,
        '4': example_visualizations,
        '5': example_content_calendar
    }
    
    if choice == '6':
        for func in examples.values():
            try:
                func()
            except Exception as e:
                print(f"⚠️  Error en ejemplo: {str(e)}\n")
    elif choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"⚠️  Error: {str(e)}\n")
    elif choice == '0':
        print("👋 Adiós!\n")
    else:
        print("⚠️  Opción no válida\n")


if __name__ == "__main__":
    main()
