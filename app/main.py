import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.anthropic_service import AnthropicService
from app.services.semrush_service import SemrushService
from app.services.url_analyzer_service import URLAnalyzerService
from app.components.data_processor import DataProcessor
from app.components.visualizer import KeywordVisualizer
from app.utils.helpers import export_to_excel, calculate_metrics

# Importar configuración del logo
try:
    from config import LOGO_URL, LOGO_BASE64
except ImportError:
    LOGO_URL = "https://cdn.pccomponentes.com/img/logos/logo-pccomponentes.svg"
    LOGO_BASE64 = None

# Configuración de la página
st.set_page_config(
    page_title="Keyword Universe Analyzer",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con branding PC Componentes
st.markdown("""
<style>
    :root {
        --pc-orange: #FF6000;
        --pc-orange-light: #FF8640;
        --pc-orange-lighter: #FFD7BF;
        --pc-blue-dark: #090029;
        --pc-blue-medium: #170453;
        --pc-blue-light: #51437E;
        --pc-gray-dark: #999999;
        --pc-gray-medium: #CCCCCC;
        --pc-white: #FFFFFF;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6000 0%, #FF8640 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .main-subtitle {
        color: #170453;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #FF6000 0%, #FF8640 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(255, 96, 0, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF8640 0%, #FF6000 100%);
        box-shadow: 0 4px 12px rgba(255, 96, 0, 0.4);
        transform: translateY(-1px);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #170453 0%, #090029 100%) !important;
    }
    
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] section {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #E8E6F0 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #FFB380 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: rgba(255, 96, 0, 0.25) !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 134, 64, 0.4) !important;
        padding: 0.75rem 1rem !important;
    }
    
    [data-testid="stSidebar"] input[type="text"],
    [data-testid="stSidebar"] input[type="password"],
    [data-testid="stSidebar"] input[type="number"],
    [data-testid="stSidebar"] textarea {
        background-color: #1F0A5C !important;
        border: 1px solid rgba(81, 67, 126, 0.4) !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        padding: 0.65rem !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox div {
        background-color: #1F0A5C !important;
        border: 1px solid rgba(81, 67, 126, 0.4) !important;
        border-radius: 6px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F5F5F5;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        background-color: transparent;
        color: #170453;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #FFD7BF;
        color: #FF6000;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6000 0%, #FF8640 100%);
        color: white !important;
        border-color: #FF6000;
    }
    
    [data-testid="stFileUploader"] {
        border: 2px dashed #FF8640;
        border-radius: 10px;
        padding: 2rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F5 100%);
    }
    
    h2 {
        border-bottom: 3px solid #FF6000;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'keyword_universe' not in st.session_state:
    st.session_state.keyword_universe = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

def display_logo():
    """Muestra el logo con sistema de fallback"""
    if LOGO_URL:
        try:
            st.image(LOGO_URL, width=120)
            return True
        except:
            pass
    
    if LOGO_BASE64:
        try:
            st.markdown(
                f'<img src="{LOGO_BASE64}" width="120" style="border-radius: 8px;">',
                unsafe_allow_html=True
            )
            return True
        except:
            pass
    
    if os.path.exists("assets/pc_logo.png"):
        try:
            st.image("assets/pc_logo.png", width=120)
            return True
        except:
            pass
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FF6000 0%, #FF8640 100%); 
                padding: 1rem; border-radius: 10px; text-align: center;
                width: 120px; box-shadow: 0 2px 8px rgba(255, 96, 0, 0.3);">
        <span style="color: white; font-size: 1.5rem; font-weight: 800; 
                     letter-spacing: 2px;">PC</span>
    </div>
    """, unsafe_allow_html=True)
    return False


def main():
    # Header con logo
    col_logo, col_title = st.columns([1, 4])
    
    with col_logo:
        display_logo()
    
    with col_title:
        st.markdown('<h1 class="main-header fade-in">🌌 Keyword Universe Analyzer</h1>', unsafe_allow_html=True)
        st.markdown('<p class="main-subtitle fade-in">Análisis SEO con IA - Powered by PC Componentes</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        with st.expander("🤖 Proveedor de IA", expanded=True):
            ai_provider = st.selectbox(
                "Selecciona el proveedor de IA",
                ["Claude (Anthropic)", "OpenAI", "Ambos (Validación Cruzada)"],
                help="Claude Sonnet 4.5 es más analítico. GPT-4o es más rápido."
            )
        
        with st.expander("🔑 API Keys", expanded=True):
            anthropic_key = None
            openai_key = None
            
            if ai_provider in ["Claude (Anthropic)", "Ambos (Validación Cruzada)"]:
                anthropic_key = st.text_input("Anthropic API Key", type="password", 
                                             help="Tu API key de Claude")
            
            if ai_provider in ["OpenAI", "Ambos (Validación Cruzada)"]:
                openai_key = st.text_input("OpenAI API Key", type="password",
                                          help="Tu API key de OpenAI")
            
            semrush_key = st.text_input("Semrush API Key", type="password",
                                       help="Tu API key de Semrush (opcional)")
        
        with st.expander("🎯 Parámetros de Análisis"):
            max_keywords = st.slider("Máximo de keywords por competidor", 
                                    100, 5000, 1000, 100)
            min_volume = st.number_input("Volumen mínimo de búsqueda", 
                                        min_value=0, value=10)
            
            model_choice = None
            claude_model = None
            openai_model = None
            
            if ai_provider == "Claude (Anthropic)":
                model_choice = st.selectbox("Modelo Claude", 
                                           ["claude-sonnet-4-5-20250929", 
                                            "claude-opus-4-20250514"])
            elif ai_provider == "OpenAI":
                model_choice = st.selectbox("Modelo OpenAI",
                                           ["gpt-4o",
                                            "gpt-4-turbo",
                                            "gpt-4",
                                            "gpt-3.5-turbo"])
            else:
                col1, col2 = st.columns(2)
                with col1:
                    claude_model = st.selectbox("Modelo Claude", 
                                               ["claude-sonnet-4-5-20250929", 
                                                "claude-opus-4-20250514"])
                with col2:
                    openai_model = st.selectbox("Modelo OpenAI",
                                               ["gpt-4o",
                                                "gpt-4-turbo"])
        
        st.divider()
        st.info("💡 **Tip:** Sube archivos CSV o Excel de Ahrefs, Semrush o similar")
    
    # TABS PRINCIPALES - AHORA CON 5 PESTAÑAS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📁 Carga de Datos", 
        "🧠 Análisis con IA", 
        "📊 Visualización",
        "📥 Exportar",
        "🔗 Análisis de URLs"
    ])
    
    # TAB 1: Carga de datos
    with tab1:
        st.header("Carga tus archivos de keywords")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Opción 1: Cargar archivos exportados")
            uploaded_files = st.file_uploader(
                "Sube archivos CSV o Excel de tus competidores",
                type=['csv', 'xlsx', 'xls'],
                accept_multiple_files=True,
                help="Archivos exportados de Ahrefs, Semrush, etc."
            )
            
            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                st.success(f"✅ {len(uploaded_files)} archivo(s) cargado(s)")
                
                for file in uploaded_files:
                    with st.expander(f"👁️ Preview: {file.name}"):
                        try:
                            if file.name.endswith('.csv'):
                                df = pd.read_csv(file)
                            else:
                                df = pd.read_excel(file)
                            
                            st.dataframe(df.head(10), use_container_width=True)
                            st.caption(f"Total rows: {len(df)} | Columns: {', '.join(df.columns)}")
                        except Exception as e:
                            st.error(f"Error al leer el archivo: {str(e)}")
        
        with col2:
            st.subheader("Opción 2: Semrush API")
            
            if semrush_key:
                competitor_domains = st.text_area(
                    "Dominios competidores (uno por línea)",
                    placeholder="example.com\ncompetitor.com",
                    height=150
                )
                
                if st.button("🔍 Obtener Keywords", type="primary"):
                    if competitor_domains:
                        domains = [d.strip() for d in competitor_domains.split('\n') if d.strip()]
                        
                        with st.spinner("Obteniendo datos de Semrush..."):
                            semrush = SemrushService(semrush_key)
                            all_data = []
                            
                            progress_bar = st.progress(0)
                            for i, domain in enumerate(domains):
                                try:
                                    data = semrush.get_organic_keywords(domain, limit=max_keywords)
                                    all_data.append(data)
                                    st.success(f"✅ {domain}: {len(data)} keywords")
                                except Exception as e:
                                    st.error(f"❌ Error con {domain}: {str(e)}")
                                
                                progress_bar.progress((i + 1) / len(domains))
                            
                            if all_data:
                                st.session_state.processed_data = pd.concat(all_data, ignore_index=True)
                                st.success(f"🎉 Total: {len(st.session_state.processed_data)} keywords obtenidas")
            else:
                st.warning("⚠️ Ingresa tu API key de Semrush")
    
    # TAB 2: Análisis con IA
    with tab2:
        st.header("Análisis con IA")
        
        has_valid_keys = True
        
        if ai_provider == "Claude (Anthropic)" and not anthropic_key:
            st.warning("⚠️ Por favor ingresa tu API key de Anthropic en la barra lateral")
            has_valid_keys = False
        elif ai_provider == "OpenAI" and not openai_key:
            st.warning("⚠️ Por favor ingresa tu API key de OpenAI en la barra lateral")
            has_valid_keys = False
        elif ai_provider == "Ambos (Validación Cruzada)" and (not anthropic_key or not openai_key):
            st.warning("⚠️ Para validación cruzada necesitas ambas API keys")
            has_valid_keys = False
        
        if has_valid_keys:
            if not st.session_state.uploaded_files and st.session_state.processed_data is None:
                st.info("📁 Primero carga datos en la pestaña 'Carga de Datos'")
            else:
                if st.session_state.processed_data is None and st.session_state.uploaded_files:
                    processor = DataProcessor()
                    st.session_state.processed_data = processor.process_files(
                        st.session_state.uploaded_files, 
                        max_keywords
                    )
                
                if st.session_state.processed_data is not None:
                    df = st.session_state.processed_data
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Keywords", f"{len(df):,}")
                    with col2:
                        st.metric("Volumen Total", f"{df['volume'].sum():,.0f}")
                    with col3:
                        st.metric("Keywords Únicas", f"{df['keyword'].nunique():,}")
                    with col4:
                        st.metric("Volumen Promedio", f"{df['volume'].mean():,.0f}")
                    
                    st.divider()
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Configuración del análisis")
                        
                        analysis_type = st.radio(
                            "Tipo de agrupación",
                            ["Temática (Topics)", "Intención de búsqueda", "Funnel de conversión"],
                            horizontal=True
                        )
                        
                        num_tiers = st.slider("Número de niveles (tiers)", 2, 5, 3)
                        
                        custom_instructions = st.text_area(
                            "Instrucciones adicionales (opcional)",
                            placeholder="Ej: Enfócate en keywords transaccionales, agrupa por producto, etc.",
                            height=100
                        )
                    
                    with col2:
                        st.subheader("Opciones avanzadas")
                        include_semantic = st.checkbox("Análisis semántico profundo", value=True)
                        include_trends = st.checkbox("Identificar tendencias emergentes", value=True)
                        include_gaps = st.checkbox("Detectar gaps de contenido", value=True)
                    
                    if st.button("🚀 Analizar con IA", type="primary", use_container_width=True):
                        with st.spinner(f"🧠 {ai_provider.split('(')[0].strip()} está analizando..."):
                            try:
                                if ai_provider == "Claude (Anthropic)":
                                    anthropic_service = AnthropicService(anthropic_key, model_choice)
                                    
                                    prompt = anthropic_service.create_universe_prompt(
                                        df,
                                        analysis_type=analysis_type,
                                        num_tiers=num_tiers,
                                        custom_instructions=custom_instructions,
                                        include_semantic=include_semantic,
                                        include_trends=include_trends,
                                        include_gaps=include_gaps
                                    )
                                    
                                    result = anthropic_service.analyze_keywords(prompt, df)
                                    result['provider'] = 'Claude'
                                    result['model'] = model_choice
                                    
                                elif ai_provider == "OpenAI":
                                    from app.services.openai_service import OpenAIService
                                    
                                    openai_service = OpenAIService(openai_key, model_choice)
                                    
                                    messages = openai_service.create_universe_prompt(
                                        df,
                                        analysis_type=analysis_type,
                                        num_tiers=num_tiers,
                                        custom_instructions=custom_instructions,
                                        include_semantic=include_semantic,
                                        include_trends=include_trends,
                                        include_gaps=include_gaps
                                    )
                                    
                                    result = openai_service.analyze_keywords(messages, df)
                                    result['provider'] = 'OpenAI'
                                    result['model'] = model_choice
                                    
                                else:
                                    from app.services.openai_service import OpenAIService
                                    
                                    st.info("1️⃣ Analizando con Claude...")
                                    anthropic_service = AnthropicService(anthropic_key, claude_model)
                                    
                                    prompt_claude = anthropic_service.create_universe_prompt(
                                        df,
                                        analysis_type=analysis_type,
                                        num_tiers=num_tiers,
                                        custom_instructions=custom_instructions,
                                        include_semantic=include_semantic,
                                        include_trends=include_trends,
                                        include_gaps=include_gaps
                                    )
                                    
                                    result_claude = anthropic_service.analyze_keywords(prompt_claude, df)
                                    
                                    st.info("2️⃣ Analizando con OpenAI...")
                                    openai_service = OpenAIService(openai_key, openai_model)
                                    
                                    messages_openai = openai_service.create_universe_prompt(
                                        df,
                                        analysis_type=analysis_type,
                                        num_tiers=num_tiers,
                                        custom_instructions=custom_instructions,
                                        include_semantic=include_semantic,
                                        include_trends=include_trends,
                                        include_gaps=include_gaps
                                    )
                                    
                                    result_openai = openai_service.analyze_keywords(messages_openai, df)
                                    
                                    st.info("3️⃣ Comparando resultados...")
                                    comparison = openai_service.compare_with_claude(result_claude, df)
                                    
                                    result = {
                                        'summary': f"**Análisis de Claude:**\n{result_claude.get('summary', '')}\n\n**Análisis de OpenAI:**\n{result_openai.get('summary', '')}",
                                        'topics': result_claude.get('topics', []),
                                        'topics_openai': result_openai.get('topics', []),
                                        'comparison': comparison,
                                        'provider': 'Ambos',
                                        'models': f"Claude: {claude_model} | OpenAI: {openai_model}"
                                    }
                                    
                                    if 'gaps' in result_claude:
                                        result['gaps'] = result_claude['gaps']
                                    if 'trends' in result_claude:
                                        result['trends'] = result_claude['trends']
                                
                                st.session_state.keyword_universe = result
                                st.success("✅ ¡Análisis completado!")
                                st.balloons()
                                
                            except Exception as e:
                                st.error(f"❌ Error en el análisis: {str(e)}")
                                import traceback
                                with st.expander("Ver detalles del error"):
                                    st.code(traceback.format_exc())
                    
                    if st.session_state.keyword_universe:
                        st.divider()
                        st.subheader("📋 Resultados del Análisis")
                        
                        result = st.session_state.keyword_universe
                        
                        provider_col1, provider_col2 = st.columns(2)
                        with provider_col1:
                            st.metric("Proveedor de IA", result.get('provider', 'N/A'))
                        with provider_col2:
                            if result.get('provider') == 'Ambos':
                                st.metric("Modelos", result.get('models', 'N/A'))
                            else:
                                st.metric("Modelo", result.get('model', 'N/A'))
                        
                        with st.expander("📊 Resumen Ejecutivo", expanded=True):
                            st.markdown(result.get('summary', 'No disponible'))
                        
                        if result.get('provider') == 'Ambos' and 'comparison' in result:
                            with st.expander("🔄 Validación Cruzada", expanded=True):
                                comp = result['comparison']
                                st.markdown("**Validación General:**")
                                st.info(comp.get('validation', 'N/A'))
                                
                                if 'missing_topics' in comp and comp['missing_topics']:
                                    st.markdown("**Topics Adicionales:**")
                                    for topic in comp['missing_topics']:
                                        st.markdown(f"- {topic}")
                                
                                if 'improvements' in comp and comp['improvements']:
                                    st.markdown("**Mejoras Sugeridas:**")
                                    for improvement in comp['improvements']:
                                        st.markdown(f"- {improvement}")
                        
                        if 'topics' in result:
                            st.subheader("🎯 Topics Identificados")
                            
                            topics_df = pd.DataFrame(result['topics'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                tier_filter = st.multiselect(
                                    "Filtrar por Tier",
                                    options=topics_df['tier'].unique(),
                                    default=topics_df['tier'].unique()
                                )
                            with col2:
                                sort_by = st.selectbox("Ordenar por", 
                                                      ["volume", "keyword_count", "priority"])
                            
                            filtered_topics = topics_df[topics_df['tier'].isin(tier_filter)].sort_values(
                                by=sort_by, ascending=False
                            )
                            
                            st.dataframe(filtered_topics, use_container_width=True, height=400)
    
    # TAB 3: Visualización
    with tab3:
        st.header("Visualización del Keyword Universe")
        
        if st.session_state.keyword_universe is None:
            st.info("🧠 Primero realiza el análisis con IA")
        else:
            result = st.session_state.keyword_universe
            
            if 'topics' in result:
                visualizer = KeywordVisualizer()
                topics_df = pd.DataFrame(result['topics'])
                
                st.subheader("🫧 Mapa de Topics (Bubble Chart)")
                fig_bubble = visualizer.create_bubble_chart(topics_df)
                st.plotly_chart(fig_bubble, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🗺️ Treemap por Volumen")
                    fig_treemap = visualizer.create_treemap(topics_df)
                    st.plotly_chart(fig_treemap, use_container_width=True)
                
                with col2:
                    st.subheader("☀️ Distribución por Tier")
                    fig_sunburst = visualizer.create_sunburst(topics_df)
                    st.plotly_chart(fig_sunburst, use_container_width=True)
                
                if 'gaps' in result:
                    st.divider()
                    st.subheader("🎯 Oportunidades de Contenido")
                    
                    for i, gap in enumerate(result['gaps'][:5]):
                        with st.expander(f"💡 Oportunidad {i+1}: {gap.get('topic', 'N/A')}"):
                            st.markdown(gap.get('description', 'N/A'))
                            st.metric("Volumen potencial", f"{gap.get('volume', 0):,.0f}")
    
    # TAB 4: Exportar
    with tab4:
        st.header("Exportar Resultados")
        
        if st.session_state.keyword_universe is None:
            st.info("🧠 Primero realiza el análisis con IA")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📄 Formato de exportación")
                
                export_format = st.radio(
                    "Selecciona el formato",
                    ["Excel (.xlsx)", "CSV", "JSON"],
                    horizontal=True
                )
                
                include_visuals = st.checkbox("Incluir gráficos (solo Excel)", value=True)
                
                if st.button("💾 Generar archivo", type="primary"):
                    with st.spinner("Generando archivo..."):
                        try:
                            if export_format == "Excel (.xlsx)":
                                file_data = export_to_excel(
                                    st.session_state.keyword_universe,
                                    include_visuals
                                )
                                st.download_button(
                                    "⬇️ Descargar Excel",
                                    data=file_data,
                                    file_name=f"keyword_universe_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            elif export_format == "CSV":
                                topics_df = pd.DataFrame(st.session_state.keyword_universe['topics'])
                                csv_data = topics_df.to_csv(index=False)
                                st.download_button(
                                    "⬇️ Descargar CSV",
                                    data=csv_data,
                                    file_name=f"keyword_universe_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv"
                                )
                            else:
                                import json
                                json_data = json.dumps(st.session_state.keyword_universe, indent=2)
                                st.download_button(
                                    "⬇️ Descargar JSON",
                                    data=json_data,
                                    file_name=f"keyword_universe_{datetime.now().strftime('%Y%m%d')}.json",
                                    mime="application/json"
                                )
                            
                            st.success("✅ Archivo generado correctamente")
                        except Exception as e:
                            st.error(f"❌ Error al generar archivo: {str(e)}")
            
            with col2:
                st.subheader("📊 Resumen de datos")
                
                result = st.session_state.keyword_universe
                
                if 'topics' in result:
                    topics_df = pd.DataFrame(result['topics'])
                    
                    st.metric("Total Topics", len(topics_df))
                    st.metric("Keywords Analizadas", topics_df['keyword_count'].sum())
                    st.metric("Volumen Total", f"{topics_df['volume'].sum():,.0f}")
                    
                    st.divider()
                    
                    st.caption("Distribución por Tier:")
                    tier_dist = topics_df.groupby('tier').size()
                    for tier, count in tier_dist.items():
                        st.text(f"Tier {tier}: {count} topics")
    
    # TAB 5: Análisis de URLs
    with tab5:
        st.header("🔗 Análisis de URLs y Directorios")
        
        st.info("""
        **Analiza URLs específicas o directorios completos:**
        - Ver qué keywords rankea cada página
        - Comparar rendimiento entre directorios
        - Detectar canibalización de keywords
        - Auditar contenido de páginas
        """)
        
        if not semrush_key:
            st.warning("⚠️ Para análisis de URLs necesitas tu API key de Semrush")
            semrush_key_url = st.text_input(
                "Ingresa tu Semrush API Key",
                type="password",
                key="semrush_key_urls"
            )
            if semrush_key_url:
                semrush_key = semrush_key_url
        
        if semrush_key:
            url_analyzer = URLAnalyzerService(semrush_key)
            
            analysis_mode = st.radio(
                "Tipo de análisis",
                ["URLs Específicas", "Directorios", "Canibalización"],
                horizontal=True
            )
            
            if analysis_mode == "URLs Específicas":
                st.subheader("📝 Analizar URLs Específicas")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    urls_input = st.text_area(
                        "URLs a analizar (una por línea)",
                        placeholder="https://example.com/blog/article-1\nhttps://example.com/productos/categoria",
                        height=150
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        get_keywords = st.checkbox("Obtener keywords", value=True)
                    with col_b:
                        scrape_content = st.checkbox("Analizar contenido", value=True)
                
                with col2:
                    st.markdown("**Métricas:**")
                    if get_keywords:
                        st.markdown("✅ Keywords rankeando")
                        st.markdown("✅ Volumen de búsqueda")
                        st.markdown("✅ Tráfico estimado")
                    if scrape_content:
                        st.markdown("✅ Title, H1, Meta")
                        st.markdown("✅ Word count")
                
                if st.button("🚀 Analizar URLs", type="primary", key="analyze_urls"):
                    if urls_input:
                        urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
                        
                        if urls:
                            with st.spinner(f"Analizando {len(urls)} URLs..."):
                                try:
                                    results_df = url_analyzer.analyze_multiple_urls(
                                        urls,
                                        use_semrush=get_keywords,
                                        scrape_content=scrape_content
                                    )
                                    
                                    st.success(f"✅ Análisis completado")
                                    
                                    if get_keywords:
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            st.metric("Total Keywords", f"{results_df['total_keywords'].sum():,.0f}")
                                        with col2:
                                            st.metric("Volumen Total", f"{results_df['total_volume'].sum():,.0f}")
                                        with col3:
                                            st.metric("Tráfico Total", f"{results_df['total_traffic'].sum():,.0f}")
                                        with col4:
                                            st.metric("Pos. Promedio", f"{results_df['avg_position'].mean():.1f}")
                                    
                                    st.subheader("📊 Resultados")
                                    st.dataframe(results_df, use_container_width=True, height=400)
                                    
                                    csv = results_df.to_csv(index=False)
                                    st.download_button(
                                        "💾 Descargar CSV",
                                        csv,
                                        f"url_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                                        "text/csv"
                                    )
                                    
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Ingresa al menos una URL")
            
            elif analysis_mode == "Directorios":
                st.subheader("📂 Comparar Directorios")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    domain = st.text_input("Dominio base", placeholder="example.com")
                    
                    directories_input = st.text_area(
                        "Directorios (uno por línea)",
                        placeholder="/blog/\n/productos/\n/guias/",
                        height=150
                    )
                
                with col2:
                    st.markdown("**Casos de uso:**")
                    st.markdown("🎯 Comparar secciones")
                    st.markdown("🎯 Priorizar optimización")
                    st.markdown("🎯 Estrategia de contenido")
                
                if st.button("🔍 Comparar", type="primary", key="compare_dirs"):
                    if domain and directories_input:
                        directories = [d.strip() for d in directories_input.split('\n') if d.strip()]
                        
                        with st.spinner("Analizando directorios..."):
                            try:
                                comparison_df = url_analyzer.compare_directories(domain, directories)
                                
                                if not comparison_df.empty:
                                    st.success("✅ Comparación completada")
                                    
                                    fig = px.bar(
                                        comparison_df.sort_values('total_volume', ascending=False),
                                        x='directory',
                                        y='total_volume',
                                        title='Volumen por Directorio',
                                        color='total_volume',
                                        color_continuous_scale=['#C5C0D4', '#51437E', '#170453', '#FF6000']
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    st.dataframe(comparison_df, use_container_width=True)
                                    
                                    csv = comparison_df.to_csv(index=False)
                                    st.download_button(
                                        "💾 Descargar",
                                        csv,
                                        f"directory_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                                        "text/csv"
                                    )
                                else:
                                    st.warning("No se encontraron datos")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Completa dominio y directorios")
            
            elif analysis_mode == "Canibalización":
                st.subheader("⚠️ Detectar Canibalización")
                
                st.markdown("""
                **¿Qué es?** Múltiples URLs compiten por las mismas keywords,
                diluyendo la autoridad.
                """)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    domain = st.text_input("Dominio", placeholder="example.com", key="canib_domain")
                    
                    min_keywords = st.slider(
                        "Mínimo keywords en común",
                        min_value=3,
                        max_value=20,
                        value=5
                    )
                
                with col2:
                    st.markdown("**Beneficios:**")
                    st.markdown("✅ Identificar duplicados")
                    st.markdown("✅ Consolidar páginas")
                    st.markdown("✅ Mejorar rankings")
                
                if st.button("🔍 Detectar", type="primary", key="detect_canib"):
                    if domain:
                        with st.spinner("Analizando..."):
                            try:
                                canib_df = url_analyzer.detect_cannibalization(
                                    domain,
                                    min_common_keywords=min_keywords
                                )
                                
                                if not canib_df.empty:
                                    st.warning(f"⚠️ {len(canib_df)} casos detectados")
                                    
                                    st.subheader("🚨 Casos Críticos")
                                    
                                    for idx, row in canib_df.head(5).iterrows():
                                        with st.expander(f"🔴 {row['common_keywords_count']} keywords en común"):
                                            col_a, col_b = st.columns(2)
                                            
                                            with col_a:
                                                st.markdown("**URL 1:**")
                                                st.code(row['url_1'], language=None)
                                            
                                            with col_b:
                                                st.markdown("**URL 2:**")
                                                st.code(row['url_2'], language=None)
                                            
                                            st.info(row['common_keywords'])
                                    
                                    st.dataframe(canib_df, use_container_width=True, height=400)
                                    
                                    csv = canib_df.to_csv(index=False)
                                    st.download_button(
                                        "💾 Descargar",
                                        csv,
                                        f"cannibalization_{datetime.now().strftime('%Y%m%d')}.csv",
                                        "text/csv"
                                    )
                                else:
                                    st.success("✅ No se detectó canibalización")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Ingresa el dominio")
        else:
            st.info("👆 Configura tu API key de Semrush")

if __name__ == "__main__":
    main()
