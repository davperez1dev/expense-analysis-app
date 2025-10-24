"""
🎯 Sistema de Cálculo de Presupuesto Inteligente
=================================================
Metodologías implementadas:
1. Promedio Móvil (3, 6, 12 meses)
2. Percentil 75 (para gastos variables)
3. Análisis de Tendencia (regresión lineal)
4. Regla 50/30/20 (necesidades/gustos/ahorros)
5. Método de Sobres (Envelope Budgeting)
6. Zero-Based Budgeting adaptado
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from scipy import stats


class BudgetCalculator:
    """Calculadora de presupuestos basada en datos históricos"""
    
    def __init__(self, df_timeline: pd.DataFrame):
        """
        Inicializa la calculadora con datos históricos
        
        Args:
            df_timeline: DataFrame con columnas de fechas y categorías en filas
        """
        self.df = df_timeline.copy()
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepara y limpia los datos para análisis"""
        # Convertir valores string con formato argentino a float
        for col in self.df.columns[1:]:  # Skip primera columna (nombres)
            if col != 'Categorías':
                self.df[col] = self.df[col].apply(self._parse_amount)
    
    def _parse_amount(self, value) -> float:
        """Convierte strings con formato argentino a float"""
        if isinstance(value, str):
            # Eliminar comillas, espacios y convertir
            value = value.strip('"').replace('.', '').replace(',', '.')
            try:
                return float(value)
            except:
                return 0.0
        return float(value) if value else 0.0
    
    def calculate_moving_average(
        self, 
        category: str, 
        months: int = 3
    ) -> float:
        """
        📊 MÉTODO 1: Promedio Móvil
        Suaviza fluctuaciones y muestra tendencia reciente
        
        Args:
            category: Nombre de la categoría
            months: Número de meses a promediar (3, 6, o 12)
        
        Returns:
            Promedio de los últimos N meses
        """
        if category not in self.df['Categorías'].values:
            return 0.0
        
        row = self.df[self.df['Categorías'] == category]
        values = row.iloc[0, -months:].values.astype(float)
        values = np.abs(values)  # Convertir a positivo
        
        return np.mean(values[values > 0]) if len(values[values > 0]) > 0 else 0.0
    
    def calculate_percentile(
        self, 
        category: str, 
        percentile: int = 75
    ) -> float:
        """
        📈 MÉTODO 2: Percentil
        Ideal para gastos variables - evita subestimar
        
        Args:
            category: Nombre de la categoría
            percentile: Percentil a calcular (75 recomendado)
        
        Returns:
            Valor del percentil especificado
        """
        if category not in self.df['Categorías'].values:
            return 0.0
        
        row = self.df[self.df['Categorías'] == category]
        values = row.iloc[0, 1:].values.astype(float)
        values = np.abs(values[values != 0])
        
        if len(values) == 0:
            return 0.0
        
        return np.percentile(values, percentile)
    
    def calculate_trend_forecast(
        self, 
        category: str, 
        forecast_months: int = 1
    ) -> float:
        """
        📉 MÉTODO 3: Análisis de Tendencia
        Usa regresión lineal para predecir gasto futuro
        
        Args:
            category: Nombre de la categoría
            forecast_months: Meses hacia adelante a predecir
        
        Returns:
            Predicción basada en tendencia histórica
        """
        if category not in self.df['Categorías'].values:
            return 0.0
        
        row = self.df[self.df['Categorías'] == category]
        values = row.iloc[0, 1:].values.astype(float)
        values = np.abs(values)
        
        # Filtrar valores no-zero
        non_zero_indices = np.where(values > 0)[0]
        if len(non_zero_indices) < 3:  # Necesitamos al menos 3 puntos
            return self.calculate_moving_average(category, 3)
        
        non_zero_values = values[non_zero_indices]
        
        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            non_zero_indices, non_zero_values
        )
        
        # Predicción
        next_index = len(values) + forecast_months - 1
        prediction = slope * next_index + intercept
        
        return max(prediction, 0)  # No puede ser negativo
    
    def get_category_volatility(self, category: str) -> str:
        """
        📊 Determina la volatilidad de una categoría
        
        Returns:
            'BAJA', 'MEDIA', 'ALTA'
        """
        if category not in self.df['Categorías'].values:
            return 'DESCONOCIDA'
        
        row = self.df[self.df['Categorías'] == category]
        values = row.iloc[0, -6:].values.astype(float)  # Últimos 6 meses
        values = np.abs(values[values != 0])
        
        if len(values) < 2:
            return 'DESCONOCIDA'
        
        mean = np.mean(values)
        std = np.std(values)
        cv = (std / mean) * 100 if mean > 0 else 0  # Coeficiente de variación
        
        if cv < 15:
            return 'BAJA'
        elif cv < 40:
            return 'MEDIA'
        else:
            return 'ALTA'
    
    def suggest_budget(
        self, 
        category: str,
        method: str = 'auto'
    ) -> Dict[str, any]:
        """
        🎯 MÉTODO PRINCIPAL: Sugiere presupuesto óptimo
        
        Args:
            category: Nombre de la categoría
            method: 'auto', 'conservative', 'moderate', 'aggressive'
        
        Returns:
            Dict con presupuesto sugerido y metadata
        """
        if category not in self.df['Categorías'].values:
            return {
                'sugerido': 0,
                'minimo': 0,
                'maximo': 0,
                'metodo': 'N/A',
                'volatilidad': 'DESCONOCIDA',
                'confianza': 0
            }
        
        # Calcular con diferentes métodos
        ma_3 = self.calculate_moving_average(category, 3)
        ma_6 = self.calculate_moving_average(category, 6)
        p75 = self.calculate_percentile(category, 75)
        p90 = self.calculate_percentile(category, 90)
        trend = self.calculate_trend_forecast(category, 1)
        
        volatility = self.get_category_volatility(category)
        
        # Estrategia según volatilidad y método
        if method == 'auto':
            if volatility == 'BAJA':
                # Para gastos estables: promedio reciente
                suggested = ma_3
                confidence = 85
            elif volatility == 'MEDIA':
                # Para gastos moderados: percentil 75
                suggested = p75
                confidence = 70
            else:  # ALTA
                # Para gastos volátiles: percentil 90
                suggested = p90
                confidence = 60
        
        elif method == 'conservative':
            # Método conservador: siempre usar percentil 90
            suggested = p90
            confidence = 90
        
        elif method == 'moderate':
            # Método moderado: promedio ponderado
            suggested = (ma_3 * 0.4 + ma_6 * 0.3 + p75 * 0.3)
            confidence = 75
        
        else:  # aggressive
            # Método agresivo: usar mínimos
            suggested = ma_3
            confidence = 50
        
        # Calcular rangos
        minimum = ma_3 * 0.8  # 20% menos que promedio reciente
        maximum = p90 * 1.1   # 10% más que percentil 90
        
        return {
            'sugerido': round(suggested, 2),
            'minimo': round(minimum, 2),
            'maximo': round(maximum, 2),
            'promedio_3m': round(ma_3, 2),
            'promedio_6m': round(ma_6, 2),
            'percentil_75': round(p75, 2),
            'percentil_90': round(p90, 2),
            'tendencia': round(trend, 2),
            'metodo': method,
            'volatilidad': volatility,
            'confianza': confidence
        }
    
    def get_all_budgets(
        self, 
        method: str = 'auto',
        exclude_categories: List[str] = None
    ) -> pd.DataFrame:
        """
        📋 Genera presupuestos para todas las categorías
        
        Args:
            method: Método de cálculo
            exclude_categories: Lista de categorías a excluir
        
        Returns:
            DataFrame con presupuestos sugeridos
        """
        if exclude_categories is None:
            exclude_categories = [
                'Gastos', 'Ingresos', 'Ganancia Neta',
                'Inversiones', 'Préstamos', 'TrabajoClientes'
            ]
        
        budgets = []
        
        for category in self.df['Categorías']:
            # Skip categorías excluidas y categorías padre
            if category in exclude_categories or category.startswith(('B-', 'D-', 'N-', 'O-', 'R-')):
                continue
            
            budget = self.suggest_budget(category, method)
            budget['categoria'] = category
            budgets.append(budget)
        
        df_budgets = pd.DataFrame(budgets)
        
        # Ordenar por gasto sugerido (mayor a menor)
        df_budgets = df_budgets.sort_values('sugerido', ascending=False)
        
        return df_budgets
    
    def analyze_spending_pattern(self, category: str) -> Dict[str, any]:
        """
        🔍 Analiza patrones de gasto de una categoría
        
        Returns:
            Análisis detallado con insights
        """
        if category not in self.df['Categorías'].values:
            return {}
        
        row = self.df[self.df['Categorías'] == category]
        values = row.iloc[0, 1:].values.astype(float)
        values = np.abs(values)
        
        # Estadísticas básicas
        non_zero = values[values > 0]
        
        if len(non_zero) == 0:
            return {'error': 'No hay datos disponibles'}
        
        # Detectar estacionalidad (comparar meses similares)
        months_count = len(values)
        
        analysis = {
            'total_gastado': round(np.sum(values), 2),
            'promedio_mensual': round(np.mean(non_zero), 2),
            'mediana': round(np.median(non_zero), 2),
            'desviacion_std': round(np.std(non_zero), 2),
            'gasto_minimo': round(np.min(non_zero), 2),
            'gasto_maximo': round(np.max(non_zero), 2),
            'meses_con_gasto': len(non_zero),
            'meses_sin_gasto': np.sum(values == 0),
            'frecuencia': round((len(non_zero) / months_count) * 100, 1)
        }
        
        # Tendencia
        if len(non_zero) >= 3:
            recent_avg = np.mean(values[-3:][values[-3:] > 0])
            old_avg = np.mean(values[:3][values[:3] > 0])
            
            if recent_avg > old_avg * 1.15:
                analysis['tendencia'] = 'CRECIENTE'
            elif recent_avg < old_avg * 0.85:
                analysis['tendencia'] = 'DECRECIENTE'
            else:
                analysis['tendencia'] = 'ESTABLE'
        else:
            analysis['tendencia'] = 'INSUFICIENTES DATOS'
        
        return analysis


