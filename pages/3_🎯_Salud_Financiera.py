"""
Página: Salud Financiera
Dashboard con métricas clave de análisis financiero personal
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from components.sidebar import FilterSidebar
from utils.data_loader import DataLoader
from utils.formatters import CurrencyFormatter
from utils.config_loader import ConfigLoader
from utils.category_classifier import CategoryClassifier
from utils.page_transitions import add_page_transition, add_custom_css

# Configuración de página
st.set_page_config(
    page_title="Salud Financiera",
    page_icon="🎯",
    layout="wide"
)

# Aplicar transiciones
add_page_transition()
add_custom_css()

# CSS personalizado para mejorar visualización
st.markdown("""
    <style>
    /* Mejorar contraste de dropdowns */
    [data-baseweb="select"] {
        background-color: #2d2d2d !important;
    }
    
    [data-baseweb="popover"] {
        background-color: #2d2d2d !important;
    }
    
    [data-baseweb="menu"] {
        background-color: #2d2d2d !important;
    }
    
    [role="option"] {
        background-color: #2d2d2d !important;
        padding: 8px 12px !important;
    }
    
    [role="option"]:hover {
        background-color: #3d3d3d !important;
    }
    
    [data-baseweb="tag"] {
        background-color: rgba(88, 166, 255, 0.2) !important;
    }
    
    /* Estilos para métricas */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-description {
        font-size: 0.8em;
        opacity: 0.8;
        margin-top: 5px;
    }
    
    /* Score de salud financiera */
    .health-score {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
    
    .score-excellent { color: #27ae60; }
    .score-good { color: #2ecc71; }
    .score-fair { color: #f39c12; }
    .score-poor { color: #e74c3c; }
    
    /* Insights */
    .insight-box {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    
    .insight-warning {
        background-color: #fff3cd;
        border-color: #ffc107;
        color: #856404;
    }
    
    .insight-success {
        background-color: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    
    .insight-info {
        background-color: #d1ecf1;
        border-color: #17a2b8;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)


def calcular_tasa_ahorro(ingresos: float, gastos: float) -> float:
    """Calcula la tasa de ahorro como porcentaje"""
    if ingresos <= 0:
        return 0
    return ((ingresos - abs(gastos)) / ingresos) * 100


def calcular_runway_emergencia(gastos_necesarios_mes: float, balance: float) -> float:
    """Calcula cuántos meses puede sobrevivir con ahorros actuales"""
    if gastos_necesarios_mes <= 0:
        return 0
    return balance / abs(gastos_necesarios_mes)


def calcular_ratio_grupos(df: pd.DataFrame) -> dict:
    """Calcula el ratio de gastos por grupo (Necesarios/Básicos/Discrecionales)"""
    gastos = df[df['Monto'] < 0].copy()
    
    if len(gastos) == 0:
        return {'Necesario': 0, 'Básico': 0, 'Discrecional': 0}
    
    total_gastos = abs(gastos['Monto'].sum())
    
    if total_gastos == 0:
        return {'Necesario': 0, 'Básico': 0, 'Discrecional': 0}
    
    ratio = {}
    for grupo in ['Necesario', 'Básico', 'Discrecional']:
        monto_grupo = abs(gastos[gastos['Grupo'] == grupo]['Monto'].sum())
        ratio[grupo] = (monto_grupo / total_gastos) * 100
    
    return ratio


def crear_gauge_chart(valor: float, titulo: str, ranges: list, colors: list, sufijo: str = "%") -> go.Figure:
    """Crea un gráfico gauge (velocímetro)"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': titulo, 'font': {'size': 20}},
        number={'suffix': sufijo, 'font': {'size': 40}},
        gauge={
            'axis': {'range': [None, ranges[-1][1]], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': "darkblue", 'thickness': 0.25},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [ranges[i][0], ranges[i][1]], 'color': colors[i]}
                for i in range(len(ranges))
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': valor
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"}
    )
    
    return fig


def generar_insights(df: pd.DataFrame, tasa_ahorro: float, ratio_grupos: dict) -> list:
    """Genera insights automáticos basados en los datos"""
    insights = []
    
    # Insight 1: Tasa de ahorro
    if tasa_ahorro >= 30:
        insights.append({
            'tipo': 'success',
            'icono': '🎉',
            'mensaje': f'¡Excelente! Tu tasa de ahorro es {tasa_ahorro:.1f}%, superando la recomendación del 20%'
        })
    elif tasa_ahorro >= 20:
        insights.append({
            'tipo': 'success',
            'icono': '✅',
            'mensaje': f'Buen trabajo. Tu tasa de ahorro es {tasa_ahorro:.1f}%, cumpliendo la recomendación mínima'
        })
    elif tasa_ahorro >= 10:
        insights.append({
            'tipo': 'warning',
            'icono': '⚠️',
            'mensaje': f'Tu tasa de ahorro es {tasa_ahorro:.1f}%. Intenta aumentarla al 20% para mayor seguridad financiera'
        })
    else:
        insights.append({
            'tipo': 'warning',
            'icono': '🚨',
            'mensaje': f'Tasa de ahorro baja ({tasa_ahorro:.1f}%). Considera reducir gastos discrecionales'
        })
    
    # Insight 2: Ratio de grupos
    if ratio_grupos.get('Necesario', 0) > 60:
        insights.append({
            'tipo': 'warning',
            'icono': '💡',
            'mensaje': f'Los gastos necesarios representan {ratio_grupos["Necesario"]:.1f}% de tus gastos. Busca optimizar costos esenciales'
        })
    
    if ratio_grupos.get('Discrecional', 0) > 30:
        insights.append({
            'tipo': 'info',
            'icono': '💰',
            'mensaje': f'Los gastos discrecionales son {ratio_grupos["Discrecional"]:.1f}% del total. Hay oportunidad de ahorro aquí'
        })
    
    # Insight 3: Top gastos
    gastos = df[df['Monto'] < 0].copy()
    if len(gastos) > 0:
        top_categoria = gastos.groupby('Categoria_Principal')['Monto'].sum().abs().idxmax()
        monto_top = abs(gastos.groupby('Categoria_Principal')['Monto'].sum()[top_categoria])
        insights.append({
            'tipo': 'info',
            'icono': '🔝',
            'mensaje': f'Tu mayor gasto es en "{top_categoria}" con ${monto_top:,.0f}'
        })
    
    return insights


def calcular_score_salud(tasa_ahorro: float, runway: float, ratio_grupos: dict) -> tuple:
    """Calcula un score de salud financiera de 0-100"""
    score = 0
    
    # Componente 1: Tasa de ahorro (40 puntos máx)
    if tasa_ahorro >= 30:
        score += 40
    elif tasa_ahorro >= 20:
        score += 30
    elif tasa_ahorro >= 10:
        score += 20
    else:
        score += max(0, tasa_ahorro)
    
    # Componente 2: Runway de emergencia (30 puntos máx)
    if runway >= 6:
        score += 30
    elif runway >= 3:
        score += 20
    elif runway >= 1:
        score += 10
    else:
        score += max(0, runway * 5)
    
    # Componente 3: Balance de categorías (30 puntos máx)
    necesario = ratio_grupos.get('Necesario', 0)
    basico = ratio_grupos.get('Básico', 0)
    discrecional = ratio_grupos.get('Discrecional', 0)
    
    # Ideal: 50% necesario, 30% básico, 20% discrecional
    desviacion = abs(necesario - 50) + abs(basico - 30) + abs(discrecional - 20)
    score += max(0, 30 - (desviacion / 3))
    
    # Determinar categoría
    if score >= 80:
        categoria = 'Excelente'
        clase_css = 'score-excellent'
    elif score >= 60:
        categoria = 'Bueno'
        clase_css = 'score-good'
    elif score >= 40:
        categoria = 'Regular'
        clase_css = 'score-fair'
    else:
        categoria = 'Necesita Mejora'
        clase_css = 'score-poor'
    
    return round(score), categoria, clase_css


def main():
    st.title("🎯 Salud Financiera")
    st.markdown("**Métricas clave y análisis de tu situación financiera**")
    
    # Cargar datos y componentes
    config = ConfigLoader()
    loader = DataLoader()
    classifier = CategoryClassifier(config)
    formatter = CurrencyFormatter(config)
    
    # Cargar y clasificar datos
    df_completo = loader.procesar_completo('data/categories_timeline.csv')
    df_completo = classifier.clasificar_dataframe(df_completo)
    
    # Excluir filas resumen
    df_completo = df_completo[df_completo['Grupo'] != 'Resumen'].copy()
    
    # Sidebar con filtros
    sidebar = FilterSidebar()
    df_filtrado, filtros = sidebar.renderizar(df_completo)
    
    if len(df_filtrado) == 0:
        st.warning("⚠️ No hay datos para mostrar con los filtros aplicados")
        return
    
    # Calcular métricas principales
    total_ingresos = df_filtrado[df_filtrado['Monto'] > 0]['Monto'].sum()
    total_gastos = df_filtrado[df_filtrado['Monto'] < 0]['Monto'].sum()
    balance = total_ingresos + total_gastos
    
    tasa_ahorro = calcular_tasa_ahorro(total_ingresos, total_gastos)
    
    # Calcular gastos necesarios mensuales (solo grupo Necesario)
    gastos_necesarios = df_filtrado[
        (df_filtrado['Monto'] < 0) & 
        (df_filtrado['Grupo'] == 'Necesario')
    ]['Monto'].sum()
    
    # Calcular meses únicos para promedios
    num_meses = df_filtrado['MesAño'].nunique() if 'MesAño' in df_filtrado.columns else 1
    gastos_necesarios_mes = abs(gastos_necesarios) / max(num_meses, 1)
    
    runway = calcular_runway_emergencia(gastos_necesarios_mes, balance)
    ratio_grupos = calcular_ratio_grupos(df_filtrado)
    
    # Calcular score de salud
    score, categoria_score, clase_css = calcular_score_salud(tasa_ahorro, runway, ratio_grupos)
    
    # Mostrar score principal
    st.markdown(f"""
        <div class="health-score {clase_css}">
            Score de Salud Financiera: {score}/100
            <div style="font-size: 0.4em; margin-top: 10px;">({categoria_score})</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sección 1: Métricas Clave
    st.subheader("📊 Métricas Clave")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Gauge de tasa de ahorro
        fig_ahorro = crear_gauge_chart(
            tasa_ahorro,
            "Tasa de Ahorro",
            [(0, 10), (10, 20), (20, 30), (30, 50)],
            ['#e74c3c', '#f39c12', '#2ecc71', '#27ae60']
        )
        st.plotly_chart(fig_ahorro, use_container_width=True)
        st.caption("✅ Ideal: >20% | 🎯 Excelente: >30%")
    
    with col2:
        # Gauge de runway
        fig_runway = crear_gauge_chart(
            runway,
            "Runway Emergencia",
            [(0, 3), (3, 6), (6, 12), (12, 24)],
            ['#e74c3c', '#f39c12', '#2ecc71', '#27ae60'],
            sufijo=" meses"
        )
        st.plotly_chart(fig_runway, use_container_width=True)
        st.caption("✅ Mínimo: 6 meses | 🎯 Ideal: 12 meses")
    
    with col3:
        # Resumen numérico
        st.metric("💵 Ingresos", formatter.formatear(total_ingresos, incluir_signo=False))
        st.metric("💸 Gastos", formatter.formatear(abs(total_gastos), incluir_signo=False))
        st.metric("💰 Balance", formatter.formatear(balance, incluir_signo=True))
        st.caption(f"Ahorro mensual promedio: {formatter.formatear(balance/max(num_meses, 1), incluir_signo=False)}")
    
    st.markdown("---")
    
    # Sección 2: Ratio de Grupos
    st.subheader("📊 Distribución de Gastos: Necesarios / Básicos / Discrecionales")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Gráfico de dona
        labels = list(ratio_grupos.keys())
        values = list(ratio_grupos.values())
        
        fig_dona = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker=dict(colors=['#BD10E0', '#4A90E2', '#F5A623']),
            textinfo='label+percent',
            textfont=dict(size=14)
        )])
        
        fig_dona.update_layout(
            title="Tu Distribución Actual",
            height=400,
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        
        st.plotly_chart(fig_dona, use_container_width=True)
    
    with col2:
        # Comparación con ideal
        ideal_ratio = {'Necesario': 50, 'Básico': 30, 'Discrecional': 20}
        
        df_comparacion = pd.DataFrame({
            'Categoría': ['Necesario', 'Básico', 'Discrecional'],
            'Tu Ratio': [ratio_grupos.get('Necesario', 0), ratio_grupos.get('Básico', 0), ratio_grupos.get('Discrecional', 0)],
            'Ideal': [ideal_ratio['Necesario'], ideal_ratio['Básico'], ideal_ratio['Discrecional']]
        })
        
        fig_comparacion = go.Figure()
        
        fig_comparacion.add_trace(go.Bar(
            name='Tu Ratio',
            x=df_comparacion['Categoría'],
            y=df_comparacion['Tu Ratio'],
            marker_color='#4A90E2',
            text=df_comparacion['Tu Ratio'].round(1),
            texttemplate='%{text}%',
            textposition='outside'
        ))
        
        fig_comparacion.add_trace(go.Bar(
            name='Ideal',
            x=df_comparacion['Categoría'],
            y=df_comparacion['Ideal'],
            marker_color='#27ae60',
            text=df_comparacion['Ideal'],
            texttemplate='%{text}%',
            textposition='outside'
        ))
        
        fig_comparacion.update_layout(
            title="Comparación vs Ideal",
            barmode='group',
            height=400,
            yaxis_title="Porcentaje (%)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            showlegend=True
        )
        
        st.plotly_chart(fig_comparacion, use_container_width=True)
    
    st.markdown("---")
    
    # Sección 3: Top 5 Gastos Más Altos
    st.subheader("🔥 Top 5 Gastos Más Altos del Período")
    
    gastos = df_filtrado[df_filtrado['Monto'] < 0].copy()
    if len(gastos) > 0:
        top_gastos = gastos.nlargest(5, 'Monto', keep='first')[
            ['Fecha', 'Categoria_Principal', 'Categorías', 'Monto', 'Grupo']
        ].copy()
        top_gastos['Monto'] = top_gastos['Monto'].abs()
        top_gastos['Monto_Formato'] = top_gastos['Monto'].apply(lambda x: formatter.formatear(x, incluir_signo=False))
        
        # Mostrar como tabla estilizada
        st.dataframe(
            top_gastos[['Fecha', 'Categoria_Principal', 'Categorías', 'Monto_Formato', 'Grupo']].rename(columns={
                'Categoria_Principal': 'Categoría Principal',
                'Monto_Formato': 'Monto'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        total_top5 = top_gastos['Monto'].sum()
        porcentaje_top5 = (total_top5 / abs(total_gastos)) * 100
        st.caption(f"💡 Estos 5 gastos representan el {porcentaje_top5:.1f}% de tus gastos totales ({formatter.formatear(total_top5, incluir_signo=False)})")
    else:
        st.info("No hay gastos para mostrar")
    
    st.markdown("---")
    
    # Sección 4: Insights Automáticos
    st.subheader("💡 Insights y Recomendaciones")
    
    insights = generar_insights(df_filtrado, tasa_ahorro, ratio_grupos)
    
    for insight in insights:
        st.markdown(f"""
            <div class="insight-box insight-{insight['tipo']}">
                <strong>{insight['icono']} {insight['mensaje']}</strong>
            </div>
        """, unsafe_allow_html=True)
    
    # Agregar recomendaciones generales
    st.markdown("---")
    with st.expander("📚 Recomendaciones Generales de Finanzas Personales"):
        st.markdown("""
        ### 🎯 Reglas de Oro:
        
        1. **Tasa de Ahorro Mínima:** 20% de tus ingresos
        2. **Fondo de Emergencia:** 6-12 meses de gastos necesarios
        3. **Distribución Ideal de Gastos:**
           - 50% Necesarios (vivienda, comida, transporte básico)
           - 30% Básicos (educación, cuidado personal, entretenimiento moderado)
           - 20% Discrecionales (gustos, extras, lujos)
        
        ### 💪 Estrategias para Mejorar:
        
        - **Aumenta ingresos:** Busca fuentes adicionales (freelance, inversiones)
        - **Reduce gastos discrecionales:** Identifica gastos hormiga
        - **Optimiza gastos fijos:** Renegocia servicios, elimina suscripciones no usadas
        - **Automatiza ahorros:** Transfiere el % de ahorro apenas cobres
        - **Revisa mensualmente:** Ajusta presupuesto según resultados
        """)


if __name__ == "__main__":
    main()
