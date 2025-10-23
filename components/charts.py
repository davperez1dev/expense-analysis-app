"""
Charts: Componentes de gráficos con Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List
from utils.config_loader import ConfigLoader


class ChartBuilder:
    """Constructor de gráficos con Plotly"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader
        self.colores_grupos = {
            g['nombre']: g['color'] 
            for g in config_loader.get_grupos().values()
        }
        self.colores_subcategorias = config_loader.get_colores_subcategorias()
    
    def grafico_lineas_evolucion(self, df: pd.DataFrame, 
                                  fecha_col: str = 'Fecha',
                                  grupo_col: str = 'Grupo',
                                  monto_col: str = 'Monto',
                                  titulo: str = 'Evolución de Gastos por Grupo') -> go.Figure:
        """
        Gráfico de líneas: evolución mensual por grupo
        
        Args:
            df: DataFrame con datos
            fecha_col: Columna de fecha
            grupo_col: Columna de grupo
            monto_col: Columna de montos
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        # Agrupar por fecha y grupo
        df_agrupado = df.groupby([fecha_col, grupo_col])[monto_col].sum().reset_index()
        
        # Convertir a valores absolutos para mejor visualización (si son gastos negativos)
        df_agrupado[monto_col] = df_agrupado[monto_col].abs()
        
        # Crear gráfico
        fig = px.line(
            df_agrupado,
            x=fecha_col,
            y=monto_col,
            color=grupo_col,
            title=titulo,
            labels={
                fecha_col: 'Fecha',
                monto_col: 'Monto ($)',
                grupo_col: 'Grupo'
            },
            color_discrete_map=self.colores_grupos
        )
        
        fig.update_traces(mode='lines+markers')
        fig.update_layout(
            hovermode='x unified',
            template='plotly_dark',
            height=500
        )
        
        return fig
    
    def grafico_barras_apiladas(self, df: pd.DataFrame,
                                fecha_col: str = 'MesAño',
                                grupo_col: str = 'Grupo',
                                monto_col: str = 'Monto',
                                titulo: str = 'Distribución Mensual por Grupo') -> go.Figure:
        """
        Gráfico de barras apiladas: distribución por grupo
        
        Args:
            df: DataFrame con datos
            fecha_col: Columna de período
            grupo_col: Columna de grupo
            monto_col: Columna de montos
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        # Agrupar por fecha y grupo
        df_agrupado = df.groupby([fecha_col, grupo_col])[monto_col].sum().reset_index()
        
        # Convertir a valores absolutos para mejor visualización
        df_agrupado[monto_col] = df_agrupado[monto_col].abs()
        
        # Crear gráfico
        fig = px.bar(
            df_agrupado,
            x=fecha_col,
            y=monto_col,
            color=grupo_col,
            title=titulo,
            labels={
                fecha_col: 'Período',
                monto_col: 'Monto ($)',
                grupo_col: 'Grupo'
            },
            color_discrete_map=self.colores_grupos,
            barmode='stack'
        )
        
        fig.update_layout(
            template='plotly_dark',
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def grafico_dona(self, df: pd.DataFrame,
                     grupo_col: str = 'Grupo',
                     monto_col: str = 'Monto',
                     titulo: str = 'Participación por Grupo') -> go.Figure:
        """
        Gráfico circular (donut): participación de cada grupo
        
        Args:
            df: DataFrame con datos
            grupo_col: Columna de grupo
            monto_col: Columna de montos
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        # Agrupar por grupo y tomar valor absoluto
        df_agrupado = df.groupby(grupo_col)[monto_col].sum().abs().reset_index()
        df_agrupado = df_agrupado.sort_values(monto_col, ascending=False)
        
        # Elegir paleta de colores
        if grupo_col == 'Grupo':
            # Usar colores de grupos definidos en config
            colores = [self.colores_grupos.get(g, '#95A5A6') for g in df_agrupado[grupo_col]]
        else:
            # Para categorías, usar paleta automática de plotly
            colores = px.colors.qualitative.Set3[:len(df_agrupado)]
        
        # Crear gráfico de dona
        fig = go.Figure(data=[go.Pie(
            labels=df_agrupado[grupo_col],
            values=df_agrupado[monto_col],
            hole=0.4,
            marker=dict(colors=colores)
        )])
        
        fig.update_layout(
            title=titulo,
            template='plotly_dark',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def grafico_pareto(self, df: pd.DataFrame,
                       categoria_col: str = 'Categoria_Principal',
                       monto_col: str = 'Monto',
                       top_n: int = 10,
                       titulo: str = 'Top Categorías (Pareto)') -> go.Figure:
        """
        Gráfico de Pareto: categorías más costosas con línea acumulada
        
        Args:
            df: DataFrame con datos
            categoria_col: Columna de categoría
            monto_col: Columna de montos
            top_n: Número de categorías principales a mostrar
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        # Filtrar solo gastos (negativos) y tomar valor absoluto
        df_gastos = df[df[monto_col] < 0].copy()
        df_gastos[monto_col] = df_gastos[monto_col].abs()
        
        # Agrupar por categoría y ordenar
        df_agrupado = df_gastos.groupby(categoria_col)[monto_col].sum().reset_index()
        df_agrupado = df_agrupado.sort_values(monto_col, ascending=False).head(top_n)
        
        # Calcular porcentaje acumulado
        df_agrupado['Porcentaje'] = (df_agrupado[monto_col] / df_agrupado[monto_col].sum() * 100)
        df_agrupado['Porcentaje_Acum'] = df_agrupado['Porcentaje'].cumsum()
        
        # Crear figura con ejes secundarios
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Barras
        fig.add_trace(
            go.Bar(
                x=df_agrupado[categoria_col],
                y=df_agrupado[monto_col],
                name='Monto',
                marker_color='#4A90E2'
            ),
            secondary_y=False
        )
        
        # Línea acumulada
        fig.add_trace(
            go.Scatter(
                x=df_agrupado[categoria_col],
                y=df_agrupado['Porcentaje_Acum'],
                name='% Acumulado',
                mode='lines+markers',
                marker=dict(color='#E74C3C', size=8),
                line=dict(color='#E74C3C', width=2)
            ),
            secondary_y=True
        )
        
        # Actualizar layout
        fig.update_xaxes(title_text="Categoría", tickangle=-45)
        fig.update_yaxes(title_text="Monto ($)", secondary_y=False)
        fig.update_yaxes(title_text="Porcentaje Acumulado (%)", secondary_y=True, range=[0, 105])
        
        fig.update_layout(
            title=titulo,
            template='plotly_dark',
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def grafico_area_apilada(self, df: pd.DataFrame,
                             fecha_col: str = 'Fecha',
                             grupo_col: str = 'Grupo',
                             monto_col: str = 'Monto',
                             titulo: str = 'Composición de Gastos en el Tiempo') -> go.Figure:
        """
        Gráfico de área apilada: composición temporal
        
        Args:
            df: DataFrame con datos
            fecha_col: Columna de fecha
            grupo_col: Columna de grupo
            monto_col: Columna de montos
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        # Agrupar por fecha y grupo
        df_agrupado = df.groupby([fecha_col, grupo_col])[monto_col].sum().abs().reset_index()
        
        # Crear gráfico
        fig = px.area(
            df_agrupado,
            x=fecha_col,
            y=monto_col,
            color=grupo_col,
            title=titulo,
            labels={
                fecha_col: 'Fecha',
                monto_col: 'Monto ($)',
                grupo_col: 'Grupo'
            },
            color_discrete_map=self.colores_grupos
        )
        
        fig.update_layout(
            template='plotly_dark',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def grafico_waterfall(self, df: pd.DataFrame,
                         titulo: str = 'Flujo Financiero') -> go.Figure:
        """
        Gráfico de cascada: Ingresos → Gastos → Ganancia Neta
        
        Args:
            df: DataFrame con datos agregados (debe tener totales)
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        # Calcular totales
        total_ingresos = df[df['Monto'] > 0]['Monto'].sum()
        total_gastos = df[df['Monto'] < 0]['Monto'].sum()
        ganancia_neta = total_ingresos + total_gastos
        
        # Crear gráfico waterfall
        fig = go.Figure(go.Waterfall(
            name="Flujo",
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Ingresos", "Gastos", "Ganancia Neta"],
            textposition="outside",
            text=[f"${total_ingresos:,.0f}", 
                  f"${total_gastos:,.0f}", 
                  f"${ganancia_neta:,.0f}"],
            y=[total_ingresos, total_gastos, 0],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#27AE60"}},
            decreasing={"marker": {"color": "#E74C3C"}},
            totals={"marker": {"color": "#4A90E2"}}
        ))
        
        fig.update_layout(
            title=titulo,
            template='plotly_dark',
            height=500,
            showlegend=False
        )
        
        return fig
    
    def grafico_heatmap(self, df: pd.DataFrame,
                       categoria_col: str = 'Categoria_Principal',
                       fecha_col: str = 'MesAño',
                       monto_col: str = 'Monto',
                       titulo: str = 'Mapa de Calor: Gastos por Categoría y Período') -> go.Figure:
        """
        Heatmap: intensidad de gastos por categoría y período
        
        Args:
            df: DataFrame con datos
            categoria_col: Columna de categoría
            fecha_col: Columna de período
            monto_col: Columna de montos
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        # Crear pivot table
        pivot = pd.pivot_table(
            df,
            index=categoria_col,
            columns=fecha_col,
            values=monto_col,
            aggfunc='sum',
            fill_value=0
        )
        
        # Tomar valor absoluto para gastos
        pivot = pivot.abs()
        
        # Crear heatmap
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale='Reds',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=titulo,
            template='plotly_dark',
            height=max(500, len(pivot) * 30),
            xaxis_tickangle=-45
        )
        
        return fig
