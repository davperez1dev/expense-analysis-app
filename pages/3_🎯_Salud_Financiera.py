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
from utils.budget_calculator import BudgetCalculator, load_calculator
from utils.budget_alerts import BudgetAlert

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
    
    # --- NUEVA SECCIÓN: Presupuestos sugeridos
    st.markdown("---")
    st.subheader("💰 Presupuestos sugeridos")
    try:
        # Cargar calculador (usando timeline ya en data)
        calculator = load_calculator('data/categories_timeline.csv')
        alert_system = BudgetAlert()

        categorias_principales = [
            'Combustible',
            'Ocio/Comer Fuera',
            'Comidas Varias',
            'Medicina Prepaga',
            'Servicios',
            'Aseo/Cosmeticos',
            'Actividad Física y Bienestar',
            'Cursos'
        ]

        metodo_calculo = st.selectbox('Método de cálculo', ['auto', 'conservative', 'moderate', 'aggressive'], index=0)
        mostrar_detalles = st.checkbox('Mostrar detalles por categoría', value=False)

        # Calcular presupuestos y gastos actuales
        presupuestos = calculator.get_all_budgets(categorias_principales, method=metodo_calculo)
        gastos_actuales = {}
        for c in categorias_principales:
            gastos_actuales[c] = df_filtrado[(df_filtrado['Categorías'] == c) & (df_filtrado['Monto'] < 0)]['Monto'].sum()

        # Resumen
        metrics = alert_system.get_summary_metrics(presupuestos, gastos_actuales)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric('💰 Presupuesto total', f"${metrics['total_presupuesto']:,.0f}")
        with col2:
            st.metric('💸 Gastado', f"${metrics['total_gastado']:,.0f}")
        with col3:
            st.metric('💵 Disponible', f"${metrics['total_presupuesto'] - metrics['total_gastado']:,.0f}")
        with col4:
            st.metric('📈 Uso promedio', f"{metrics['porcentaje_total']:.1f}%")

        st.markdown('#### Alertas por categoría')
        for c in categorias_principales:
            bud = presupuestos.get(c, 0)
            spent = gastos_actuales.get(c, 0)
            if bud <= 0:
                continue
            lvl = alert_system.get_alert_level(spent, bud)
            color = alert_system.get_alert_color(lvl)
            icon = alert_system.get_alert_icon(lvl)
            pct = alert_system.calculate_usage_percentage(spent, bud)

            st.markdown(f"<div style='border-left:4px solid {color}; padding:10px; border-radius:6px; margin:6px 0;'>\n<strong>{icon} {c}</strong> — Gastado: ${abs(spent):,.0f} / Presupuesto: ${bud:,.0f} ({pct:.1f}%)\n</div>", unsafe_allow_html=True)

            if mostrar_detalles:
                info = calculator.suggest_budget(c, method=metodo_calculo)
                analysis = calculator.suggest_budget(c, method=metodo_calculo)  # re-use for now
                with st.expander(f'Detalles: {c}'):
                    st.write(info)

    except Exception as e:
        st.warning(f'No se pudo calcular presupuestos: {e}')

    # Agregar recomendaciones generales
    st.markdown("---")
    
    # NUEVA SECCIÓN: Sistema de Presupuestos
    st.header("💰 Control de Presupuestos")
    
    # Cargar calculador de presupuestos
    try:
        calculator = BudgetCalculator(pd.read_csv('data/categories_timeline.csv'))
        alert_system = BudgetAlert()
        
        # Selector de método de cálculo
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("### 🎯 Presupuestos Sugeridos por Categoría")
        
        with col2:
            metodo_calculo = st.selectbox(
                "Método de cálculo",
                ['auto', 'conservative', 'moderate', 'aggressive'],
                index=0,
                help="Auto: Selecciona automáticamente según volatilidad"
            )
        
        with col3:
            mostrar_detalles = st.checkbox("Mostrar detalles", value=False)
        
        # Obtener presupuestos para categorías principales
        categorias_principales = [
            'Combustible',
            'Ocio/Comer Fuera',
            'Comidas Varias',
            'Medicina Prepaga',
            'Servicios',
            'Aseo/Cosmeticos',
            'Actividad Física y Bienestar',
            'Cursos'
        ]
        
        # Calcular gastos actuales del período filtrado
        gastos_actuales = {}
        for categoria in categorias_principales:
            gasto = df_filtrado[
                (df_filtrado['Categorías'] == categoria) & 
                (df_filtrado['Monto'] < 0)
            ]['Monto'].sum()
            gastos_actuales[categoria] = gasto
        
        # Calcular presupuestos sugeridos
        presupuestos = {}
        for categoria in categorias_principales:
            budget_info = calculator.suggest_budget(categoria, method=metodo_calculo)
            presupuestos[categoria] = budget_info['sugerido']
        
        # Mostrar dashboard de alertas
        st.markdown("#### 🚦 Estado de Presupuestos")
        
        # Métricas resumen
        metrics = alert_system.get_summary_metrics(presupuestos, gastos_actuales)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Presupuesto Total",
                f"${metrics['total_presupuesto']:,.0f}",
                help="Suma de todos los presupuestos sugeridos"
            )
        
        with col2:
            st.metric(
                "💸 Gastado",
                f"${metrics['total_gastado']:,.0f}",
                delta=f"-{metrics['porcentaje_total']:.1f}%",
                delta_color="inverse",
                help="Total gastado en el período"
            )
        
        with col3:
            remaining = metrics['total_presupuesto'] - metrics['total_gastado']
            st.metric(
                "💵 Disponible",
                f"${remaining:,.0f}",
                help="Presupuesto restante"
            )
        
        with col4:
            st.metric(
                "📈 Uso Promedio",
                f"{metrics['porcentaje_total']:.1f}%",
                help="Porcentaje promedio de uso"
            )
        
        # Estado por categoría
        st.markdown("#### 🏷️ Alertas por Categoría")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background-color: #28a74520; border-radius: 8px;">
                <div style="font-size: 28px;">✅</div>
                <div style="font-weight: bold; font-size: 24px;">{metrics['categorias_safe']}</div>
                <div style="font-size: 12px; color: #aaa;">En control</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background-color: #ffc10720; border-radius: 8px;">
                <div style="font-size: 28px;">⚠️</div>
                <div style="font-weight: bold; font-size: 24px;">{metrics['categorias_warning']}</div>
                <div style="font-size: 12px; color: #aaa;">Atención</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background-color: #fd7e1420; border-radius: 8px;">
                <div style="font-size: 28px;">🚨</div>
                <div style="font-weight: bold; font-size: 24px;">{metrics['categorias_danger']}</div>
                <div style="font-size: 12px; color: #aaa;">Peligro</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background-color: #dc354520; border-radius: 8px;">
                <div style="font-size: 28px;">❌</div>
                <div style="font-weight: bold; font-size: 24px;">{metrics['categorias_exceeded']}</div>
                <div style="font-size: 12px; color: #aaa;">Excedido</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mostrar alertas individuales por categoría
        for categoria in categorias_principales:
            budget = presupuestos.get(categoria, 0)
            spent = gastos_actuales.get(categoria, 0)
            
            if budget > 0:  # Solo mostrar si hay presupuesto
                percentage = alert_system.calculate_usage_percentage(spent, budget)
                level = alert_system.get_alert_level(spent, budget)
                color = alert_system.get_alert_color(level)
                icon = alert_system.get_alert_icon(level)
                
                # Crear tarjeta de alerta
                st.markdown(f"""
                <div style="
                    border-left: 5px solid {color};
                    background-color: {color}15;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                ">
                    <div style="font-size: 16px; margin-bottom: 10px;">
                        {icon} <strong>{categoria}</strong>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <div style="
                            width: 100%;
                            background-color: #e9ecef;
                            border-radius: 10px;
                            height: 25px;
                            position: relative;
                            overflow: hidden;
                            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
                        ">
                            <div style="
                                width: {min(percentage, 100)}%;
                                background-color: {color};
                                height: 100%;
                                border-radius: 10px;
                                transition: width 0.3s ease;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            ">
                                <span style="
                                    color: white;
                                    font-weight: bold;
                                    font-size: 12px;
                                    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                                ">
                                    {percentage:.1f}%
                                </span>
                            </div>
                        </div>
                    </div>
                    <div style="color: #555; font-size: 14px;">
                        Gastado: <strong>${abs(spent):,.0f}</strong> / 
                        Presupuesto: <strong>${budget:,.0f}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar detalles si está activado
                if mostrar_detalles:
                    budget_info = calculator.suggest_budget(categoria, method=metodo_calculo)
                    analysis = calculator.analyze_spending_pattern(categoria)
                    
                    with st.expander(f"📊 Detalles de {categoria}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📈 Análisis Estadístico**")
                            st.write(f"- Promedio 3 meses: ${budget_info['promedio_3m']:,.0f}")
                            st.write(f"- Promedio 6 meses: ${budget_info['promedio_6m']:,.0f}")
                            st.write(f"- Percentil 75: ${budget_info['percentil_75']:,.0f}")
                            st.write(f"- Percentil 90: ${budget_info['percentil_90']:,.0f}")
                            st.write(f"- Volatilidad: {budget_info['volatilidad']}")
                            st.write(f"- Confianza: {budget_info['confianza']}%")
                        
                        with col2:
                            st.markdown("**🔍 Patrón de Gastos**")
                            if 'promedio_mensual' in analysis:
                                st.write(f"- Promedio mensual: ${analysis['promedio_mensual']:,.0f}")
                                st.write(f"- Rango: ${analysis['gasto_minimo']:,.0f} - ${analysis['gasto_maximo']:,.0f}")
                                st.write(f"- Tendencia: {analysis['tendencia']}")
                                st.write(f"- Frecuencia: {analysis['frecuencia']}%")
        
        # Información sobre metodología
        with st.expander("ℹ️ ¿Cómo se calculan estos presupuestos?"):
            st.markdown("""
            ### 📊 Metodología de Cálculo
            
            El sistema analiza tu historial de gastos (últimos 22 meses) y utiliza diferentes métodos según la volatilidad de cada categoría:
            
            #### 🎯 Métodos Disponibles:
            
            **AUTO (Recomendado):**
            - Gastos estables (CV < 15%): Usa promedio de 3 meses
            - Gastos moderados (CV 15-40%): Usa Percentil 75 ⭐
            - Gastos volátiles (CV > 40%): Usa Percentil 90
            
            **CONSERVATIVE:**
            - Siempre usa Percentil 90 (máxima protección)
            
            **MODERATE:**
            - Promedio ponderado entre múltiples métricas
            
            **AGGRESSIVE:**
            - Usa promedio de 3 meses (presupuesto más ajustado)
            
            #### 🚦 Niveles de Alerta:
            - ✅ **Verde (0-70%)**: Todo bajo control
            - ⚠️ **Amarillo (70-90%)**: Atención, reduce gastos
            - 🚨 **Naranja (90-100%)**: Peligro, detén gastos
            - ❌ **Rojo (>100%)**: Presupuesto excedido
            
            **Coeficiente de Variación (CV)** = Desviación Estándar / Promedio × 100
            """)
    
    except Exception as e:
        st.warning(f"⚠️ No se pudo cargar el sistema de presupuestos: {str(e)}")
        st.info("Asegúrate de tener el archivo 'data/categories_timeline.csv' disponible")
    
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
