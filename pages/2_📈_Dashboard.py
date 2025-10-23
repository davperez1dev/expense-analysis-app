"""
Página 2: Dashboard de Análisis Financiero con Gráficos
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ConfigLoader, CategoryClassifier, DataLoader, CurrencyFormatter
from components.sidebar import FilterSidebar
from components.charts import ChartBuilder
from utils.page_transitions import add_page_transition, add_custom_css

st.set_page_config(
    page_title="Dashboard Financiero",
    page_icon="📈",
    layout="wide"
)

# Aplicar transiciones
add_page_transition()
add_custom_css()

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
    
    /* Gráficos con mejor contraste */
    .js-plotly-plot {
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(250, 250, 250, 0.1);
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Separadores */
    hr {
        border-color: rgba(250, 250, 250, 0.2);
        margin: 1.5rem 0;
    }
    
    /* Columnas con espaciado */
    [data-testid="column"] {
        padding: 0 8px;
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
def inicializar_componentes():
    """Inicializa componentes"""
    config_loader = ConfigLoader()
    classifier = CategoryClassifier(config_loader)
    data_loader = DataLoader()
    formatter = CurrencyFormatter(config_loader)
    sidebar = FilterSidebar()
    chart_builder = ChartBuilder(config_loader)
    
    return config_loader, classifier, data_loader, formatter, sidebar, chart_builder


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


def main():
    st.title("📈 Dashboard de Análisis Financiero")
    st.markdown("### Visualiza tus patrones de gasto e ingresos")
    
    # Inicializar componentes
    config_loader, classifier, data_loader, formatter, sidebar, chart_builder = inicializar_componentes()
    
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
    
    if len(df_filtrado) == 0:
        st.warning("⚠️ No hay datos para mostrar con los filtros aplicados")
        st.stop()
    
    st.markdown("---")
    
    # KPIs Principales
    col1, col2, col3, col4 = st.columns(4)
    
    total_ingresos = df_filtrado[df_filtrado['Monto'] > 0]['Monto'].sum()
    total_gastos = df_filtrado[df_filtrado['Monto'] < 0]['Monto'].sum()
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
        delta_color = "normal" if ganancia_neta >= 0 else "inverse"
        st.metric(
            "💰 Ganancia Neta",
            formatter.formatear(ganancia_neta, incluir_signo=False),
            delta=f"{tasa_ahorro:.1f}%"
        )
    
    with col4:
        if 'Fecha' in df_filtrado.columns:
            num_meses = df_filtrado['Fecha'].nunique()
            promedio = total_gastos / num_meses if num_meses > 0 else 0
        else:
            promedio = 0
        
        st.metric(
            "📊 Promedio Mensual",
            formatter.formatear(abs(promedio), incluir_signo=False),
            delta=None
        )
    
    st.markdown("---")
    
    # Tabs con diferentes análisis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Visión General", 
        "📈 Evolución Temporal", 
        "📊 Análisis de Categorías",
        "💵 Análisis de Ingresos",
        "⚖️ Comparativas"
    ])
    
    with tab1:
        st.subheader("Visión General del Período")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 📊 EXPLICACIÓN - Distribución por Grupo
            st.info("""
            **Distribución de Gastos por Grupo**
            
            Visualiza la proporción de gastos por categoría (Básico, Discrecional, Necesario).
            
            **Pregunta clave:** ¿Dónde se va la mayor parte de mi dinero?
            """)
            
            # Gráfico de dona - SOLO GASTOS
            df_solo_gastos = df_filtrado[df_filtrado['Monto'] < 0]
            fig_dona = chart_builder.grafico_dona(
                df_solo_gastos,
                titulo="Distribución de Gastos por Grupo"
            )
            st.plotly_chart(fig_dona, use_container_width=True)
        
        with col2:
            # 📊 EXPLICACIÓN - Flujo Financiero
            st.info("""
            **Flujo Financiero: Ingresos → Gastos**
            
            Diagrama de cascada que muestra cómo tus ingresos se transforman en gastos por grupo, revelando tu ganancia neta.
            
            **Pregunta clave:** ¿Cómo fluye mi dinero desde los ingresos hasta el resultado final?
            """)
            
            # Gráfico waterfall
            fig_waterfall = chart_builder.grafico_waterfall(
                df_filtrado,
                titulo="Flujo Financiero: Ingresos → Gastos"
            )
            st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # Gráfico de líneas: Ingresos vs Gastos
        st.subheader("Evolución: Ingresos vs Gastos")
        
        # 📊 EXPLICACIÓN - Comparación Temporal
        st.info("""
        **Comparación Ingresos vs Gastos Mensual**
        
        Grafica ambas líneas en el tiempo para identificar meses de superávit o déficit.
        
        **Preguntas que responde:**
        - ¿Mis ingresos superan a mis gastos consistentemente?
        - ¿En qué meses tuve déficit?
        - ¿Hay correlación entre aumentos de ingresos y gastos?
        """)
        
        df_ingresos = df_filtrado[df_filtrado['Monto'] > 0].copy()
        df_gastos = df_filtrado[df_filtrado['Monto'] < 0].copy()
        df_gastos['Monto'] = df_gastos['Monto'].abs()
        
        df_ingresos['Tipo'] = 'Ingresos'
        df_gastos['Tipo'] = 'Gastos'
        
        df_comparacion = pd.concat([df_ingresos, df_gastos])
        
        if 'Fecha' in df_comparacion.columns:
            df_agrupado = df_comparacion.groupby(['Fecha', 'Tipo'])['Monto'].sum().reset_index()
            
            fig_lineas = px.line(
                df_agrupado,
                x='Fecha',
                y='Monto',
                color='Tipo',
                title='Comparación Ingresos vs Gastos Mensual',
                labels={'Fecha': 'Fecha', 'Monto': 'Monto ($)', 'Tipo': 'Tipo'},
                color_discrete_map={'Ingresos': '#27AE60', 'Gastos': '#E74C3C'}
            )
            fig_lineas.update_traces(mode='lines+markers')
            fig_lineas.update_layout(template='plotly_white', height=400)
            
            st.plotly_chart(fig_lineas, use_container_width=True)
    
    with tab2:
        st.subheader("Análisis de Evolución Temporal")
        
        # 📊 EXPLICACIÓN - Evolución por Grupo
        st.info("""
        **Evolución de Gastos por Grupo**
        
        Líneas de tendencia que muestran cómo cada grupo de gastos evoluciona mes a mes.
        
        **Preguntas que responde:**
        - ¿Qué grupos de gasto están aumentando o disminuyendo?
        - ¿Hay estacionalidad en algún grupo específico?
        - ¿Qué grupo tiene mayor variabilidad?
        """)
        
        # Gráfico de líneas por grupo
        fig_evolucion = chart_builder.grafico_lineas_evolucion(
            df_filtrado[df_filtrado['Monto'] < 0],  # Solo gastos
            titulo="Evolución de Gastos por Grupo"
        )
        st.plotly_chart(fig_evolucion, use_container_width=True)
        
        # Gráfico de área apilada
        st.subheader("Composición de Gastos en el Tiempo")
        
        # 📊 EXPLICACIÓN - Área Apilada
        st.info("""
        **Distribución de Gastos (Área Apilada)**
        
        Muestra la composición total de gastos y cómo cada grupo contribuye al total en cada período.
        
        **Preguntas que responde:**
        - ¿Cómo cambia la proporción de cada grupo a lo largo del tiempo?
        - ¿El total de gastos está creciendo o disminuyendo?
        - ¿Qué grupo domina en cada período?
        """)
        
        fig_area = chart_builder.grafico_area_apilada(
            df_filtrado[df_filtrado['Monto'] < 0],
            titulo="Distribución de Gastos (Área Apilada)"
        )
        st.plotly_chart(fig_area, use_container_width=True)
        
        # Gráfico de barras apiladas
        st.subheader("Distribución Mensual Detallada")
        
        # 📊 EXPLICACIÓN - Barras Apiladas
        st.info("""
        **Gastos Mensuales por Grupo**
        
        Visualización en barras apiladas que facilita la comparación mes a mes del total y la composición de gastos.
        
        **Preguntas que responde:**
        - ¿En qué meses gasté más en total?
        - ¿Cómo se distribuyen los gastos dentro de cada mes?
        - ¿Hay patrones recurrentes en la composición mensual?
        """)
        
        fig_barras = chart_builder.grafico_barras_apiladas(
            df_filtrado[df_filtrado['Monto'] < 0],
            titulo="Gastos Mensuales por Grupo"
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    
    with tab3:
        st.subheader("Análisis Detallado de Categorías")
        
        # 📊 EXPLICACIÓN - Pareto
        st.info("""
        **Top 10 Categorías con Mayor Gasto (Principio de Pareto)**
        
        Aplica la regla 80/20: típicamente el 80% de tus gastos proviene del 20% de las categorías. 
        Este gráfico identifica dónde concentrar tus esfuerzos de optimización.
        
        **Preguntas que responde:**
        - ¿Cuáles son mis categorías de mayor impacto?
        - ¿Qué porcentaje acumulado representan mis top 10 categorías?
        - ¿Dónde debo enfocarme para reducir gastos significativamente?
        """)
        
        # Gráfico de Pareto
        fig_pareto = chart_builder.grafico_pareto(
            df_filtrado,
            top_n=10,
            titulo="Top 10 Categorías con Mayor Gasto (Pareto)"
        )
        st.plotly_chart(fig_pareto, use_container_width=True)
        
        # Heatmap
        st.subheader("Mapa de Calor: Gastos por Categoría y Período")
        
        # 📊 EXPLICACIÓN - Heatmap
        st.info("""
        **Intensidad de Gasto (Top 15 Categorías)**
        
        Mapa de calor que revela patrones de gasto por categoría a lo largo del tiempo. 
        Los colores más intensos indican mayores gastos.
        
        **Preguntas que responde:**
        - ¿Qué categorías tienen gastos recurrentes vs. esporádicos?
        - ¿Hay concentración de gastos en períodos específicos?
        - ¿Qué categorías presentan mayor variabilidad temporal?
        """)
        
        # Filtrar solo top 15 categorías para mejor visualización
        top_cats = df_filtrado[df_filtrado['Monto'] < 0].groupby('Categoria_Principal')['Monto'].sum().abs().nlargest(15).index
        df_top = df_filtrado[df_filtrado['Categoria_Principal'].isin(top_cats)]
        
        fig_heatmap = chart_builder.grafico_heatmap(
            df_top,
            titulo="Intensidad de Gasto (Top 15 Categorías)"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Tabla de categorías principales
        st.subheader("Ranking de Categorías")
        
        # 📊 EXPLICACIÓN - Ranking
        st.info("""
        **Ranking de Categorías (Top 20)**
        
        Tabla detallada que desglosa cada categoría por total gastado, número de transacciones, 
        promedio por transacción y porcentaje del total.
        
        **Preguntas que responde:**
        - ¿Cuánto gasto en total en cada categoría?
        - ¿Cuántas veces al mes gasto en cada categoría?
        - ¿Cuál es el ticket promedio de cada categoría?
        - ¿Cuánto gasto en promedio por mes en cada categoría?
        - ¿Qué porcentaje de mi presupuesto consume cada categoría?
        """)
        
        # Calcular número de meses únicos en el período
        df_gastos_detalle = df_filtrado[df_filtrado['Monto'] < 0]
        num_meses_gastos = df_gastos_detalle['MesAño'].nunique() if 'MesAño' in df_gastos_detalle.columns else 1
        
        ranking = df_gastos_detalle.groupby('Categoria_Principal').agg({
            'Monto': ['sum', 'count', 'mean']
        }).round(2)
        ranking.columns = ['Total', 'Transacciones', 'Promedio x Transacción']
        ranking['Total'] = ranking['Total'].abs()
        ranking['Promedio x Transacción'] = ranking['Promedio x Transacción'].abs()
        ranking = ranking.sort_values('Total', ascending=False).head(20)
        
        # Calcular promedio mensual por categoría
        ranking['Promedio x Mes'] = (ranking['Total'] / num_meses_gastos).round(2)
        
        # Calcular porcentaje
        total_abs = ranking['Total'].sum()
        ranking['%'] = (ranking['Total'] / total_abs * 100).round(1)
        
        # Formatear
        ranking['Total'] = ranking['Total'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
        ranking['Promedio x Transacción'] = ranking['Promedio x Transacción'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
        ranking['Promedio x Mes'] = ranking['Promedio x Mes'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
        
        st.dataframe(ranking, use_container_width=True)
        
        # Nota explicativa
        st.caption(f"""
        📊 **Interpretación de las columnas de Promedio:**
        - **Promedio x Transacción:** Monto promedio de cada gasto individual en esa categoría
        - **Promedio x Mes:** Cuánto gastas en promedio por mes en esa categoría (Total ÷ {num_meses_gastos} meses)
        """)
    
    with tab4:
        st.subheader("Análisis de Fuentes de Ingresos")
        
        df_ingresos_detalle = df_filtrado[df_filtrado['Monto'] > 0]
        
        if len(df_ingresos_detalle) == 0:
            st.info("No hay registros de ingresos en el período filtrado")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # 📊 EXPLICACIÓN - Composición de Ingresos
                st.info("""
                **Composición de Ingresos por Fuente**
                
                Muestra la distribución porcentual de tus ingresos según su origen (salario, ingresos pasivos, extras, etc.).
                
                **Pregunta clave:** ¿De dónde proviene la mayor parte de mis ingresos?
                """)
                
                # Gráfico de dona de ingresos
                fig_ingresos_dona = chart_builder.grafico_dona(
                    df_ingresos_detalle,
                    grupo_col='Categoria_Principal',
                    titulo="Composición de Ingresos por Fuente"
                )
                st.plotly_chart(fig_ingresos_dona, use_container_width=True)
            
            with col2:
                # 📊 EXPLICACIÓN - Evolución de Ingresos
                st.info("""
                **Evolución de Ingresos por Fuente**
                
                Traza la evolución temporal de cada fuente de ingreso, permitiendo identificar cuáles son recurrentes y cuáles ocasionales.
                
                **Pregunta clave:** ¿Qué fuentes son más estables en el tiempo?
                """)
                
                # Evolución de ingresos
                fig_ingresos_evol = chart_builder.grafico_lineas_evolucion(
                    df_ingresos_detalle,
                    grupo_col='Categoria_Principal',
                    titulo="Evolución de Ingresos por Fuente"
                )
                st.plotly_chart(fig_ingresos_evol, use_container_width=True)
            
            # Gráfico de evolución mensual de ingresos totales
            st.subheader("📈 Evolución Mensual de Ingresos Totales")
            
            # 📊 EXPLICACIÓN DEL GRÁFICO
            st.info("""
            **¿Qué muestra este gráfico?**  
            Visualiza la evolución temporal de tus ingresos totales mes a mes, con una línea de referencia del promedio.
            
            **Preguntas que responde:**
            - ¿En qué meses recibo más ingresos?
            - ¿Mis ingresos son estables o fluctúan significativamente?
            - **Promedio de Referencia (línea roja):** Es el promedio simple de TODOS los meses mostrados. 
              Esta línea horizontal te ayuda a identificar rápidamente qué meses estuvieron por encima o por debajo 
              del promedio general del período filtrado.
            - ¿Hay una tendencia general de crecimiento o decrecimiento en mis ingresos?
            """)
            
            with st.expander("💡 ¿Cómo interpretar la línea de promedio?"):
                st.markdown("""
                **La línea roja horizontal representa el PROMEDIO FIJO** de todos los meses visibles.
                
                **Ejemplo:**
                - Enero 2024: $50,000
                - Febrero 2024: $60,000  
                - Marzo 2024: $45,000
                - **Promedio = $51,667** (línea recta que cruza horizontalmente)
                
                **Interpretación:**
                - 📈 **Barras por encima** de la línea = Meses con ingresos superiores al promedio
                - 📉 **Barras por debajo** de la línea = Meses con ingresos inferiores al promedio
                
                Esta línea NO varía porque es un **promedio fijo** del período completo, 
                útil como punto de referencia para comparar el desempeño de cada mes.
                """)
            
            # Agrupar ingresos por mes
            ingresos_por_mes = df_ingresos_detalle.groupby('MesAño')['Monto'].sum().reset_index()
            
            # Ordenar cronológicamente si tenemos la columna de orden
            if 'FechaOrden' in df_ingresos_detalle.columns:
                orden_meses = df_ingresos_detalle.groupby('MesAño')['FechaOrden'].first().sort_values()
                ingresos_por_mes['FechaOrden'] = ingresos_por_mes['MesAño'].map(orden_meses)
                ingresos_por_mes = ingresos_por_mes.sort_values('FechaOrden')
            
            # Calcular el promedio de ingresos
            promedio_ingresos = ingresos_por_mes['Monto'].mean()
            
            # Crear gráfico de barras
            fig_ingresos_mes = px.bar(
                ingresos_por_mes,
                x='MesAño',
                y='Monto',
                title='Ingresos Totales por Mes',
                labels={'MesAño': 'Mes', 'Monto': 'Ingresos ($)'},
                color='Monto',
                color_continuous_scale='Greens'
            )
            
            # Agregar línea de promedio
            fig_ingresos_mes.add_trace(
                go.Scatter(
                    x=ingresos_por_mes['MesAño'],
                    y=[promedio_ingresos] * len(ingresos_por_mes),
                    mode='lines',
                    name=f'Promedio: {formatter.formatear(promedio_ingresos, incluir_signo=False)}',
                    line=dict(color='#FF6B6B', width=3, dash='dash'),
                    hovertemplate='Promedio: %{y:,.2f}<extra></extra>'
                )
            )
            
            fig_ingresos_mes.update_layout(
                template='plotly_dark',
                height=400,
                xaxis_tickangle=-45,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_ingresos_mes, use_container_width=True)
            
            # Tabla resumen de ingresos
            st.subheader("Detalle de Ingresos por Categoría")
            
            # 📊 EXPLICACIÓN DE LA TABLA
            st.info("""
            **¿Qué muestra esta tabla?**  
            Desglosa tus ingresos por categoría principal, mostrando el total recibido, número de transacciones, 
            promedio por transacción y porcentaje de contribución al total.
            
            **Preguntas que responde:**
            - ¿Cuál es mi principal fuente de ingresos?
            - ¿Qué porcentaje de mis ingresos proviene de cada fuente?
            - ¿Cuántas veces al mes recibo ingresos de cada categoría?
            - ¿Cuál es el monto promedio por transacción en cada categoría?
            - ¿Cuánto recibo en promedio por mes de cada fuente?
            """)
            
            # Calcular número de meses únicos en el período
            num_meses = df_ingresos_detalle['MesAño'].nunique() if 'MesAño' in df_ingresos_detalle.columns else 1
            
            resumen_ingresos = df_ingresos_detalle.groupby('Categoria_Principal').agg({
                'Monto': ['sum', 'count', 'mean']
            }).round(2)
            resumen_ingresos.columns = ['Total', 'Transacciones', 'Promedio x Transacción']
            resumen_ingresos = resumen_ingresos.sort_values('Total', ascending=False)
            
            # Calcular promedio mensual por categoría
            resumen_ingresos['Promedio x Mes'] = (resumen_ingresos['Total'] / num_meses).round(2)
            
            # Guardar valores numéricos antes de formatear
            total_ing = resumen_ingresos['Total'].sum()
            total_transacciones = resumen_ingresos['Transacciones'].sum()
            promedio_por_transaccion = total_ing / total_transacciones if total_transacciones > 0 else 0
            promedio_por_mes = total_ing / num_meses if num_meses > 0 else 0
            
            resumen_ingresos['%'] = (resumen_ingresos['Total'] / total_ing * 100).round(1)
            
            # Crear fila de totales con valores numéricos correctos
            fila_total = pd.DataFrame({
                'Total': [total_ing],
                'Transacciones': [total_transacciones],
                'Promedio x Transacción': [promedio_por_transaccion],
                'Promedio x Mes': [promedio_por_mes],
                '%': [100.0]
            }, index=['TOTAL'])
            
            # Formatear montos antes de concatenar
            resumen_ingresos['Total'] = resumen_ingresos['Total'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
            resumen_ingresos['Promedio x Transacción'] = resumen_ingresos['Promedio x Transacción'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
            resumen_ingresos['Promedio x Mes'] = resumen_ingresos['Promedio x Mes'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
            
            fila_total['Total'] = fila_total['Total'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
            fila_total['Promedio x Transacción'] = fila_total['Promedio x Transacción'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
            fila_total['Promedio x Mes'] = fila_total['Promedio x Mes'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
            
            # Concatenar tabla con fila de totales
            resumen_ingresos_completo = pd.concat([resumen_ingresos, fila_total])
            
            st.dataframe(resumen_ingresos_completo, use_container_width=True)
            
            # Nota explicativa sobre los promedios
            st.caption(f"""
            📊 **Interpretación de las columnas de Promedio:**
            
            - **Promedio x Transacción:** Monto promedio de cada ingreso individual (Total ÷ Número de transacciones)
            - **Promedio x Mes:** Cuánto recibes en promedio por mes de esa fuente (Total ÷ {num_meses} meses)
            
            **Nota sobre fila TOTAL:** Los promedios NO se suman, se calculan sobre el total general.
            - Promedio x Transacción TOTAL = Total de ingresos ÷ Total de transacciones
            - Promedio x Mes TOTAL = Total de ingresos ÷ {num_meses} meses
            """)
    
    with tab5:
        st.subheader("Comparativas y Análisis Adicional")
        
        # Comparación por grupo
        st.subheader("Comparación de Grupos")
        
        # 📊 EXPLICACIÓN - Comparación de Grupos
        st.info("""
        **Comparación de Gastos por Grupo**
        
        Compara el total gastado en cada grupo para identificar prioridades y oportunidades de ahorro.
        
        **Preguntas que responde:**
        - ¿Qué grupo consume más recursos?
        - ¿La distribución de gastos está alineada con mis prioridades?
        - ¿En qué grupo puedo reducir gastos más fácilmente?
        """)
        
        # Filtrar solo gastos (montos negativos)
        df_solo_gastos_comp = df_filtrado[df_filtrado['Monto'] < 0]
        comparacion_grupos = df_solo_gastos_comp.groupby('Grupo')['Monto'].sum().abs().sort_values(ascending=False)
        
        fig_comp = go.Figure(data=[
            go.Bar(
                x=comparacion_grupos.index,
                y=comparacion_grupos.values,
                marker_color=[config_loader.get_color_grupo(g) for g in comparacion_grupos.index]
            )
        ])
        fig_comp.update_layout(
            title="Comparación de Gastos por Grupo",
            xaxis_title="Grupo",
            yaxis_title="Monto Total ($)",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Top 5 vs Resto
        st.subheader("Concentración del Gasto: Top 5 vs Resto")
        
        # 📊 EXPLICACIÓN - Concentración del Gasto
        st.info("""
        **Concentración del Gasto (Top 5 vs Resto)**
        
        Evalúa si tus gastos están concentrados en pocas categorías o distribuidos uniformemente. 
        Una alta concentración indica oportunidades claras de optimización.
        
        **Preguntas que responde:**
        - ¿Qué porcentaje de mis gastos está en solo 5 categorías?
        - ¿Mis gastos están muy concentrados o distribuidos?
        - ¿Vale la pena enfocarme solo en las top 5 para optimizar?
        """)
        
        top5 = df_filtrado[df_filtrado['Monto'] < 0].groupby('Categoria_Principal')['Monto'].sum().abs().nlargest(5)
        resto = df_filtrado[df_filtrado['Monto'] < 0]['Monto'].sum() - top5.sum()
        
        concentracion = pd.DataFrame({
            'Categoria': list(top5.index) + ['Otras'],
            'Monto': list(top5.values) + [abs(resto)]
        })
        
        fig_concentracion = px.pie(
            concentracion,
            values='Monto',
            names='Categoria',
            title='Concentración del Gasto (Top 5 vs Resto)'
        )
        st.plotly_chart(fig_concentracion, use_container_width=True)


if __name__ == "__main__":
    main()
