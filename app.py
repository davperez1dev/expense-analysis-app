"""
Aplicación Principal de Análisis de Gastos Personales
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from utils import ConfigLoader, CategoryClassifier, DataLoader, CurrencyFormatter
from utils.page_transitions import add_page_transition, add_custom_css

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Gastos Personales",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar transiciones y estilos mejorados
add_page_transition()
add_custom_css()

# CSS personalizado - Adaptado para tema oscuro
st.markdown("""
    <style>
    /* Configuración general */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Métricas con contraste mejorado */
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(250, 250, 250, 0.2);
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .stMetric label {
        color: #fafafa !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        opacity: 0.9;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }
    
    /* Títulos con mejor visibilidad */
    h1 {
        color: #fafafa !important;
        font-weight: 700 !important;
        padding-bottom: 0.5rem;
    }
    h2 {
        color: #e6e6e6 !important;
        font-weight: 600 !important;
        padding-top: 1rem;
    }
    h3 {
        color: #d9d9d9 !important;
        font-weight: 600 !important;
    }
    
    /* Texto general legible */
    .stMarkdown, p, span, div {
        color: #d9d9d9 !important;
    }
    
    /* Tablas con mejor contraste */
    .stDataFrame {
        border: 1px solid rgba(250, 250, 250, 0.2);
    }
    
    /* Expanders mejorados */
    .streamlit-expanderHeader {
        background-color: rgba(88, 166, 255, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(88, 166, 255, 0.3);
        color: #fafafa !important;
        font-weight: 600 !important;
    }
    
    /* Alerts y mensajes */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        border-left: 4px solid #58a6ff;
    }
    
    /* Separadores */
    hr {
        border-color: rgba(250, 250, 250, 0.2);
    }
    
    /* Captions más legibles */
    .caption, small {
        color: #a9a9a9 !important;
    }
    
    /* Mejora de selectbox y multiselect */
    .stSelectbox label, .stMultiSelect label {
        color: #fafafa !important;
        font-weight: 600 !important;
    }
    
    /* Mejorar contraste de selectbox/multiselect desplegados */
    [data-baseweb="select"] {
        background-color: #1e1e1e !important;
    }
    
    [data-baseweb="popover"] {
        background-color: #2d2d2d !important;
        border: 1px solid #4a4a4a !important;
    }
    
    /* Opciones del dropdown */
    [data-baseweb="menu"] {
        background-color: #2d2d2d !important;
        border: 1px solid #4a4a4a !important;
    }
    
    [role="option"] {
        background-color: #2d2d2d !important;
        color: #fafafa !important;
        padding: 8px 12px !important;
    }
    
    [role="option"]:hover {
        background-color: #3d3d3d !important;
        color: #58a6ff !important;
    }
    
    [role="option"][aria-selected="true"] {
        background-color: rgba(88, 166, 255, 0.2) !important;
        color: #58a6ff !important;
        font-weight: 600 !important;
    }
    
    /* Checkboxes en multiselect */
    [data-baseweb="checkbox"] {
        border-color: #58a6ff !important;
    }
    
    /* Tags seleccionados en multiselect */
    [data-baseweb="tag"] {
        background-color: rgba(88, 166, 255, 0.3) !important;
        color: #fafafa !important;
        border: 1px solid #58a6ff !important;
    }
    
    /* Input text en selectbox/multiselect */
    [data-baseweb="input"] input {
        background-color: #2d2d2d !important;
        color: #fafafa !important;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def inicializar_configuracion(_config_mtime: float = None):
    """Inicializa la configuración y componentes
    
    Args:
        _config_mtime: Tiempo de modificación del config (para invalidar caché cuando cambie)
    """
    config_loader = ConfigLoader()
    classifier = CategoryClassifier(config_loader)
    data_loader = DataLoader()
    formatter = CurrencyFormatter(config_loader)
    
    return config_loader, classifier, data_loader, formatter


@st.cache_data
def cargar_y_procesar_datos(_data_loader, _classifier, file_path: str = None, _file_mtime: float = None):
    """Carga y procesa los datos del CSV
    
    Args:
        _file_mtime: Tiempo de modificación del archivo (para invalidar caché cuando cambie)
    """
    if file_path is None:
        file_path = "data/categories_timeline.csv"
    
    # Procesar datos
    df = _data_loader.procesar_completo(file_path)
    
    # Clasificar categorías
    df = _classifier.clasificar_dataframe(df)
    
    # Excluir filas resumen del análisis detallado
    df_analisis = df[df['Grupo'] != 'Resumen'].copy()
    
    # Excluir categorías principales que tienen subcategorías
    # (son filas de totales que causan doble contabilización)
    categorias_con_subcat = _classifier.obtener_categorias_con_subcategorias()
    df_analisis = df_analisis[~df_analisis['Categorías'].isin(categorias_con_subcat)].copy()
    
    return df, df_analisis


def main():
    """Función principal de la aplicación"""
    
    # Obtener tiempo de modificación del config para invalidar caché
    config_path = Path("config/categories_config.yaml")
    config_mtime = os.path.getmtime(config_path) if config_path.exists() else 0
    
    # Inicializar componentes
    config_loader, classifier, data_loader, formatter = inicializar_configuracion(config_mtime)
    
    # Título principal
    st.title("💰 Análisis de Gastos Personales")
    st.markdown("### Dashboard interactivo para análisis financiero")
    
    # Verificar si hay archivo subido
    file_path = None
    if 'uploaded_file' in st.session_state and st.session_state['uploaded_file'] is not None:
        uploaded_file = st.session_state['uploaded_file']
        # Guardar temporalmente
        temp_path = Path("data/temp_upload.csv")
        temp_path.parent.mkdir(exist_ok=True)
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        file_path = str(temp_path)
    else:
        # Usar archivo por defecto
        default_path = Path("data/categories_timeline.csv")
        if not default_path.exists():
            st.error(f"""
                ⚠️ **Archivo de datos no encontrado**
                
                Por favor, copia tu archivo CSV a: `{default_path}`
                
                O sube un archivo usando el botón en la barra lateral.
            """)
            st.stop()
        file_path = str(default_path)
    
    # Obtener tiempo de modificación del archivo para invalidar caché
    file_mtime = os.path.getmtime(file_path)
    
    # Cargar datos
    try:
        with st.spinner("Cargando datos..."):
            df_completo, df_analisis = cargar_y_procesar_datos(
                data_loader, classifier, file_path, file_mtime
            )
        
        st.success(f"✅ Datos cargados: {len(df_analisis):,} registros procesados")
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        st.stop()
    
    # Mostrar información general
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_registros = len(df_analisis)
        st.metric("📊 Total Registros", f"{total_registros:,}")
    
    with col2:
        categorias = df_analisis['Categoria_Principal'].nunique()
        st.metric("🏷️ Categorías", f"{categorias}")
    
    with col3:
        if 'Fecha' in df_analisis.columns:
            periodos = df_analisis['Fecha'].nunique()
            st.metric("📅 Períodos", f"{periodos}")
    
    with col4:
        grupos = df_analisis['Grupo'].nunique()
        st.metric("🔖 Grupos", f"{grupos}")
    
    st.markdown("---")
    
    # Resumen rápido
    with st.expander("📈 Resumen Financiero Rápido", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        total_ingresos = df_analisis[df_analisis['Monto'] > 0]['Monto'].sum()
        total_gastos = df_analisis[df_analisis['Monto'] < 0]['Monto'].sum()
        ganancia_neta = total_ingresos + total_gastos
        tasa_ahorro = (ganancia_neta / total_ingresos * 100) if total_ingresos > 0 else 0
        
        with col1:
            st.metric(
                "💵 Total Ingresos",
                formatter.formatear(total_ingresos, incluir_signo=False),
                delta=None
            )
        
        with col2:
            st.metric(
                "💸 Total Gastos",
                formatter.formatear(abs(total_gastos), incluir_signo=False),
                delta=None
            )
        
        with col3:
            st.metric(
                "💰 Ganancia Neta",
                formatter.formatear(ganancia_neta, incluir_signo=False),
                delta=f"{tasa_ahorro:.1f}% ahorro"
            )
        
        with col4:
            promedio_mensual = total_gastos / df_analisis['Fecha'].nunique() if 'Fecha' in df_analisis.columns else 0
            st.metric(
                "📊 Promedio Mensual",
                formatter.formatear(abs(promedio_mensual), incluir_signo=False),
                delta=None
            )
    
    st.markdown("---")
    
    # Información de navegación
    st.markdown("""
        <div style='background-color: rgba(88, 166, 255, 0.1); 
                    padding: 1.5rem; 
                    border-radius: 10px; 
                    border-left: 4px solid #58a6ff;
                    margin: 1rem 0;'>
            <h3 style='color: #58a6ff; margin-top: 0;'>� Cómo usar esta aplicación</h3>
            <p style='color: #d9d9d9;'><strong>�👈 Usa la barra lateral para:</strong></p>
            <ul style='color: #d9d9d9;'>
                <li>Filtrar datos por fecha, grupo y categoría</li>
                <li>Ajustar rangos de montos</li>
                <li>Subir tu propio archivo CSV</li>
            </ul>
            <p style='color: #d9d9d9;'><strong>📄 Navega entre páginas:</strong></p>
            <ul style='color: #d9d9d9;'>
                <li><strong>📊 Explorador</strong>: Visualiza y filtra datos en formato tabla con pivotes</li>
                <li><strong>📈 Dashboard</strong>: Analiza gráficos interactivos, tendencias y comparativas</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.caption(f"💡 Versión de configuración: {config_loader.get_version()} | Desarrollado con Streamlit")


if __name__ == "__main__":
    main()
