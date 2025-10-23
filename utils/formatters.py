"""
Formatters: Utilidades para formatear montos, fechas y otros datos
"""
from typing import Union, Optional
import pandas as pd
from utils.config_loader import ConfigLoader


class CurrencyFormatter:
    """Formateador de moneda según configuración"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader.get_formato_moneda()
        self.simbolo = self.config.get('simbolo', '$')
        self.sep_miles = self.config.get('separador_miles', ',')
        self.sep_decimal = self.config.get('separador_decimal', '.')
        self.decimales = self.config.get('decimales', 2)
        self.posicion = self.config.get('posicion_simbolo', 'antes')
    
    def formatear(self, monto: Union[float, int], 
                  incluir_signo: bool = True,
                  color: bool = False) -> str:
        """
        Formatea un monto con el formato de moneda configurado
        
        Args:
            monto: Cantidad a formatear
            incluir_signo: Si incluir el signo + o -
            color: Si retornar con formato de color HTML
        
        Returns:
            String formateado
        """
        if pd.isna(monto):
            return '-'
        
        # Determinar signo
        signo = ''
        if incluir_signo and monto != 0:
            signo = '+' if monto > 0 else '-'
        
        # Valor absoluto
        valor_abs = abs(monto)
        
        # Formatear con separadores
        if self.decimales > 0:
            formato = f'{{:,.{self.decimales}f}}'
        else:
            formato = '{:,.0f}'
        
        valor_formateado = formato.format(valor_abs)
        
        # Reemplazar separadores según configuración
        if self.sep_miles != ',':
            valor_formateado = valor_formateado.replace(',', 'TEMP')
            valor_formateado = valor_formateado.replace('.', self.sep_decimal)
            valor_formateado = valor_formateado.replace('TEMP', self.sep_miles)
        elif self.sep_decimal != '.':
            valor_formateado = valor_formateado.replace('.', self.sep_decimal)
        
        # Posicionar símbolo
        if self.posicion == 'antes':
            resultado = f"{signo}{self.simbolo}{valor_formateado}"
        else:
            resultado = f"{signo}{valor_formateado}{self.simbolo}"
        
        # Aplicar color si se solicita
        if color:
            if monto > 0:
                resultado = f'<span style="color: #27AE60">{resultado}</span>'
            elif monto < 0:
                resultado = f'<span style="color: #E74C3C">{resultado}</span>'
        
        return resultado
    
    def formatear_serie(self, serie: pd.Series, **kwargs) -> pd.Series:
        """Formatea una serie completa de montos"""
        return serie.apply(lambda x: self.formatear(x, **kwargs))


class DateFormatter:
    """Formateador de fechas"""
    
    @staticmethod
    def formatear_fecha(fecha: pd.Timestamp, formato: str = '%d/%m/%Y') -> str:
        """Formatea una fecha"""
        if pd.isna(fecha):
            return '-'
        return fecha.strftime(formato)
    
    @staticmethod
    def formatear_mes_año(fecha: pd.Timestamp) -> str:
        """Formatea como 'Mes Año' (ej: Enero 2024)"""
        if pd.isna(fecha):
            return '-'
        
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return f"{meses[fecha.month]} {fecha.year}"
    
    @staticmethod
    def formatear_periodo(fecha_inicio: pd.Timestamp, fecha_fin: pd.Timestamp) -> str:
        """Formatea un período entre dos fechas"""
        if pd.isna(fecha_inicio) or pd.isna(fecha_fin):
            return '-'
        return f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"


class NumberFormatter:
    """Formateador de números generales"""
    
    @staticmethod
    def formatear_porcentaje(valor: float, decimales: int = 1) -> str:
        """Formatea como porcentaje"""
        if pd.isna(valor):
            return '-'
        return f"{valor:.{decimales}f}%"
    
    @staticmethod
    def formatear_numero(valor: Union[int, float], decimales: int = 0, 
                        separador_miles: str = ',') -> str:
        """Formatea un número con separadores de miles"""
        if pd.isna(valor):
            return '-'
        
        if decimales > 0:
            formato = f'{{:,.{decimales}f}}'
        else:
            formato = '{:,.0f}'
        
        resultado = formato.format(valor)
        
        if separador_miles != ',':
            resultado = resultado.replace(',', separador_miles)
        
        return resultado
    
    @staticmethod
    def abreviar_numero(valor: Union[int, float]) -> str:
        """Abrevia números grandes (K, M, B)"""
        if pd.isna(valor):
            return '-'
        
        valor_abs = abs(valor)
        signo = '-' if valor < 0 else ''
        
        if valor_abs >= 1_000_000_000:
            return f"{signo}{valor_abs/1_000_000_000:.1f}B"
        elif valor_abs >= 1_000_000:
            return f"{signo}{valor_abs/1_000_000:.1f}M"
        elif valor_abs >= 1_000:
            return f"{signo}{valor_abs/1_000:.1f}K"
        else:
            return f"{signo}{valor_abs:.0f}"


class TableFormatter:
    """Formateador de tablas para Streamlit"""
    
    @staticmethod
    def aplicar_estilo_condicional(df: pd.DataFrame, 
                                   columnas_monto: list = None) -> pd.DataFrame:
        """
        Aplica estilo condicional a un DataFrame
        
        Args:
            df: DataFrame a estilizar
            columnas_monto: Lista de columnas con montos
        
        Returns:
            Styler de pandas
        """
        if columnas_monto is None:
            # Detectar columnas numéricas
            columnas_monto = df.select_dtypes(include=['number']).columns.tolist()
        
        def color_negativo_positivo(val):
            """Aplica color según el valor"""
            if pd.isna(val) or not isinstance(val, (int, float)):
                return ''
            if val < 0:
                return 'color: #E74C3C; font-weight: bold'
            elif val > 0:
                return 'color: #27AE60; font-weight: bold'
            return ''
        
        styler = df.style.applymap(
            color_negativo_positivo,
            subset=columnas_monto
        )
        
        return styler
    
    @staticmethod
    def crear_pivot_formateado(df: pd.DataFrame,
                               index: str,
                               columns: str,
                               values: str,
                               aggfunc: str = 'sum',
                               formatter: Optional[CurrencyFormatter] = None) -> pd.DataFrame:
        """
        Crea una tabla pivot formateada
        
        Args:
            df: DataFrame fuente
            index: Columna para índice
            columns: Columna para columnas
            values: Columna para valores
            aggfunc: Función de agregación
            formatter: Formateador de moneda
        
        Returns:
            DataFrame pivot
        """
        pivot = pd.pivot_table(
            df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        )
        
        # Formatear si se provee formatter
        if formatter:
            pivot = pivot.applymap(formatter.formatear)
        
        return pivot
