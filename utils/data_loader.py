"""
DataLoader: Carga y transforma datos del CSV de gastos
"""
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil import parser
from pathlib import Path
from typing import Optional, Tuple
import logging
import unicodedata

logger = logging.getLogger(__name__)


class DataLoader:
    """Carga y transforma datos de gastos desde CSV"""
    
    def __init__(self):
        self.df_wide = None
        self.df_long = None
    
    def cargar_csv(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Carga el archivo CSV en formato wide
        
        Args:
            file_path: Ruta al archivo CSV
            encoding: Codificación del archivo
        
        Returns:
            DataFrame en formato wide (categorías como filas, períodos como columnas)
        """
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"CSV cargado: {file_path} - Shape: {df.shape}")
            self.df_wide = df
            return df
        except Exception as e:
            logger.error(f"Error al cargar CSV: {e}")
            raise
    
    def transformar_a_long(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Transforma el DataFrame de formato wide a long
        
        Args:
            df: DataFrame en formato wide (opcional, usa self.df_wide si no se provee)
        
        Returns:
            DataFrame en formato long con columnas: Categorías, Periodo, Monto
        """
        if df is None:
            df = self.df_wide
        
        if df is None:
            raise ValueError("No hay datos cargados. Usa cargar_csv() primero.")
        
        # Identificar columna de categorías (primera columna)
        categoria_col = df.columns[0]
        
        # Columnas de períodos (todas excepto la primera)
        periodo_cols = df.columns[1:].tolist()
        
        # Melt: convertir de wide a long
        df_long = pd.melt(
            df,
            id_vars=[categoria_col],
            value_vars=periodo_cols,
            var_name='Periodo',
            value_name='Monto'
        )
        
        # Renombrar columna de categorías si es necesario
        if categoria_col != 'Categorías':
            df_long = df_long.rename(columns={categoria_col: 'Categorías'})
        
        # Limpiar montos (remover separadores de miles y convertir a float)
        df_long['Monto'] = df_long['Monto'].apply(self._limpiar_monto)
        
        logger.info(f"Transformación a long completada - Shape: {df_long.shape}")
        self.df_long = df_long
        return df_long
    
    def _limpiar_monto(self, valor) -> float:
        """Convierte strings de montos con formato a float"""
        if pd.isna(valor):
            return 0.0
        
        if isinstance(valor, (int, float)):
            return float(valor)
        
        # Si es string, remover separadores de miles y espacios
        valor_str = str(valor).strip()
        valor_str = valor_str.replace(',', '')  # Remover comas
        valor_str = valor_str.replace('.', '', valor_str.count('.') - 1)  # Mantener solo el último punto
        valor_str = valor_str.replace(' ', '')  # Remover espacios
        
        try:
            return float(valor_str)
        except ValueError:
            logger.warning(f"No se pudo convertir a float: {valor}")
            return 0.0
    
    def extraer_fecha_periodo(self, periodo: str) -> Tuple[datetime, str, int, str]:
        """
        Extrae información de fecha desde el string de período
        
        Args:
            periodo: String como "1/1/2024-31/1/2024"
        
        Returns:
            Tupla (fecha_inicio, nombre_mes, año, mes_año_str)
        """
        try:
            # Tomar la fecha de inicio (primera parte antes del guión)
            fecha_inicio_str = periodo.split('-')[0].strip()
            
            # Parsear la fecha
            fecha_inicio = parser.parse(fecha_inicio_str, dayfirst=True)
            
            # Extraer componentes
            nombre_mes = self._obtener_nombre_mes(fecha_inicio.month)
            año = fecha_inicio.year
            mes_año = f"{nombre_mes} {año}"
            
            return fecha_inicio, nombre_mes, año, mes_año
        except Exception as e:
            logger.error(f"Error al parsear período '{periodo}': {e}")
            return None, 'Desconocido', 0, 'Desconocido'
    
    def _obtener_nombre_mes(self, mes_num: int) -> str:
        """Convierte número de mes a nombre en español"""
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return meses.get(mes_num, 'Desconocido')
    
    def _normalizar_texto(self, texto: str) -> str:
        """
        Normaliza texto para comparaciones (minúsculas y sin acentos)
        
        Args:
            texto: Texto a normalizar
        
        Returns:
            Texto normalizado
        """
        # Convertir a minúsculas
        texto = texto.lower().strip()
        
        # Remover acentos usando unicodedata
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
        
        return texto
    
    def validar_duplicados(self, df: pd.DataFrame) -> None:
        """
        Detecta y advierte sobre categorías con nombres duplicados (normalizados)
        
        Args:
            df: DataFrame en formato long con columna 'Categorías'
        """
        if 'Categorías' not in df.columns:
            logger.warning("No se encontró columna 'Categorías' para validar duplicados")
            return
        
        # Obtener categorías únicas del dataframe
        categorias_unicas = df['Categorías'].unique()
        
        # Crear diccionario: nombre_normalizado -> lista de nombres originales
        nombres_normalizados = {}
        for cat in categorias_unicas:
            cat_norm = self._normalizar_texto(str(cat))
            if cat_norm not in nombres_normalizados:
                nombres_normalizados[cat_norm] = []
            nombres_normalizados[cat_norm].append(cat)
        
        # Buscar duplicados (más de un nombre original para el mismo nombre normalizado)
        duplicados = {
            norm: originales 
            for norm, originales in nombres_normalizados.items() 
            if len(originales) > 1
        }
        
        if duplicados:
            logger.warning("=" * 80)
            logger.warning("⚠️  CATEGORÍAS DUPLICADAS DETECTADAS")
            logger.warning("=" * 80)
            logger.warning("Las siguientes categorías tienen nombres duplicados (ignorando")
            logger.warning("mayúsculas/minúsculas, acentos y espacios extras):")
            logger.warning("")
            
            for norm, originales in duplicados.items():
                logger.warning(f"  • Nombre normalizado: '{norm}'")
                logger.warning(f"    Nombres encontrados: {originales}")
                logger.warning("")
            
            logger.warning("ADVERTENCIA: Los nombres duplicados causarán pérdida de datos durante")
            logger.warning("la clasificación, ya que el índice del clasificador solo guardará una")
            logger.warning("de las categorías duplicadas.")
            logger.warning("")
            logger.warning("SOLUCIÓN: Renombre las categorías para que sean únicas. Por ejemplo:")
            logger.warning("  - 'Mantenimiento' en B-Transporte → 'Mantenimiento Auto'")
            logger.warning("  - 'Mantenimiento' en N-Vivienda → 'Mantenimiento Casa'")
            logger.warning("=" * 80)
        else:
            logger.info("✓ Validación de duplicados: No se encontraron categorías duplicadas")
    
    
    def agregar_columnas_temporales(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Agrega columnas con información temporal extraída del período
        
        Args:
            df: DataFrame en formato long (opcional)
        
        Returns:
            DataFrame con columnas adicionales: Fecha, Mes, Año, MesAño, MesNum
        """
        if df is None:
            df = self.df_long
        
        if df is None:
            raise ValueError("No hay datos en formato long. Usa transformar_a_long() primero.")
        
        df = df.copy()
        
        # Extraer información temporal
        temporal_info = df['Periodo'].apply(self.extraer_fecha_periodo)
        
        df['Fecha'] = temporal_info.apply(lambda x: x[0])
        df['Mes'] = temporal_info.apply(lambda x: x[1])
        df['Año'] = temporal_info.apply(lambda x: x[2])
        df['MesAño'] = temporal_info.apply(lambda x: x[3])
        
        # Agregar número de mes para ordenamiento
        meses_orden = {
            'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
            'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
            'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
        }
        df['MesNum'] = df['Mes'].map(meses_orden)
        
        # Crear una columna de ordenamiento que combine año y mes
        df['FechaOrden'] = df['Año'] * 100 + df['MesNum']
        
        logger.info("Columnas temporales agregadas")
        return df
    
    def procesar_completo(self, file_path: str) -> pd.DataFrame:
        """
        Pipeline completo: carga, transforma y agrega información temporal
        
        Args:
            file_path: Ruta al archivo CSV
        
        Returns:
            DataFrame procesado en formato long con todas las columnas
        """
        # 1. Cargar CSV
        self.cargar_csv(file_path)
        
        # 2. Transformar a formato long
        df = self.transformar_a_long()
        
        # 3. Validar duplicados (antes de clasificar)
        self.validar_duplicados(df)
        
        # 4. Agregar columnas temporales
        df = self.agregar_columnas_temporales(df)
        
        # 5. Ordenar por fecha
        df = df.sort_values(['Fecha', 'Categorías']).reset_index(drop=True)
        
        logger.info(f"Procesamiento completo finalizado - {len(df)} registros")
        return df
    
    def obtener_resumen(self, df: Optional[pd.DataFrame] = None) -> dict:
        """Retorna un resumen estadístico de los datos"""
        if df is None:
            df = self.df_long
        
        if df is None:
            return {}
        
        return {
            'total_registros': len(df),
            'categorias_unicas': df['Categorías'].nunique(),
            'periodos_unicos': df['Periodo'].nunique() if 'Periodo' in df.columns else 0,
            'rango_fechas': (df['Fecha'].min(), df['Fecha'].max()) if 'Fecha' in df.columns else None,
            'total_gastos': df[df['Monto'] < 0]['Monto'].sum(),
            'total_ingresos': df[df['Monto'] > 0]['Monto'].sum(),
        }