def load_calculator(csv_path: str = 'data/categories_timeline.csv') -> BudgetCalculator:
    """
    Helper function para cargar el calculador
    
    Args:
        csv_path: Ruta al archivo CSV
    
    Returns:
        Instancia de BudgetCalculator
    """
    df = pd.read_csv(csv_path)
    return BudgetCalculator(df)


# ============================================================================
# 📚 MEJORES PRÁCTICAS Y METODOLOGÍAS
# ============================================================================

BUDGET_METHODOLOGIES = {
    "50/30/20": {
        "descripcion": "Regla clásica de budgeting",
        "distribucion": {
            "Necesidades": 50,  # Vivienda, salud, alimentación, transporte
            "Gustos": 30,       # Entretenimiento, hobbies, comer fuera
            "Ahorros": 20       # Inversiones, emergencias, metas
        },
        "recomendado_para": "Perfiles con ingresos estables"
    },
    
    "Envelope_System": {
        "descripcion": "Sistema de sobres - asignar dinero específico a cada categoría",
        "ventajas": [
            "Control total del gasto",
            "Previene gasto excesivo",
            "Fácil de visualizar"
        ],
        "implementacion": "Crear 'sobres virtuales' con límites estrictos"
    },
    
    "Zero_Based": {
        "descripcion": "Presupuesto base cero - cada peso tiene un propósito",
        "proceso": [
            "1. Calcular ingresos totales",
            "2. Asignar cada peso a una categoría",
            "3. Ingresos - Gastos = 0 (todo asignado)"
        ],
        "recomendado_para": "Perfiles que quieren control máximo"
    },
    
    "Pay_Yourself_First": {
        "descripcion": "Pagar primero tus ahorros/inversiones",
        "orden": [
            "1. Recibir ingreso",
            "2. Transferir % a ahorros/inversiones",
            "3. Vivir con el resto"
        ],
        "porcentaje_recomendado": "20-30% de ingresos"
    },
    
    "Percentile_Method": {
        "descripcion": "Usar percentiles para presupuestos variables",
        "guia": {
            "Percentil 50 (Mediana)": "Para gastos muy estables",
            "Percentil 75": "Para gastos moderadamente variables (RECOMENDADO)",
            "Percentil 90": "Para gastos muy variables o importantes"
        }
    }
}


def get_methodology_recommendation(income_stability: str, control_level: str) -> str:
    """
    Recomienda metodología según perfil del usuario
    
    Args:
        income_stability: 'ESTABLE', 'VARIABLE', 'IRREGULAR'
        control_level: 'ALTO', 'MEDIO', 'BAJO'
    
    Returns:
        Nombre de metodología recomendada
    """
    if income_stability == 'ESTABLE':
        if control_level == 'ALTO':
            return 'Zero_Based'
        elif control_level == 'MEDIO':
            return '50/30/20'
        else:
            return 'Pay_Yourself_First'
    
    elif income_stability == 'VARIABLE':
        if control_level == 'ALTO':
            return 'Envelope_System'
        else:
            return 'Percentile_Method'
    
    else:  # IRREGULAR
        return 'Percentile_Method'
