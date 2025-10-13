import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any  
import sys
import os
from pathlib import Path
from io import BytesIO
import openpyxl

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.anthropic_service import AnthropicService
from app.services.semrush_service import SemrushServiceOptimized as SemrushService
from app.services.architecture_service import ArchitectureService 
from app.components.data_processor import DataProcessor
from app.components.visualizer import KeywordVisualizer
from app.utils.helpers import export_to_excel, calculate_metrics, format_number
from app.utils.cache_manager import CacheManager
from app.utils.helpers import safe_preview_dataframe
from app.utils.cache_manager import get_cache_manager
from config import CACHE_CONFIG, estimate_analysis_cost

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
    /* Colores corporativos PC Componentes */
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
    
    /* Header principal */
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
    
    /* Logo container */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%);
        border-radius: 12px;
        border-left: 4px solid #FF6000;
    }
    
    /* Botones primarios */
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
    
    /* Tarjetas de métricas */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9F9F9 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #FF6000;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(255, 96, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #170453 0%, #090029 100%) !important;
    }
    
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] section,
    [data-testid="stSidebar"] [class*="css"] {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #E8E6F0 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #FFB380 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: rgba(255, 96, 0, 0.25) !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 134, 64, 0.4) !important;
        padding: 0.75rem 1rem !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: rgba(255, 96, 0, 0.35) !important;
        border-color: rgba(255, 134, 64, 0.6) !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: transparent !important;
        border: none !important;
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
    
    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {
        color: #B8A0D4 !important;
        opacity: 0.6 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #1F0A5C !important;
        border: 1px solid rgba(81, 67, 126, 0.4) !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: rgba(81, 67, 126, 0.6) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Tabs */
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
    
    /* Dividers */
    hr {
        border-color: #FF8640;
        margin: 2rem 0;
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
if 'architecture' not in st.session_state:
    st.session_state.architecture = None
if 'analyses_history' not in st.session_state:
    st.session_state.analyses_history = []
if 'multi_analyses' not in st.session_state:
    st.session_state.multi_analyses = {
        'Temática (Topics)': None,
        'Intención de búsqueda': None,
        'Funnel de conversión': None
    }
if 'current_dataset_hash' not in st.session_state:
    st.session_state.current_dataset_hash = None
if 'project_metadata' not in st.session_state:
    st.session_state.project_metadata = {
        'project_name': f"Proyecto {datetime.now().strftime('%Y-%m-%d')}",
        'total_keywords': 0,
        'total_volume': 0
    }


def get_analysis_progress():
    """Retorna el progreso de análisis completados"""
    completed = sum(1 for v in st.session_state.multi_analyses.values() if v is not None)
    total = len(st.session_state.multi_analyses)
    return completed, total


def save_analysis_to_multi(analysis_type: str, result: Dict, df):
    """Guarda un análisis en el tracker multi-análisis"""
    st.session_state.multi_analyses[analysis_type] = result
    
    if df is not None:
        cache_manager = CacheManager()
        st.session_state.current_dataset_hash = cache_manager.get_data_hash(df)
        st.session_state.project_metadata['total_keywords'] = len(df)
        st.session_state.project_metadata['total_volume'] = int(df['volume'].sum())


def reset_multi_analyses():
    """Resetea todos los análisis (nuevo dataset)"""
    st.session_state.multi_analyses = {
        'Temática (Topics)': None,
        'Intención de búsqueda': None,
        'Funnel de conversión': None
    }
    st.session_state.current_dataset_hash = None


def display_logo():
    """Muestra el logo con sistema de fallback en cascada"""
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

    # Inicializar cache manager
    from app.utils.cache_manager import CacheManager
    
    if 'cache_manager' not in st.session_state:
        st.session_state.cache_manager = CacheManager(
            cache_dir="data/cache",
            ttl_hours=24
        )
    
    cache_manager = st.session_state.cache_manager
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selección de proveedor de IA
        with st.expander("🤖 Proveedor de IA", expanded=True):
            ai_provider = st.selectbox(
                "Selecciona el proveedor de IA",
                ["Claude (Anthropic)", "OpenAI", "Ambos (Validación Cruzada)"],
                help="Claude Sonnet 4.5 es más analítico. GPT-4 es más rápido."
            )
        
        # API Keys
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
        
        # Configuración del análisis 
        with st.expander("🎯 Parámetros de Análisis"):
            max_keywords = st.slider("Máximo de keywords por competidor", 
                                    100, 5000, 1000, 100)
            min_volume = st.number_input("Volumen mínimo de búsqueda", 
                                        min_value=0, value=10)
            
            # Inicializar variables por defecto
            model_choice = None
            claude_model = "claude-sonnet-4-5-20250929"
            openai_model = "gpt-4o"
            
            # Selección de modelo según proveedor
            if ai_provider == "Claude (Anthropic)":
                model_choice = st.selectbox("Modelo Claude", 
                                           ["claude-sonnet-4-5-20250929", 
                                            "claude-opus-4-20250514"])
                claude_model = model_choice
                
            elif ai_provider == "OpenAI":
                model_choice = st.selectbox("Modelo OpenAI",
                                           ["gpt-4o",
                                            "gpt-4-turbo",
                                            "gpt-4",
                                            "gpt-3.5-turbo"])
                openai_model = model_choice
                
            else:  # Ambos
                col1, col2 = st.columns(2)
                with col1:
                    claude_model = st.selectbox("Modelo Claude", 
                                               ["claude-sonnet-4-5-20250929", 
                                                "claude-opus-4-20250514"])
                with col2:
                    openai_model = st.selectbox("Modelo OpenAI",
                                               ["gpt-4o",
                                                "gpt-4-turbo"])
                model_choice = claude_model
        
        # Gestión de Caché
        with st.expander("💾 Sistema de Caché", expanded=False):
            st.markdown("**Sistema de caché inteligente**")
            st.markdown("Ahorra costos reutilizando análisis previos")
            
            cache_manager = get_cache_manager()
            
            cache_enabled = st.checkbox(
                "Habilitar caché",
                value=CACHE_CONFIG.get('enabled', True),
                help="Reutiliza análisis previos para ahorrar costos"
            )
            
            ttl_hours = st.slider(
                "Validez del caché (horas)",
                min_value=1,
                max_value=168,
                value=CACHE_CONFIG.get('default_ttl_hours', 24),
                help="Tiempo que permanece válido un análisis en caché"
            )
            
            st.divider()
            
            # Estadísticas del caché
            cache_info = cache_manager.get_cache_info()
            
            st.markdown("**📊 Estadísticas**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Análisis en caché", f"{cache_info['cached_analyses']}")
                st.metric("Hit rate", f"{cache_info['hit_rate']:.1f}%",
                         help="% de análisis recuperados del caché")
            
            with col2:
                st.metric("$ Ahorrado", f"${cache_info['cost_saved']:.2f}",
                         help="Costos ahorrados usando caché")
                st.metric("Tamaño", f"{cache_info['size_mb']} MB")
            
            st.divider()
            
            # Acciones de gestión
            st.markdown("**🔧 Gestión**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Limpiar caché antiguo", help="Elimina análisis con más de 7 días"):
                    deleted = cache_manager.clear_cache(older_than_hours=168)
                    st.success(f"✅ {deleted} análisis eliminados")
                    st.rerun()
            
            with col2:
                if st.button("⚠️ Limpiar todo", help="Elimina TODO el caché"):
                    if st.session_state.get('confirm_clear_all', False):
                        deleted = cache_manager.clear_cache()
                        st.success(f"✅ {deleted} análisis eliminados")
                        st.session_state.confirm_clear_all = False
                        st.rerun()
                    else:
                        st.session_state.confirm_clear_all = True
                        st.warning("⚠️ Haz clic de nuevo para confirmar")
            
            # Listado de análisis recientes
            with st.expander("📋 Análisis en caché (últimos 10)"):
                recent_analyses = cache_manager.list_cached_analyses(limit=10)
                
                if recent_analyses:
                    for analysis in recent_analyses:
                        age_text = f"{analysis['age_hours']:.1f}h" if analysis['age_hours'] < 24 else f"{analysis['age_hours']/24:.1f}d"
                        
                        st.text(f"""
{analysis['provider']} ({analysis['model']})
Antigüedad: {age_text} | Costo: ${analysis['cost']:.3f}
Parámetros: {analysis['parameters'].get('analysis_type', 'N/A')} | Tiers: {analysis['parameters'].get('num_tiers', 'N/A')}
                        """)
                        st.caption(f"Hash: {analysis['hash'][:16]}...")
                        st.divider()
                else:
                    st.info("No hay análisis en caché todavía")
        
        # Análisis Guardados
        with st.expander("💾 Análisis Guardados", expanded=False):
            st.markdown("### Gestión de Análisis")
            
            cache_manager = CacheManager()
            
            # CORRECCIÓN: Obtener estadísticas directamente
            analyses = cache_manager.list_analyses()
            total_analyses = len(analyses)
            
            # Calcular tamaño total (estimado en MB)
            try:
                cache_dir = Path(cache_manager.cache_dir)
                if cache_dir.exists():
                    total_size_bytes = sum(f.stat().st_size for f in cache_dir.glob('*.json') if f.is_file())
                    total_size_mb = round(total_size_bytes / (1024 * 1024), 2)
                else:
                    total_size_mb = 0
            except Exception:
                total_size_mb = 0
            
            col_cache1, col_cache2 = st.columns(2)
            with col_cache1:
                st.metric("Análisis guardados", total_analyses)
            with col_cache2:
                st.metric("Tamaño", f"{total_size_mb} MB")
            
            if analyses:
                st.markdown("#### Cargar Análisis Anterior")
                
                search_query = st.text_input(
                    "🔍 Buscar por nombre",
                    placeholder="placas base, portátiles...",
                    key="cache_search"
                )
                
                if search_query:
                    analyses = cache_manager.search_analyses(search_query)
                
                if analyses:
                    analysis_options = {
                        f"{item['name']} ({item['stats']['total_keywords']:,} kws) - {item['timestamp'][:10]}": item['id']
                        for item in analyses
                    }
                    
                    selected_name = st.selectbox(
                        "Selecciona un análisis",
                        options=list(analysis_options.keys()),
                        key="cache_selector"
                    )
                    
                    if selected_name:
                        selected_id = analysis_options[selected_name]
                        selected_analysis = next(item for item in analyses if item['id'] == selected_id)
                        
                        with st.expander("ℹ️ Detalles", expanded=False):
                            st.write(f"**Descripción:** {selected_analysis.get('description', 'Sin descripción')}")
                            st.write(f"**Fecha:** {selected_analysis['timestamp'][:19]}")
                            st.write(f"**Topics:** {selected_analysis['stats']['total_topics']}")
                            st.write(f"**Volumen total:** {selected_analysis['stats']['total_volume']:,}")
                            st.write(f"**Proveedor:** {selected_analysis['stats']['provider']}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.button("📂 Cargar", type="primary", use_container_width=True, key="load_cache"):
                                with st.spinner("Cargando análisis..."):
                                    loaded = cache_manager.load_analysis(selected_id)
                                    
                                    if loaded:
                                        st.session_state.keyword_universe = loaded['keyword_universe']
                                        
                                        if 'processed_data' in loaded:
                                            st.session_state.processed_data = pd.DataFrame(loaded['processed_data'])
                                        
                                        st.success("✅ Análisis cargado correctamente")
                                        st.info("💡 Ve a la pestaña 'Visualización' o 'Exportar' para ver los resultados")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al cargar el análisis")
                        
                        with col_btn2:
                            if st.button("🗑️ Eliminar", use_container_width=True, key="delete_cache"):
                                if cache_manager.delete_analysis(selected_id):
                                    st.success("✅ Análisis eliminado")
                                    st.rerun()
                                else:
                                    st.error("❌ Error al eliminar")
                else:
                    st.info("No se encontraron análisis con ese criterio")
            else:
                st.info("📭 No hay análisis guardados aún")
                st.caption("Los análisis se guardan automáticamente al completarse")
            
            st.markdown("---")
            st.markdown("#### Gestión de Caché")
            
            if st.button("🗑️ Limpiar toda la caché", key="clear_all_cache"):
                count = cache_manager.clear_cache()
                st.success(f"✅ {count} análisis eliminados")
                st.rerun()
        
        # Widget de Progreso de Análisis
        with st.expander("📊 Progreso de Informes", expanded=True):
            st.markdown("### Estado del Informe Completo")
            
            completed, total = get_analysis_progress()
            
            progress_percentage = completed / total if total > 0 else 0
            st.progress(progress_percentage)
            
            col_prog1, col_prog2 = st.columns(2)
            with col_prog1:
                st.metric("Completados", f"{completed}/{total}")
            with col_prog2:
                if completed == total:
                    st.metric("Estado", "✅ Listo")
                else:
                    st.metric("Pendientes", f"{total - completed}")
            
            st.caption(f"**{int(progress_percentage * 100)}%** del informe completo")
            
            st.markdown("#### Análisis Disponibles")
            
            for analysis_type, analysis_data in st.session_state.multi_analyses.items():
                col_status, col_name = st.columns([1, 5])
                
                with col_status:
                    if analysis_data:
                        st.markdown("✅")
                    else:
                        st.markdown("⏳")
                
                with col_name:
                    if analysis_data:
                        topics_count = len(analysis_data.get('topics', []))
                        st.markdown(f"**{analysis_type}** ({topics_count} topics)")
                    else:
                        st.markdown(f"**{analysis_type}**")
            
            if completed > 0:
                st.markdown("---")
                if st.button("🔄 Reiniciar Todos los Análisis", key="reset_all_analyses"):
                    reset_multi_analyses()
                    st.success("✅ Análisis reiniciados")
                    st.rerun()
        
        st.divider()
        st.info("💡 **Tip:** Sube archivos CSV o Excel de Ahrefs, Semrush o similar con columnas: keyword, volume, traffic")
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📁 Carga de Datos", 
        "🧠 Análisis con IA", 
        "📊 Visualización",
        "🏗️ Arquitectura Web",
        "🎯 Oportunidades",
        "📥 Exportar"
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
                analysis_mode = st.radio(
                    "Tipo de análisis",
                    ["🌐 Dominios", "🔗 URLs", "📁 Directorios", "📋 Mixto"],
                    help="""
                    - Dominios: Analiza un dominio completo
                    - URLs: Analiza páginas específicas
                    - Directorios: Analiza secciones del sitio
                    - Mixto: Combina dominios, URLs y directorios
                    """
                )
                
                if analysis_mode == "🌐 Dominios":
                    targets_input = st.text_area(
                        "Dominios (uno por línea)",
                        placeholder="example.com\ncompetitor.com",
                        height=150
                    )
                    target_type = 'domain'
                    
                elif analysis_mode == "🔗 URLs":
                    targets_input = st.text_area(
                        "URLs completas (una por línea)",
                        placeholder="https://example.com/producto",
                        height=150
                    )
                    target_type = 'url'
                    
                elif analysis_mode == "📁 Directorios":
                    targets_input = st.text_area(
                        "Directorios (uno por línea)",
                        placeholder="example.com/blog/",
                        height=150
                    )
                    target_type = 'directory'
                    
                else:
                    st.info("💡 En modo mixto, especifica el tipo al lado de cada entrada")
                    targets_input = st.text_area(
                        "Targets (formato: tipo|valor)",
                        placeholder="domain|example.com\nurl|https://competitor.com/producto",
                        height=180
                    )
                    target_type = 'mixed'
                
                col_opt1, col_opt2 = st.columns(2)
                with col_opt1:
                    semrush_limit = st.number_input(
                        "Keywords por target",
                        min_value=10,
                        max_value=10000,
                        value=500,
                        step=50
                    )
                
                with col_opt2:
                    semrush_database = st.selectbox(
                        "Base de datos",
                        ["us", "uk", "es", "fr", "de", "it", "br", "mx", "ar"]
                    )
                
                filter_branded = st.checkbox("Filtrar keywords de marca", value=True)
                
                if st.button("🔍 Obtener Keywords de Semrush", type="primary", use_container_width=True):
                    if targets_input:
                        targets_list = []
                        
                        if target_type == 'mixed':
                            for line in targets_input.split('\n'):
                                line = line.strip()
                                if '|' in line:
                                    tipo, valor = line.split('|', 1)
                                    tipo = tipo.strip().lower()
                                    valor = valor.strip()
                                    
                                    if tipo in ['domain', 'url', 'directory'] and valor:
                                        targets_list.append({'target': valor, 'type': tipo})
                        else:
                            for line in targets_input.split('\n'):
                                line = line.strip()
                                if line:
                                    targets_list.append({'target': line, 'type': target_type})
                        
                        if not targets_list:
                            st.error("❌ No se encontraron targets válidos")
                        else:
                            with st.spinner(f"🔄 Obteniendo datos de Semrush ({len(targets_list)} targets)..."):
                                try:
                                    semrush = SemrushService(semrush_key)
                                    
                                    all_data = semrush.batch_get_keywords(
                                        targets=targets_list,
                                        limit=semrush_limit,
                                        delay=1.0,
                                        database=semrush_database
                                    )
                                    
                                    if len(all_data) > 0:
                                        st.session_state.processed_data = all_data
                                        
                                        st.success(f"✅ {len(all_data)} keywords obtenidas exitosamente")
                                        
                                        col_sum1, col_sum2, col_sum3 = st.columns(3)
                                        
                                        with col_sum1:
                                            st.metric("Keywords Únicas", all_data['keyword'].nunique())
                                        
                                        with col_sum2:
                                            st.metric("Volumen Total", f"{all_data['volume'].sum():,.0f}")
                                        
                                        with col_sum3:
                                            st.metric("Tráfico Total", f"{all_data['traffic'].sum():,.0f}")
                                        
                                        if 'source' in all_data.columns:
                                            with st.expander("📊 Distribución por Source"):
                                                source_summary = all_data.groupby(['source', 'source_type']).agg({
                                                    'keyword': 'count',
                                                    'volume': 'sum',
                                                    'traffic': 'sum'
                                                }).reset_index()
                                                source_summary.columns = ['Source', 'Tipo', 'Keywords', 'Volumen', 'Tráfico']
                                                st.dataframe(source_summary, use_container_width=True)
                                        
                                        with st.expander("👁️ Preview de los datos"):
                                            st.dataframe(
                                                safe_preview_dataframe(all_data, n=20),
                                                use_container_width=True
                                            )
                                    else:
                                        st.warning("⚠️ No se obtuvieron keywords. Verifica los targets.")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error al obtener datos de Semrush: {str(e)}")
                                    with st.expander("🔍 Ver detalles del error"):
                                        import traceback
                                        st.code(traceback.format_exc())
                    else:
                        st.warning("⚠️ Por favor ingresa al menos un target")
            else:
                st.warning("⚠️ Ingresa tu API key de Semrush en la barra lateral")
    
    # TAB 2: Análisis con IA
    with tab2:
        st.header("Análisis con IA")
        
        if ai_provider == "Claude (Anthropic)" and not anthropic_key:
            st.warning("⚠️ Por favor ingresa tu API key de Anthropic en la barra lateral")
            return
        elif ai_provider == "OpenAI" and not openai_key:
            st.warning("⚠️ Por favor ingresa tu API key de OpenAI en la barra lateral")
            return
        elif ai_provider == "Ambos (Validación Cruzada)" and (not anthropic_key or not openai_key):
            st.warning("⚠️ Para validación cruzada necesitas ambas API keys")
            return
        
        if not st.session_state.uploaded_files and st.session_state.processed_data is None:
            st.info("📁 Primero carga datos en la pestaña 'Carga de Datos'")
            return
        
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
            
            cache_manager = CacheManager()
            data_hash = cache_manager.get_data_hash(df)
            cached_analysis_id = cache_manager.find_cached_analysis(data_hash, analysis_type, num_tiers)
            
            force_new = True
            
            if cached_analysis_id:
                st.info(f"💾 Ya existe un análisis de **{analysis_type}** con {num_tiers} tiers para estos datos en caché")
                
                col_cache_opt1, col_cache_opt2 = st.columns(2)
                
                with col_cache_opt1:
                    if st.button("📂 Cargar desde Caché (Sin gastar créditos)", type="primary", use_container_width=True):
                        with st.spinner("Cargando análisis desde caché..."):
                            loaded = cache_manager.load_analysis(cached_analysis_id)
                            
                            if loaded:
                                st.session_state.keyword_universe = loaded['keyword_universe']
                                if 'processed_data' in loaded:
                                    st.session_state.processed_data = pd.DataFrame(loaded['processed_data'])
                                
                                st.success("✅ Análisis cargado desde caché")
                                st.balloons()
                                st.rerun()
                
                with col_cache_opt2:
                    st.caption("O ejecuta nuevo análisis:")
                    force_new = st.checkbox("Forzar nuevo análisis", value=False)
            
            st.divider()
            st.subheader("💰 Estimación de Costos")
            
            if ai_provider == "Claude (Anthropic)":
                cost_est = estimate_analysis_cost(model_choice, len(df))
                provider_name = "Claude"
                model_name = model_choice
            elif ai_provider == "OpenAI":
                cost_est = estimate_analysis_cost(model_choice, len(df))
                provider_name = "OpenAI"
                model_name = model_choice
            else:
                cost_est_claude = estimate_analysis_cost(claude_model, len(df))
                cost_est_openai = estimate_analysis_cost(openai_model, len(df))
                cost_est = {
                    'cost': cost_est_claude['cost'] + cost_est_openai['cost'],
                    'input_tokens': cost_est_claude['input_tokens'] + cost_est_openai['input_tokens'],
                    'output_tokens': cost_est_claude['output_tokens'] + cost_est_openai['output_tokens']
                }
                provider_name = "Ambos"
                model_name = f"{claude_model} + {openai_model}"
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Costo estimado", f"${cost_est['cost']:.4f}")
            with col2:
                st.metric("Tokens (input)", f"{cost_est['input_tokens']:,}")
            with col3:
                st.metric("Tokens (output)", f"{cost_est['output_tokens']:,}")
            
            if cache_enabled:
                cache_manager_check = get_cache_manager()
                test_hash = cache_manager_check.generate_hash(
                    df=df,
                    analysis_type=analysis_type,
                    num_tiers=num_tiers,
                    custom_instructions=custom_instructions,
                    include_semantic=include_semantic,
                    include_trends=include_trends,
                    include_gaps=include_gaps
                )
                
                cached_result = cache_manager_check.get_cached_analysis(test_hash, ttl_hours)
                
                if cached_result:
                    st.success(f"""
✅ **Análisis disponible en caché**

Este análisis ya fue realizado anteriormente y está disponible en caché.

- **Proveedor:** {cached_result.get('_cache_metadata', {}).get('provider', 'N/A')}
- **Antigüedad:** {cached_result.get('_cache_metadata', {}).get('age_hours', 0):.1f} horas
- **Ahorro:** ${cost_est['cost']:.4f}

Al hacer clic en "Analizar", se recuperará del caché sin consumir créditos.
                    """)
                else:
                    st.info(f"""
ℹ️ **Análisis nuevo**

Este análisis no está en caché y consumirá:
- **${cost_est['cost']:.4f}** en créditos de API
- **{cost_est['input_tokens'] + cost_est['output_tokens']:,}** tokens

Quedará guardado en caché para futuras consultas.
                    """)
            
            st.divider()
            
            if st.button("🚀 Analizar con IA", type="primary", use_container_width=True):
                with st.spinner(f"🧠 {ai_provider.split('(')[0].strip()} está analizando tu universo de keywords..."):
                    try:
                        analysis_params = {
                            'analysis_type': analysis_type,
                            'num_tiers': num_tiers,
                            'custom_instructions': custom_instructions,
                            'include_semantic': include_semantic,
                            'include_trends': include_trends,
                            'include_gaps': include_gaps
                        }
                        
                        if ai_provider == "Claude (Anthropic)":
                            anthropic_service = AnthropicService(anthropic_key, model_choice)
                            
                            prompt = anthropic_service.create_universe_prompt(df, **analysis_params)
                            
                            result = anthropic_service.analyze_keywords(
                                prompt,
                                df,
                                use_cache=cache_enabled,
                                **analysis_params
                            )
                            result['provider'] = 'Claude'
                            result['model'] = model_choice
                            
                        elif ai_provider == "OpenAI":
                            from app.services.openai_service import OpenAIService
                            
                            openai_service = OpenAIService(openai_key, model_choice)
                            
                            messages = openai_service.create_universe_prompt(df, **analysis_params)
                            
                            result = openai_service.analyze_keywords(
                                messages,
                                df,
                                use_cache=cache_enabled,
                                **analysis_params
                            )
                            result['provider'] = 'OpenAI'
                            result['model'] = model_choice
                            
                        else:
                            from app.services.openai_service import OpenAIService
                            
                            st.info("1️⃣ Analizando con Claude...")
                            anthropic_service = AnthropicService(anthropic_key, claude_model)
                            
                            prompt_claude = anthropic_service.create_universe_prompt(df, **analysis_params)
                            result_claude = anthropic_service.analyze_keywords(
                                prompt_claude,
                                df,
                                use_cache=cache_enabled,
                                **analysis_params
                            )
                            
                            st.info("2️⃣ Analizando con OpenAI...")
                            openai_service = OpenAIService(openai_key, openai_model)
                            
                            messages_openai = openai_service.create_universe_prompt(df, **analysis_params)
                            result_openai = openai_service.analyze_keywords(
                                messages_openai,
                                df,
                                use_cache=cache_enabled,
                                **analysis_params
                            )
                            
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
                        
                        # GUARDAR EN HISTORIAL DE ANÁLISIS
                        if result not in st.session_state.analyses_history:
                            st.session_state.analyses_history.append({
                                'timestamp': datetime.now(),
                                'analysis_type': analysis_type,
                                'provider': result.get('provider', 'N/A'),
                                'result': result
                            })
                        
                        # Mostrar si vino del caché
                        if result.get('_cache_metadata', {}).get('cached', False):
                            st.success("✅ ¡Análisis completado! (Recuperado del caché)")
                            st.info(f"💰 Has ahorrado ${cost_est['cost']:.4f} usando el caché")
                        else:
                            st.success("✅ ¡Análisis completado y guardado en caché!")
                        
                        st.balloons()
                        
                        # AUTO-GUARDAR EN BACKGROUND
                        try:
                            auto_name = f"{analysis_type} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            
                            metadata = {
                                'name': auto_name,
                                'description': f"Auto-guardado: {analysis_type} con {num_tiers} tiers",
                                'analysis_type': analysis_type,
                                'num_tiers': num_tiers,
                                'total_keywords': len(df),
                                'total_volume': int(df['volume'].sum()),
                                'custom_instructions': custom_instructions,
                                'data_hash': data_hash,
                                'cache_key': cache_manager._generate_cache_key(data_hash, analysis_type, num_tiers)
                            }
                            
                            analysis_id = cache_manager.save_analysis(
                                keyword_universe=result,
                                processed_data=df,
                                metadata=metadata,
                                auto_save=True
                            )
                            
                            st.success(f"💾 Análisis guardado automáticamente (ID: {analysis_id[:12]}...)")
                            
                        except Exception as e:
                            st.warning(f"⚠️ No se pudo auto-guardar: {str(e)}")
                        
                        # OPCIÓN DE GUARDADO MANUAL CON NOMBRE PERSONALIZADO
                        st.divider()
                        st.subheader("💾 Guardar con Nombre Personalizado")
                        
                        with st.form("save_analysis_form", clear_on_submit=False):
                            st.markdown("Opcionalmente, guarda este análisis con un nombre más descriptivo:")
                            
                            col_form1, col_form2 = st.columns([3, 1])
                            
                            with col_form1:
                                custom_name = st.text_input(
                                    "Nombre personalizado",
                                    value="",
                                    placeholder="Ej: Placas base AMD 2024",
                                    help="Deja vacío para usar el nombre automático"
                                )
                                
                                custom_description = st.text_area(
                                    "Descripción detallada",
                                    value="",
                                    placeholder="Ej: Análisis temático de placas base AMD para mercado español, enfoque en gaming",
                                    height=80
                                )
                            
                            with col_form2:
                                st.markdown("&nbsp;")
                                st.markdown("&nbsp;")
                                submitted = st.form_submit_button(
                                    "💾 Guardar Personalizado",
                                    type="secondary",
                                    use_container_width=True
                                )
                            
                            if submitted and (custom_name or custom_description):
                                try:
                                    final_name = custom_name if custom_name else auto_name
                                    final_description = custom_description if custom_description else metadata['description']
                                    
                                    custom_metadata = metadata.copy()
                                    custom_metadata['name'] = final_name
                                    custom_metadata['description'] = final_description
                                    
                                    custom_id = cache_manager.save_analysis(
                                        keyword_universe=result,
                                        processed_data=df,
                                        metadata=custom_metadata,
                                        auto_save=False
                                    )
                                    
                                    st.success(f"✅ Guardado personalizado: {final_name}")
                                    st.info("💡 Puedes encontrarlo en la barra lateral → 💾 Análisis Guardados")
                                    
                                except Exception as e:
                                    st.error(f"❌ Error al guardar: {str(e)}")
                        
                        st.caption("💡 **Nota:** Ya se guardó automáticamente. El guardado personalizado crea una copia adicional con tu nombre.")
                        
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
                            st.markdown("**Topics Adicionales Sugeridos por OpenAI:**")
                            for topic in comp['missing_topics']:
                                st.markdown(f"- {topic}")
                        
                        if 'improvements' in comp and comp['improvements']:
                            st.markdown("**Mejoras Sugeridas:**")
                            for improvement in comp['improvements']:
                                st.markdown(f"- {improvement}")
                
                if 'topics' in result:
                    st.subheader("🎯 Topics Identificados (Claude)" if result.get('provider') == 'Ambos' else "🎯 Topics Identificados")
                    
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
                
                if result.get('provider') == 'Ambos' and 'topics_openai' in result:
                    st.subheader("🎯 Topics Identificados (OpenAI)")
                    topics_openai_df = pd.DataFrame(result['topics_openai'])
                    st.dataframe(topics_openai_df, use_container_width=True, height=400)
    
    # TAB 3: Visualización
    with tab3:
        st.header("Visualización del Keyword Universe")
        
        if st.session_state.keyword_universe is None:
            st.info("🧠 Primero realiza el análisis con IA en la pestaña anterior")
            return
        
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
    
    # TAB 4: Arquitectura Web
    with tab4:
        st.header("🏗️ Propuesta de Arquitectura Web")
        
        if not st.session_state.keyword_universe:
            st.info("🧠 Primero realiza al menos un análisis en la pestaña 'Análisis con IA'")
            st.markdown("""
            ### ¿Qué es la Arquitectura Web?
            
            Esta funcionalidad genera una propuesta completa de estructura para tu sitio web basada en:
            - El análisis de keywords realizado
            - Patrones de búsqueda identificados
            - Intención del usuario
            - Volumen y prioridad estratégica
            """)
            return
        
        st.subheader("⚙️ Configuración")
        
        arch_provider = st.radio(
            "Proveedor de IA para arquitectura",
            ["Claude", "OpenAI", "Ambos"],
            horizontal=True,
            help="Claude es más estratégico. OpenAI es más rápido."
        )
        
        custom_arch_instructions = st.text_area(
            "Instrucciones adicionales (opcional)",
            placeholder="Ej: Enfócate en categorías de producto, prioriza marcas premium, estructura para e-commerce, etc.",
            height=100
        )
        
        if st.button("🏗️ Generar Arquitectura Web", type="primary", use_container_width=True):
            
            if arch_provider in ["Claude", "Ambos"] and not anthropic_key:
                st.error("⚠️ Necesitas la API key de Anthropic")
                return
            
            if arch_provider in ["OpenAI", "Ambos"] and not openai_key:
                st.error("⚠️ Necesitas la API key de OpenAI")
                return
            
            with st.spinner(f"🏗️ Generando arquitectura web..."):
                try:
                    arch_service = ArchitectureService(
                        anthropic_key=anthropic_key if arch_provider in ["Claude", "Ambos"] else None,
                        openai_key=openai_key if arch_provider in ["OpenAI", "Ambos"] else None,
                        claude_model=claude_model,
                        openai_model=openai_model
                    )
                    
                    architecture = arch_service.generate_architecture(
                        analysis_results=st.session_state.keyword_universe,
                        df=st.session_state.processed_data,
                        provider=arch_provider,
                        custom_instructions=custom_arch_instructions
                    )
                    
                    st.session_state.architecture = architecture
                    
                    st.success("✅ ¡Arquitectura generada exitosamente!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error generando arquitectura: {str(e)}")
                    import traceback
                    with st.expander("Ver detalles del error"):
                        st.code(traceback.format_exc())
        
        if st.session_state.architecture:
            st.divider()
            st.subheader("📋 Arquitectura Propuesta")
            
            arch = st.session_state.architecture
            
            provider_col1, provider_col2 = st.columns(2)
            with provider_col1:
                st.metric("Proveedor", arch.get('provider', 'N/A'))
            with provider_col2:
                if arch.get('provider') == 'Ambos':
                    st.metric("Modelos", arch.get('models', 'N/A'))
                else:
                    st.metric("Modelo", arch.get('model', 'N/A'))
            
            with st.expander("📊 Resumen Ejecutivo", expanded=True):
                st.markdown(arch.get('overview', 'No disponible'))
            
            if 'site_structure' in arch and 'main_sections' in arch['site_structure']:
                st.subheader("🗂️ Estructura del Sitio")
                
                sections = arch['site_structure']['main_sections']
                
                for section in sections:
                    with st.expander(f"📁 {section.get('section_name', 'N/A')} - {section.get('priority', 'N/A').upper()}"):
                        st.markdown(f"**URL:** `{section.get('url_structure', 'N/A')}`")
                        st.markdown(f"**Tipo:** {section.get('page_type', 'N/A')}")
                        st.markdown(f"**Descripción:** {section.get('description', 'N/A')}")
                        
                        if 'target_topics' in section:
                            st.markdown("**Topics objetivo:**")
                            for topic in section['target_topics']:
                                st.markdown(f"- {topic}")
                        
                        if 'subsections' in section and section['subsections']:
                            st.markdown("**Subsecciones:**")
                            for subsection in section['subsections']:
                                st.markdown(f"- `{subsection.get('url', 'N/A')}` - {subsection.get('name', 'N/A')}")
            
            if 'content_strategy' in arch:
                st.divider()
                st.subheader("📝 Estrategia de Contenido")
                
                content_strat = arch['content_strategy']
                
                if 'pillar_pages' in content_strat:
                    st.markdown("**Páginas Pillar:**")
                    for pillar in content_strat['pillar_pages']:
                        with st.expander(f"🏛️ {pillar.get('title', 'N/A')}"):
                            st.markdown(f"**URL:** `{pillar.get('url', 'N/A')}`")
                            st.markdown(f"**Palabras estimadas:** {pillar.get('estimated_word_count', 0):,}")
                            st.markdown(f"**Artículos de soporte:** {pillar.get('supporting_articles', 0)}")
                            st.markdown(f"**Prioridad:** {pillar.get('priority', 'N/A')}")
            
            if 'implementation_roadmap' in arch:
                st.divider()
                st.subheader("📅 Roadmap de Implementación")
                
                for phase in arch['implementation_roadmap']:
                    with st.expander(f"**Fase {phase.get('phase', 0)}** - {phase.get('duration', 'N/A')}"):
                        st.markdown(f"**Foco:** {phase.get('focus', 'N/A')}")
                        st.markdown(f"**Páginas a crear:** {phase.get('pages_to_create', 0)}")
                        st.markdown(f"**Esfuerzo estimado:** {phase.get('estimated_effort', 'N/A')}")
    
    # TAB 5: Oportunidades
    with tab5:
        st.header("🎯 Oportunidades Identificadas")
        
        if st.session_state.keyword_universe is None:
            st.info("🧠 Primero realiza el análisis con IA en la pestaña 'Análisis con IA'")
        else:
            result = st.session_state.keyword_universe
            
            st.subheader("📊 Resumen de Oportunidades")
            
            total_opportunities = 0
            gaps_count = len(result.get('gaps', []))
            trends_count = len(result.get('trends', []))
            tier1_count = len([t for t in result.get('topics', []) if t.get('tier') == 1])
            
            if 'topics_openai' in result:
                tier1_openai = len([t for t in result.get('topics_openai', []) if t.get('tier') == 1])
                tier1_count = max(tier1_count, tier1_openai)
            
            total_opportunities = gaps_count + trends_count + tier1_count
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Oportunidades", total_opportunities)
            
            with col2:
                st.metric("Gaps de Contenido", gaps_count)
            
            with col3:
                st.metric("Tendencias Emergentes", trends_count)
            
            with col4:
                st.metric("Topics Prioritarios", tier1_count)
            
            st.divider()
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                opportunity_filter = st.multiselect(
                    "Filtrar por tipo de oportunidad",
                    ["Gaps de Contenido", "Tendencias", "Topics Tier 1"],
                    default=["Gaps de Contenido", "Tendencias", "Topics Tier 1"]
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Ordenar por",
                    ["Volumen (mayor)", "Volumen (menor)", "Nombre"]
                )
            
            all_opportunities = []
            
            if "Gaps de Contenido" in opportunity_filter and gaps_count > 0:
                for gap in result['gaps']:
                    all_opportunities.append({
                        'tipo': 'Gap de Contenido',
                        'nombre': gap.get('topic', 'N/A'),
                        'volumen': gap.get('volume', 0),
                        'keywords': gap.get('keyword_count', 0),
                        'prioridad': 'Alta',
                        'dificultad': gap.get('difficulty', 'medium'),
                        'descripcion': gap.get('description', ''),
                        'tier_badge': 'badge-tier-1',
                        'icon': '🎯'
                    })
            
            if "Tendencias" in opportunity_filter and trends_count > 0:
                for trend in result['trends']:
                    all_opportunities.append({
                        'tipo': 'Tendencia Emergente',
                        'nombre': trend.get('trend', 'N/A'),
                        'volumen': trend.get('total_volume', 0),
                        'keywords': len(trend.get('keywords', [])),
                        'prioridad': 'Media',
                        'dificultad': 'variable',
                        'descripcion': trend.get('insight', ''),
                        'tier_badge': 'badge-tier-2',
                        'icon': '📈'
                    })
            
            if "Topics Tier 1" in opportunity_filter and tier1_count > 0:
                tier1_topics = [t for t in result.get('topics', []) if t.get('tier') == 1]
                
                for topic in tier1_topics:
                    all_opportunities.append({
                        'tipo': 'Topic Prioritario',
                        'nombre': topic.get('topic', 'N/A'),
                        'volumen': topic.get('volume', 0),
                        'keywords': topic.get('keyword_count', 0),
                        'prioridad': topic.get('priority', 'high'),
                        'dificultad': 'variable',
                        'descripcion': topic.get('description', ''),
                        'tier_badge': 'badge-tier-1',
                        'icon': '⭐'
                    })
            
            if sort_by == "Volumen (mayor)":
                all_opportunities.sort(key=lambda x: x['volumen'], reverse=True)
            elif sort_by == "Volumen (menor)":
                all_opportunities.sort(key=lambda x: x['volumen'])
            else:
                all_opportunities.sort(key=lambda x: x['nombre'])
            
            if not all_opportunities:
                st.warning("No hay oportunidades que coincidan con los filtros seleccionados")
            else:
                st.subheader(f"📋 {len(all_opportunities)} Oportunidades Encontradas")
                
                for i, opp in enumerate(all_opportunities):
                    with st.expander(
                        f"{opp['icon']} {opp['nombre']} - {format_number(opp['volumen'])} búsquedas/mes",
                        expanded=(i < 5)
                    ):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**Tipo:** {opp['tipo']}")
                        
                        with col2:
                            st.markdown(
                                f"<span class='{opp['tier_badge']}'>{opp['prioridad'].upper()}</span>",
                                unsafe_allow_html=True
                            )
                        
                        with col3:
                            st.markdown(f"**Dificultad:** {opp['dificultad'].title()}")
                        
                        st.divider()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Volumen Total", f"{opp['volumen']:,}")
                        
                        with col2:
                            st.metric("Keywords Relacionadas", opp['keywords'])
                        
                        st.markdown("**Descripción:**")
                        st.write(opp['descripcion'])
                        
                        st.markdown("**Acción Recomendada:**")
                        if opp['tipo'] == 'Gap de Contenido':
                            st.info("💡 Crear contenido completo que cubra este tema. Poca competencia actual.")
                        elif opp['tipo'] == 'Tendencia Emergente':
                            st.info("💡 Actuar rápido para posicionarse antes que la competencia.")
                        else:
                            st.info("💡 Priorizar en la estrategia de contenido. Alto ROI potencial.")
            
            if all_opportunities:
                st.divider()
                st.subheader("📊 Matriz de Priorización")
                
                priority_data = []
                for opp in all_opportunities:
                    priority_data.append({
                        'Oportunidad': opp['nombre'],
                        'Tipo': opp['tipo'],
                        'Volumen': opp['volumen'],
                        'Keywords': opp['keywords'],
                        'Prioridad': opp['prioridad'],
                        'Dificultad': opp['dificultad']
                    })
                
                priority_df = pd.DataFrame(priority_data)
                
                st.dataframe(
                    priority_df,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Volumen": st.column_config.NumberColumn("Volumen", format="%d"),
                        "Keywords": st.column_config.NumberColumn("Keywords", format="%d"),
                    }
                )
                
                st.divider()
                col1, col2 = st.columns([3, 1])
                
                with col2:
                    csv_opps = priority_df.to_csv(index=False)
                    st.download_button(
                        "📥 Exportar Oportunidades",
                        data=csv_opps,
                        file_name=f"oportunidades_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        type="primary"
                    )
    
    # TAB 6: Exportar
    with tab6:
        st.header("Exportar Resultados")
        
        if st.session_state.keyword_universe is None:
            st.info("🧠 Primero realiza el análisis con IA")
            return
        
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
        
        if st.session_state.architecture:
            st.divider()
            st.subheader("🏗️ Exportar Arquitectura Web")
            
            arch_format = st.radio(
                "Formato de arquitectura",
                ["JSON", "Excel", "Mapa del Sitio (TXT)"],
                horizontal=True
            )
            
            if st.button("💾 Exportar Arquitectura", key="export_arch"):
                try:
                    if arch_format == "JSON":
                        import json
                        json_data = json.dumps(st.session_state.architecture, indent=2, ensure_ascii=False)
                        st.download_button(
                            "⬇️ Descargar Arquitectura JSON",
                            data=json_data,
                            file_name=f"web_architecture_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json"
                        )
                    elif arch_format == "Excel":
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            summary_df = pd.DataFrame({
                                'Sección': ['Resumen'],
                                'Contenido': [st.session_state.architecture.get('overview', 'N/A')]
                            })
                            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                            
                            if 'site_structure' in st.session_state.architecture:
                                if 'main_sections' in st.session_state.architecture['site_structure']:
                                    sections_data = []
                                    for sec in st.session_state.architecture['site_structure']['main_sections']:
                                        sections_data.append({
                                            'Sección': sec.get('section_name', ''),
                                            'URL': sec.get('url_structure', ''),
                                            'Tipo': sec.get('page_type', ''),
                                            'Prioridad': sec.get('priority', '')
                                        })
                                    
                                    if sections_data:
                                        sections_df = pd.DataFrame(sections_data)
                                        sections_df.to_excel(writer, sheet_name='Estructura', index=False)
                        
                        output.seek(0)
                        st.download_button(
                            "⬇️ Descargar Arquitectura Excel",
                            data=output.getvalue(),
                            file_name=f"web_architecture_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        arch_service = ArchitectureService()
                        sitemap = arch_service.export_to_document(st.session_state.architecture)
                        st.download_button(
                            "⬇️ Descargar Mapa del Sitio",
                            data=sitemap,
                            file_name=f"sitemap_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
                    
                    st.success("✅ Arquitectura exportada")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
