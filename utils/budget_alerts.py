"""
⚠️ Sistema de Alertas de Presupuesto
=====================================
Monitorea gastos en tiempo real y genera alertas inteligentes
"""

import streamlit as st
from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd


class BudgetAlert:
    """Sistema de alertas de presupuesto"""
    
    # Niveles de alerta
    SAFE = "SAFE"          # 0-70% del presupuesto
    WARNING = "WARNING"    # 70-90% del presupuesto
    DANGER = "DANGER"      # 90-100% del presupuesto
    EXCEEDED = "EXCEEDED"  # >100% del presupuesto
    
    def __init__(self):
        """Inicializa el sistema de alertas"""
        self.thresholds = {
            self.SAFE: 70,
            self.WARNING: 90,
            self.DANGER: 100
        }
    
    def calculate_usage_percentage(
        self, 
        spent: float, 
        budget: float
    ) -> float:
        """
        Calcula porcentaje de uso del presupuesto
        
        Args:
            spent: Monto gastado
            budget: Presupuesto asignado
        
        Returns:
            Porcentaje de uso (0-100+)
        """
        if budget <= 0:
            return 0.0
        
        return (abs(spent) / budget) * 100
    
    def get_alert_level(
        self, 
        spent: float, 
        budget: float
    ) -> str:
        """
        Determina nivel de alerta
        
        Args:
            spent: Monto gastado
            budget: Presupuesto asignado
        
        Returns:
            Nivel de alerta (SAFE, WARNING, DANGER, EXCEEDED)
        """
        percentage = self.calculate_usage_percentage(spent, budget)
        
        if percentage >= 100:
            return self.EXCEEDED
        elif percentage >= self.thresholds[self.DANGER]:
            return self.DANGER
        elif percentage >= self.thresholds[self.WARNING]:
            return self.WARNING
        else:
            return self.SAFE
    
    def get_alert_color(self, level: str) -> str:
        """Retorna color según nivel de alerta"""
        colors = {
            self.SAFE: "#28a745",      # Verde
            self.WARNING: "#ffc107",   # Amarillo
            self.DANGER: "#fd7e14",    # Naranja
            self.EXCEEDED: "#dc3545"   # Rojo
        }
        return colors.get(level, "#6c757d")
    
    def get_alert_icon(self, level: str) -> str:
        """Retorna emoji según nivel de alerta"""
        icons = {
            self.SAFE: "✅",
            self.WARNING: "⚠️",
            self.DANGER: "🚨",
            self.EXCEEDED: "❌"
        }
        return icons.get(level, "ℹ️")
    
    def get_alert_message(
        self, 
        level: str, 
        category: str,
        spent: float,
        budget: float,
        percentage: float
    ) -> str:
        """
        Genera mensaje de alerta personalizado
        
        Args:
            level: Nivel de alerta
            category: Nombre de categoría
            spent: Monto gastado
            budget: Presupuesto
            percentage: Porcentaje usado
        
        Returns:
            Mensaje de alerta
        """
        remaining = budget - abs(spent)
        
        messages = {
            self.SAFE: f"✅ **{category}**: Todo bajo control. Gastaste ${abs(spent):,.2f} de ${budget:,.2f} ({percentage:.1f}%). Quedan ${remaining:,.2f}.",
            
            self.WARNING: f"⚠️ **{category}**: Te estás acercando al límite. Gastaste ${abs(spent):,.2f} de ${budget:,.2f} ({percentage:.1f}%). Quedan solo ${remaining:,.2f}.",
            
            self.DANGER: f"🚨 **{category}**: ¡Cuidado! Casi alcanzaste tu presupuesto. Gastaste ${abs(spent):,.2f} de ${budget:,.2f} ({percentage:.1f}%). Quedan ${remaining:,.2f}.",
            
            self.EXCEEDED: f"❌ **{category}**: ¡Presupuesto excedido! Gastaste ${abs(spent):,.2f} cuando tu presupuesto era ${budget:,.2f} ({percentage:.1f}%). Te excediste en ${abs(remaining):,.2f}."
        }
        
        return messages.get(level, "")
    
    def create_progress_bar(
        self, 
        percentage: float,
        level: str
    ) -> str:
        """
        Crea barra de progreso HTML
        
        Args:
            percentage: Porcentaje de uso
            level: Nivel de alerta
        
        Returns:
            HTML de barra de progreso
        """
        color = self.get_alert_color(level)
        percentage_capped = min(percentage, 100)
        
        html = f"""
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
                width: {percentage_capped}%;
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
        """
        
        return html
    
    def display_alert_card(
        self,
        category: str,
        spent: float,
        budget: float
    ):
        """
        Muestra tarjeta de alerta en Streamlit
        
        Args:
            category: Nombre de categoría
            spent: Monto gastado
            budget: Presupuesto asignado
        """
        percentage = self.calculate_usage_percentage(spent, budget)
        level = self.get_alert_level(spent, budget)
        color = self.get_alert_color(level)
        icon = self.get_alert_icon(level)
        message = self.get_alert_message(level, category, spent, budget, percentage)
        
        # Tarjeta con estilo
        st.markdown(f"""
        <div style="
            border-left: 5px solid {color};
            background-color: {color}15;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        ">
            <div style="font-size: 16px; margin-bottom: 10px;">
                {icon} <strong>{category}</strong>
            </div>
            <div style="margin-bottom: 10px;">
                {self.create_progress_bar(percentage, level)}
            </div>
            <div style="color: #555; font-size: 14px;">
                Gastado: <strong>${abs(spent):,.2f}</strong> / 
                Presupuesto: <strong>${budget:,.2f}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def get_summary_metrics(
        self,
        budgets: Dict[str, float],
        expenses: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Genera métricas resumen de todos los presupuestos
        
        Args:
            budgets: Dict {categoria: presupuesto}
            expenses: Dict {categoria: gasto_actual}
        
        Returns:
            Métricas agregadas
        """
        total_budget = sum(budgets.values())
        total_spent = sum(abs(expenses.get(cat, 0)) for cat in budgets.keys())
        
        alerts_count = {
            self.SAFE: 0,
            self.WARNING: 0,
            self.DANGER: 0,
            self.EXCEEDED: 0
        }
        
        for category, budget in budgets.items():
            spent = expenses.get(category, 0)
            level = self.get_alert_level(spent, budget)
            alerts_count[level] += 1
        
        return {
            'total_presupuesto': total_budget,
            'total_gastado': total_spent,
            'porcentaje_total': (total_spent / total_budget * 100) if total_budget > 0 else 0,
            'categorias_safe': alerts_count[self.SAFE],
            'categorias_warning': alerts_count[self.WARNING],
            'categorias_danger': alerts_count[self.DANGER],
            'categorias_exceeded': alerts_count[self.EXCEEDED],
            'total_categorias': len(budgets)
        }
    
    def display_summary_dashboard(
        self,
        budgets: Dict[str, float],
        expenses: Dict[str, float]
    ):
        """
        Muestra dashboard resumen de alertas
        
        Args:
            budgets: Dict {categoria: presupuesto}
            expenses: Dict {categoria: gasto_actual}
        """
        metrics = self.get_summary_metrics(budgets, expenses)
        
        # Título
        st.markdown("### 📊 Resumen de Presupuestos")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Presupuesto Total",
                f"${metrics['total_presupuesto']:,.0f}",
                help="Suma de todos los presupuestos asignados"
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
        
        # Alertas por categoría
        st.markdown("#### 🚦 Estado de Categorías")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background-color: #28a74520; border-radius: 8px;">
                <div style="font-size: 24px;">✅</div>
                <div style="font-weight: bold; font-size: 20px;">{metrics['categorias_safe']}</div>
                <div style="font-size: 12px; color: #666;">En control</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background-color: #ffc10720; border-radius: 8px;">
                <div style="font-size: 24px;">⚠️</div>
                <div style="font-weight: bold; font-size: 20px;">{metrics['categorias_warning']}</div>
                <div style="font-size: 12px; color: #666;">Atención</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background-color: #fd7e1420; border-radius: 8px;">
                <div style="font-size: 24px;">🚨</div>
                <div style="font-weight: bold; font-size: 20px;">{metrics['categorias_danger']}</div>
                <div style="font-size: 12px; color: #666;">Peligro</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background-color: #dc354520; border-radius: 8px;">
                <div style="font-size: 24px;">❌</div>
                <div style="font-weight: bold; font-size: 20px;">{metrics['categorias_exceeded']}</div>
                <div style="font-size: 12px; color: #666;">Excedido</div>
            </div>
            """, unsafe_allow_html=True)


def create_budget_comparison_chart(
    categories: List[str],
    budgets: List[float],
    spent: List[float]
) -> pd.DataFrame:
    """
    Crea DataFrame para gráfico de comparación
    
    Args:
        categories: Lista de nombres de categorías
        budgets: Lista de presupuestos
        spent: Lista de gastos actuales
    
    Returns:
        DataFrame con datos para gráfico
    """
    df = pd.DataFrame({
        'Categoría': categories,
        'Presupuesto': budgets,
        'Gastado': [abs(s) for s in spent],
        'Disponible': [b - abs(s) for b, s in zip(budgets, spent)]
    })
    
    # Calcular porcentajes
    df['% Usado'] = (df['Gastado'] / df['Presupuesto'] * 100).round(1)
    
    return df
