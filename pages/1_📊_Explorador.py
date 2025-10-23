"""
Página 1: Explorador de Datos con Filtros
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ConfigLoader, CategoryClassifier, DataLoader, CurrencyFormatter, TableFormatter
from components.sidebar import FilterSidebar

st.set_page_config(
    page_title="Explorador de Datos",
    page_icon="📊",
    layout="wide"
)

# CSS personalizado - Adaptado para tema oscuro
st.markdown("""
    <style>
    /* Métricas con contraste mejorado */
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(250, 250, 250, 0.2);
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .stMetric label {
        color: #fafafa !important;
        font-weight: 600 !important;
        opacity: 0.9;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-weight: 700 !important;
    }
    
    /* Títulos con mejor visibilidad */
    h1 {
        color: #fafafa !important;
        font-weight: 700 !important;
    }
    h2 {
        color: #e6e6e6 !important;
        font-weight: 600 !important;
    }
    h3 {
        color: #d9d9d9 !important;
        font-weight: 600 !important;
    }
    
    /* Tablas con mejor contraste */
    .stDataFrame {
        border: 1px solid rgba(250, 250, 250, 0.2);
        border-radius: 8px;
    }
    
    /* Tabs más visibles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 8px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        color: #d9d9d9 !important;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(88, 166, 255, 0.3);
        color: #58a6ff !important;
        font-weight: 600;
    }
    
    /* Botones de descarga */
    .stDownloadButton button {
        background-color: rgba(88, 166, 255, 0.2);
        border: 1px solid #58a6ff;
        color: #58a6ff !important;
        font-weight: 600;
    }
    .stDownloadButton button:hover {
        background-color: rgba(88, 166, 255, 0.3);
    }
    
    /* Separadores */
    hr {
        border-color: rgba(250, 250, 250, 0.2);
        margin: 1.5rem 0;
    }
    
    /* Warnings y alertas */
    .stAlert {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def inicializar_componentes():
    """Inicializa componentes"""
    config_loader = ConfigLoader()
    classifier = CategoryClassifier(config_loader)
    data_loader = DataLoader()
    formatter = CurrencyFormatter(config_loader)
    sidebar = FilterSidebar()
    
    return config_loader, classifier, data_loader, formatter, sidebar


@st.cache_data
def cargar_datos(_data_loader, _classifier, file_path: str = None, _file_mtime: float = None):
    """Carga datos
    
    Args:
        _file_mtime: Tiempo de modificación del archivo (para invalidar caché cuando cambie)
    """
    if file_path is None:
        file_path = "data/categories_timeline.csv"
    
    df = _data_loader.procesar_completo(file_path)
    df = _classifier.clasificar_dataframe(df)
    
    # Excluir filas resumen
    df_analisis = df[df['Grupo'] != 'Resumen'].copy()
    
    # Excluir categorías principales que tienen subcategorías
    # (son filas de totales que causan doble contabilización)
    categorias_con_subcat = _classifier.obtener_categorias_con_subcategorias()
    df_analisis = df_analisis[~df_analisis['Categorías'].isin(categorias_con_subcat)].copy()
    
    return df_analisis


def crear_pivot_table(df: pd.DataFrame, formatter: CurrencyFormatter) -> pd.DataFrame:
    """Crea tabla pivot formateada"""
    # Crear pivot
    pivot = pd.pivot_table(
        df,
        index=['Grupo', 'Categoria_Principal'],
        columns='MesAño',
        values='Monto',
        aggfunc='sum',
        fill_value=0
    )
    
    # Ordenar columnas cronológicamente
    if 'FechaOrden' in df.columns:
        # Crear mapeo de MesAño a FechaOrden para ordenamiento
        orden_map = df.groupby('MesAño')['FechaOrden'].first().sort_values()
        columnas_ordenadas = orden_map.index.tolist()
        
        # Reordenar columnas del pivot según el orden cronológico
        pivot = pivot.reindex(columns=columnas_ordenadas)
    
    # Agregar totales por fila
    pivot['TOTAL'] = pivot.sum(axis=1)
    
    # Agregar totales por columna
    pivot.loc[('TOTAL', ''), :] = pivot.sum(axis=0)
    
    return pivot


def main():
    st.title("📊 Explorador de Datos")
    st.markdown("### Filtra y analiza tus gastos en detalle")
    
    # Inicializar componentes
    config_loader, classifier, data_loader, formatter, sidebar = inicializar_componentes()
    
    # Determinar archivo
    file_path = None
    if 'uploaded_file' in st.session_state:
        uploaded_file = st.session_state.get('uploaded_file')
        if uploaded_file is not None:
            temp_path = Path("data/temp_upload.csv")
            temp_path.parent.mkdir(exist_ok=True)
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            file_path = str(temp_path)
    
    if file_path is None:
        file_path = "data/categories_timeline.csv"
    
    # Obtener tiempo de modificación del archivo para invalidar caché
    file_mtime = os.path.getmtime(file_path)
    
    # Cargar datos
    try:
        df_analisis = cargar_datos(data_loader, classifier, file_path, file_mtime)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        st.stop()
    
    # Renderizar sidebar y obtener datos filtrados
    df_filtrado, filtros = sidebar.renderizar(df_analisis)
    
    st.markdown("---")
    
    # Métricas del dataset filtrado
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 Registros", f"{len(df_filtrado):,}")
    
    with col2:
        categorias = df_filtrado['Categoria_Principal'].nunique()
        st.metric("🏷️ Categorías", categorias)
    
    with col3:
        total_gastos = df_filtrado[df_filtrado['Monto'] < 0]['Monto'].sum()
        st.metric("💸 Gastos", formatter.formatear(abs(total_gastos), incluir_signo=False))
    
    with col4:
        total_ingresos = df_filtrado[df_filtrado['Monto'] > 0]['Monto'].sum()
        st.metric("💵 Ingresos", formatter.formatear(total_ingresos, incluir_signo=False))
    
    with col5:
        balance = total_ingresos + total_gastos
        
        # Determinar el estado del balance
        if balance > 0:
            icono = "📈"
            estado = "Superávit"
            color_fondo = "#d4edda"  # Verde claro
            color_texto = "#155724"   # Verde oscuro
            signo = "+"
        elif balance < 0:
            icono = "📉"
            estado = "Déficit"
            color_fondo = "#f8d7da"  # Rojo claro
            color_texto = "#721c24"   # Rojo oscuro
            signo = ""  # El signo negativo ya viene del número
        else:
            icono = "⚖️"
            estado = "Equilibrado"
            color_fondo = "#d1ecf1"  # Azul claro
            color_texto = "#0c5460"   # Azul oscuro
            signo = ""
        
        # Mostrar balance con estilo visual destacado
        st.markdown(f"""
            <div style="
                background-color: {color_fondo};
                border-left: 5px solid {color_texto};
                padding: 15px;
                border-radius: 5px;
                margin-top: 10px;
            ">
                <div style="color: {color_texto}; font-size: 0.8em; font-weight: 600; margin-bottom: 5px;">
                    {icono} BALANCE - {estado}
                </div>
                <div style="color: {color_texto}; font-size: 1.8em; font-weight: bold;">
                    {signo}{formatter.formatear(abs(balance), incluir_signo=False)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Tabla Pivot", "📊 Vista Detallada", "📈 Resumen por Grupo"])
    
    with tab1:
        st.subheader("Tabla Matricial: Categorías x Períodos")
        
        if len(df_filtrado) == 0:
            st.warning("⚠️ No hay datos para mostrar con los filtros aplicados")
        else:
            # Crear pivot table
            pivot = crear_pivot_table(df_filtrado, formatter)
            
            # Mostrar pivot (sin background_gradient para evitar dependencia de matplotlib)
            st.dataframe(
                pivot.style.format(formatter.formatear),
                use_container_width=True,
                height=600
            )
            
            # Botón de descarga
            csv = pivot.to_csv()
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name="gastos_pivot.csv",
                mime="text/csv"
            )
    
    with tab2:
        st.subheader("Vista Detallada de Transacciones")
        
        if len(df_filtrado) == 0:
            st.warning("⚠️ No hay datos para mostrar con los filtros aplicados")
        else:
            # Preparar dataframe para mostrar
            df_mostrar = df_filtrado[[
                'Fecha', 'MesAño', 'Grupo', 'Categoria_Principal', 
                'Subcategoria', 'Monto'
            ]].copy()
            
            # Formatear monto
            df_mostrar['Monto_Fmt'] = df_mostrar['Monto'].apply(formatter.formatear)
            df_mostrar = df_mostrar.drop('Monto', axis=1)
            
            # Ordenar por fecha (usar FechaOrden si está disponible)
            if 'FechaOrden' in df_filtrado.columns:
                df_mostrar['FechaOrden'] = df_filtrado['FechaOrden']
                df_mostrar = df_mostrar.sort_values('FechaOrden', ascending=False)
                df_mostrar = df_mostrar.drop('FechaOrden', axis=1)
            else:
                df_mostrar = df_mostrar.sort_values('Fecha', ascending=False)
            
            # Mostrar
            st.dataframe(
                df_mostrar,
                use_container_width=True,
                height=600
            )
            
            # Descarga
            csv = df_mostrar.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name="gastos_detalle.csv",
                mime="text/csv"
            )
    
    with tab3:
        st.subheader("Resumen Agrupado")
        
        if len(df_filtrado) == 0:
            st.warning("⚠️ No hay datos para mostrar con los filtros aplicados")
        else:
            # Agrupar por grupo
            resumen_grupo = df_filtrado.groupby('Grupo').agg({
                'Monto': ['sum', 'count', 'mean']
            }).round(2)
            
            resumen_grupo.columns = ['Total', 'Transacciones', 'Promedio']
            resumen_grupo = resumen_grupo.sort_values('Total')
            
            # Calcular porcentajes
            total_abs = resumen_grupo['Total'].abs().sum()
            resumen_grupo['Porcentaje'] = (resumen_grupo['Total'].abs() / total_abs * 100).round(1)
            
            # Formatear
            resumen_grupo['Total_Fmt'] = resumen_grupo['Total'].apply(formatter.formatear)
            resumen_grupo['Promedio_Fmt'] = resumen_grupo['Promedio'].apply(formatter.formatear)
            resumen_grupo['Porcentaje_Fmt'] = resumen_grupo['Porcentaje'].apply(lambda x: f"{x}%")
            
            # Mostrar
            st.dataframe(
                resumen_grupo[['Total_Fmt', 'Transacciones', 'Promedio_Fmt', 'Porcentaje_Fmt']],
                use_container_width=True
            )
            
            # Gráfico de barras simple
            st.bar_chart(resumen_grupo['Total'].abs())


if __name__ == "__main__":
    main()
