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

# CSS personalizado con branding PC Componentes - OPTIMIZADO PARA USABILIDAD
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
    
    /* ============================================
       SIDEBAR - OPTIMIZADO PARA USABILIDAD
       ============================================ */
    
    /* Sidebar principal */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #170453 0%, #090029 100%);
    }
    
    /* Texto general - Color claro pero no blanco puro */
    [data-testid="stSidebar"] * {
        color: #E8E6F0 !important;
    }
    
    /* Labels con mejor contraste */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stRadio label {
        color: #FFB380 !important;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Expanders con mejor visibilidad */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: rgba(255, 96, 0, 0.25) !important;
        border-radius: 8px;
        color: #FFFFFF !important;
        font-weight: 600;
        border: 1.5px solid rgba(255, 134, 64, 0.5);
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: rgba(255, 96, 0, 0.35) !important;
        border-color: rgba(255, 134, 64, 0.7);
    }
    
    /* Contenido del expander - SIN fondo blanco */
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: transparent !important;
        border: none !important;
        padding-top: 1rem;
    }
    
    [data-testid="stSidebar"] details {
        background-color: transparent !important;
        margin-bottom: 1rem;
    }
    
    /* Inputs - ELIMINADO fondo blanco, ahora azul oscuro sólido */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background-color: rgba(23, 4, 83, 0.6) !important;
        border: 2px solid rgba(255, 134, 64, 0.4) !important;
        color: #F5F5F5 !important;
        border-radius: 6px;
        padding: 0.6rem;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] input:hover,
    [data-testid="stSidebar"] textarea:hover {
        border-color: rgba(255, 134, 64, 0.6) !important;
        background-color: rgba(23, 4, 83, 0.8) !important;
    }
    
    /* Placeholders más legibles */
    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {
        color: rgba(255, 179, 128, 0.6) !important;
        font-style: italic;
    }
    
    /* Focus con mejor visibilidad */
    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus {
        border-color: #FF8640 !important;
        box-shadow: 0 0 0 3px rgba(255, 134, 64, 0.25) !important;
        background-color: rgba(23, 4, 83, 0.9) !important;
        outline: none;
    }
    
    /* Selectboxes - ELIMINADO fondo blanco completamente */
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background-color: rgba(23, 4, 83, 0.6) !important;
        border: 2px solid rgba(255, 134, 64, 0.4) !important;
        color: #F5F5F5 !important;
        border-radius: 6px;
    }
    
    /* Todos los elementos internos del selectbox sin blanco */
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
    [data-testid="stSidebar"] .stSelectbox input {
        background-color: rgba(23, 4, 83, 0.6) !important;
        border: 2px solid rgba(255, 134, 64, 0.4) !important;
        color: #F5F5F5 !important;
    }
    
    /* Texto dentro del selectbox */
    [data-testid="stSidebar"] .stSelectbox span,
    [data-testid="stSidebar"] .stSelectbox div {
        color: #F5F5F5 !important;
        background-color: transparent !important;
    }
    
    /* Hover state */
    [data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: rgba(255, 134, 64, 0.6) !important;
        background-color: rgba(23, 4, 83, 0.8) !important;
    }
    
    /* El contenedor principal del select */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: rgba(23, 4, 83, 0.6) !important;
    }
    
    /* Dropdown menus con mejor contraste */
    [data-testid="stSidebar"] [data-baseweb="popover"] {
        background-color: #1F0A5C !important;
        border: 1.5px solid rgba(255, 134, 64, 0.4);
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    [data-testid="stSidebar"] [role="option"] {
        background-color: transparent !important;
        color: #E8E6F0 !important;
        padding: 0.6rem 1rem;
        transition: all 0.15s ease;
    }
    
    /* Hover en opciones - SIN blanco, usando naranja */
    [data-testid="stSidebar"] [role="option"]:hover {
        background-color: rgba(255, 96, 0, 0.3) !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] [aria-selected="true"] {
        background-color: rgba(255, 96, 0, 0.4) !important;
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    /* Radio buttons */
    [data-testid="stSidebar"] .stRadio > div {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: #E8E6F0 !important;
    }
    
    [data-testid="stSidebar"] input[type="radio"]:checked + div {
        background-color: #FF6000 !important;
        border-color: #FF6000 !important;
    }
    
    /* Sliders */
    [data-testid="stSidebar"] .stSlider {
        padding: 1rem 0;
    }
    
    [data-testid="stSidebar"] .stSlider [role="slider"] {
        background-color: #FF6000 !important;
    }
    
    /* Number Input */
    [data-testid="stSidebar"] .stNumberInput input {
        background-color: rgba(23, 4, 83, 0.6) !important;
        border: 2px solid rgba(255, 134, 64, 0.4) !important;
        color: #F5F5F5 !important;
    }
    
    [data-testid="stSidebar"] .stNumberInput button {
        background-color: rgba(255, 96, 0, 0.2) !important;
        color: #FFB380 !important;
        border: 1px solid rgba(255, 134, 64, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stNumberInput button:hover {
        background-color: rgba(255, 96, 0, 0.4) !important;
        color: #FFFFFF !important;
    }
    
    /* Info boxes con mejor visibilidad */
    [data-testid="stSidebar"] .stAlert {
        background-color: rgba(255, 96, 0, 0.2) !important;
        border-left: 4px solid #FF8640 !important;
        border-radius: 8px;
        color: #F5F5F5 !important;
        padding: 1rem;
    }
    
    [data-testid="stSidebar"] .stAlert * {
        color: #F5F5F5 !important;
    }
    
    [data-testid="stSidebar"] .stAlert svg {
        fill: #FFB380 !important;
    }
    
    /* Dividers */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 134, 64, 0.3) !important;
        margin: 1.5rem 0;
        border-width: 1px;
    }
    
    /* Headers en sidebar */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Accesibilidad - Focus visible */
    [data-testid="stSidebar"] *:focus-visible {
        outline: 2px solid #FF8640 !important;
        outline-offset: 2px;
    }
    
    /* ============================================
       FIN SIDEBAR - ÁREA PRINCIPAL
       ============================================ */
    
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
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left-width: 4px;
    }
    
    /* Success */
    [data-baseweb="notification"][kind="success"] {
        background-color: #E8F5E9;
        border-left-color: #4CAF50;
    }
    
    /* Info */
    [data-baseweb="notification"][kind="info"] {
        background-color: #FFD7BF;
        border-left-color: #FF6000;
    }
    
    /* Warning */
    [data-baseweb="notification"][kind="warning"] {
        background-color: #FFF3E0;
        border-left-color: #FF6000;
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Headers de secciones */
    h1, h2, h3 {
        color: #090029;
        font-weight: 700;
    }
    
    h2 {
        border-bottom: 3px solid #FF6000;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    /* Dividers */
    hr {
        border-color: #FF8640;
        margin: 2rem 0;
    }
    
    /* Select boxes y inputs del área principal */
    .stSelectbox > div > div {
        border-color: #CCCCCC;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #FF6000;
        box-shadow: 0 0 0 2px rgba(255, 96, 0, 0.1);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #FF8640;
        border-radius: 10px;
        padding: 2rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F5 100%);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #FF6000;
        background: #FFF9F5;
    }
    
    /* Spinner personalizado */
    .stSpinner > div {
        border-top-color: #FF6000 !important;
    }
    
    /* Badges/Pills */
    .badge-tier-1 {
        background: linear-gradient(135deg, #FF6000 0%, #FF8640 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-tier-2 {
        background: linear-gradient(135deg, #170453 0%, #51437E 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-tier-3 {
        background: linear-gradient(135deg, #8B81A9 0%, #C5C0D4 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Links */
    a {
        color: #FF6000 !important;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #FF8640 !important;
        text-decoration: underline;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 2px solid #F5F5F5;
        color: #999999;
        font-size: 0.9rem;
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
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
    """
    Muestra el logo con sistema de fallback en cascada
    Prioridad: URL > Base64 > Archivo local > Placeholder
    """
    # Prioridad 1: Logo desde URL externa
    if LOGO_URL:
        try:
            st.image(LOGO_URL, width=120)
            return True
        except Exception as e:
            # Silencioso - continuar al siguiente método
            pass
    
    # Prioridad 2: Logo en Base64 embebido
    if LOGO_BASE64:
        try:
            st.markdown(
                f'<img src="{LOGO_BASE64}" width="120" style="border-radius: 8px;">',
                unsafe_allow_html=True
            )
            return True
        except Exception as e:
            # Silencioso - continuar al siguiente método
            pass
    
    # Prioridad 3: Logo local en assets/
    if os.path.exists("assets/pc_logo.png"):
        try:
            st.image("assets/pc_logo.png", width=120)
            return True
        except Exception as e:
            # Silencioso - continuar al fallback
            pass
    
    # Prioridad 4: Fallback - Placeholder con iniciales PC
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
            
            # Selección de modelo según proveedor
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
        
        st.divider()
        
        # Info
        st.info("💡 **Tip:** Sube archivos CSV o Excel de Ahrefs, Semrush o similar con columnas: keyword, volume, traffic")
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 Carga de Datos", 
        "🧠 Análisis con IA", 
        "📊 Visualización",
        "📥 Exportar"
    ])
    
    # TAB 1: Carga de datos
    with tab1:
        st.header("Carga tus archivos de keywords")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Opción 1: Cargar archivos
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
                
                # Preview de los datos
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
            # Opción 2: Integración directa con Semrush
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
        
        # Validar API keys según proveedor
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
        
        # Preparar datos
        if st.session_state.processed_data is None and st.session_state.uploaded_files:
            processor = DataProcessor()
            st.session_state.processed_data = processor.process_files(
                st.session_state.uploaded_files, 
                max_keywords
            )
        
        if st.session_state.processed_data is not None:
            df = st.session_state.processed_data
            
            # Métricas rápidas
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
            
            # Configuración del prompt
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
            
            # Botón de análisis
            if st.button("🚀 Analizar con IA", type="primary", use_container_width=True):
                with st.spinner(f"🧠 {ai_provider.split('(')[0].strip()} está analizando tu universo de keywords..."):
                    try:
                        if ai_provider == "Claude (Anthropic)":
                            # Análisis con Claude
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
                            # Análisis con OpenAI
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
                            
                        else:  # Ambos (Validación Cruzada)
                            from app.services.openai_service import OpenAIService
                            
                            # Análisis con Claude
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
                            
                            # Análisis con OpenAI
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
                            
                            # Validación cruzada
                            st.info("3️⃣ Comparando resultados...")
                            comparison = openai_service.compare_with_claude(result_claude, df)
                            
                            # Combinar resultados
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
            
            # Mostrar resultados si existen
            if st.session_state.keyword_universe:
                st.divider()
                st.subheader("📋 Resultados del Análisis")
                
                result = st.session_state.keyword_universe
                
                # Mostrar info del proveedor
                provider_col1, provider_col2 = st.columns(2)
                with provider_col1:
                    st.metric("Proveedor de IA", result.get('provider', 'N/A'))
                with provider_col2:
                    if result.get('provider') == 'Ambos':
                        st.metric("Modelos", result.get('models', 'N/A'))
                    else:
                        st.metric("Modelo", result.get('model', 'N/A'))
                
                # Resumen ejecutivo
                with st.expander("📊 Resumen Ejecutivo", expanded=True):
                    st.markdown(result.get('summary', 'No disponible'))
                
                # Si es validación cruzada, mostrar comparación
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
                
                # Topics por tier
                if 'topics' in result:
                    st.subheader("🎯 Topics Identificados (Claude)" if result.get('provider') == 'Ambos' else "🎯 Topics Identificados")
                    
                    topics_df = pd.DataFrame(result['topics'])
                    
                    # Filtros
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
                
                # Si hay análisis de OpenAI también, mostrarlo
                if result.get('provider') == 'Ambos' and 'topics_openai' in result:
                    st.subheader("🎯 Topics Identificados (OpenAI)")
                    topics_openai_df = pd.DataFrame(result['topics_openai'])
                    st.dataframe(topics_openai_df, use_container_width=True, height=400)
    
    # TAB 3: Visualización
    with tab3:
        st.header("Visualización del Keyword Universe")
        
        if st.session_state.keyword_universe is None:
            st.info("🧠 Primero realiza el análisis con Claude en la pestaña anterior")
            return
        
        result = st.session_state.keyword_universe
        
        if 'topics' in result:
            visualizer = KeywordVisualizer()
            topics_df = pd.DataFrame(result['topics'])
            
            # Gráfico de burbujas
            st.subheader("🫧 Mapa de Topics (Bubble Chart)")
            
            fig_bubble = visualizer.create_bubble_chart(topics_df)
            st.plotly_chart(fig_bubble, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Treemap
                st.subheader("🗺️ Treemap por Volumen")
                fig_treemap = visualizer.create_treemap(topics_df)
                st.plotly_chart(fig_treemap, use_container_width=True)
            
            with col2:
                # Sunburst
                st.subheader("☀️ Distribución por Tier")
                fig_sunburst = visualizer.create_sunburst(topics_df)
                st.plotly_chart(fig_sunburst, use_container_width=True)
            
            # Análisis de gaps
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
            st.info("🧠 Primero realiza el análisis con Claude")
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
                        else:  # JSON
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

if __name__ == "__main__":
    main()
