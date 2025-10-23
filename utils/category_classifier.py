"""CategoryClassifier: Clasifica categorías según la jerarquía definida en configuración.
Utiliza un índice pre-construido para clasificación O(1) y normalización de texto.
"""
import pandas as pd
from typing import Tuple, Optional, Dict
from utils.config_loader import ConfigLoader
import logging
import unicodedata

logger = logging.getLogger(__name__)


class CategoryClassifier:
    """Clasifica categorías en grupos según jerarquía configurable"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader
        self.grupos = config_loader.get_grupos()
        self.jerarquia = config_loader.get_jerarquia_categorias()
        self.contextuales = config_loader.get_categorias_contextuales()
        self.filas_resumen = config_loader.get_filas_resumen()
        
        # Para evitar advertencias repetidas por la misma categoría
        self._warned_categories = set()
        
        # Construir índice inverso: subcategoria -> (grupo, cat_principal, subcat)
        self._indice_subcategorias = self._construir_indice()
    
    def _normalizar(self, texto: str) -> str:
        """Normaliza texto: minúsculas, sin acentos, sin espacios extras"""
        if not texto:
            return ""
        texto = str(texto).strip()
        # Quitar acentos
        nfkd = unicodedata.normalize('NFKD', texto)
        sin_acentos = ''.join([c for c in nfkd if not unicodedata.combining(c)])
        return sin_acentos.lower()
    
    def _construir_indice(self) -> Dict[str, Tuple[str, str, Optional[str]]]:
        """
        Construye un índice normalizado: 
        {subcategoria_normalizada: (grupo_nombre, cat_principal, subcat_original)}
        """
        indice = {}
        
        if not self.jerarquia:
            return indice
        
        for grupo_key, categorias in self.jerarquia.items():
            # Validar que categorias no sea None
            if not categorias or not isinstance(categorias, dict):
                continue
                
            for cat_principal, info in categorias.items():
                # Validar que info tenga la estructura esperada
                if not info or not isinstance(info, dict):
                    continue
                    
                grupo_codigo = info.get('grupo')
                if not grupo_codigo or grupo_codigo not in self.grupos:
                    continue
                    
                grupo_nombre = self.grupos[grupo_codigo]['nombre']
                
                # Indexar la categoría principal (sin subcategoría)
                cat_norm = self._normalizar(cat_principal)
                indice[cat_norm] = (grupo_nombre, cat_principal, None)
                
                # Indexar todas las subcategorías
                for subcat in info.get('subcategorias', []):
                    subcat_norm = self._normalizar(subcat)
                    indice[subcat_norm] = (grupo_nombre, cat_principal, subcat)
        
        return indice
    
    def clasificar(self, categoria: str, monto: float) -> Tuple[str, str, Optional[str]]:
        """
        Clasifica una categoría según la jerarquía definida.
        
        Args:
            categoria: Nombre de la categoría
            monto: Monto asociado (para reglas contextuales)
        
        Returns:
            Tupla (grupo, categoria_principal, subcategoria)
        """
        # Excluir filas resumen (comparación normalizada)
        categoria_norm = self._normalizar(categoria)
        if any(self._normalizar(fila) == categoria_norm for fila in self.filas_resumen):
            return ('Resumen', categoria, None)
        
        # 1. Buscar en el índice de jerarquía (búsqueda exacta)
        if categoria_norm in self._indice_subcategorias:
            return self._indice_subcategorias[categoria_norm]
        
        # 2. Buscar en categorías contextuales ("Otros")
        resultado_contextual = self._clasificar_contextual(categoria, monto)
        if resultado_contextual:
            return resultado_contextual
        
        # 3. Intentar match por prefijo de grupo (B-, D-, N-, R-, O-)
        prefijos_grupos = {
            'B-': 'basico',
            'D-': 'discrecional', 
            'N-': 'necesario',
            'R-': 'ingreso_regular',
            'O-': 'ingreso_ocasional'
        }
        
        for prefijo, grupo_codigo in prefijos_grupos.items():
            if categoria.startswith(prefijo):
                if grupo_codigo in self.grupos:
                    grupo_nombre = self.grupos[grupo_codigo]['nombre']
                    # Retornar como categoría principal sin subcategoría
                    return (grupo_nombre, categoria, None)
        
        # 4. Si no se encuentra, advertir una sola vez por categoría
        if categoria not in self._warned_categories:
            self._warned_categories.add(categoria)
            logger.warning(f"Categoría sin clasificar: '{categoria}'")
        
        return ('Sin Clasificar', categoria, None)
    
    def _clasificar_contextual(self, categoria: str, monto: float) -> Optional[Tuple]:
        """Clasifica categorías contextuales como 'Otros' según el signo del monto"""
        categoria_norm = self._normalizar(categoria)
        
        for cat_key, config in self.contextuales.items():
            cat_key_norm = self._normalizar(cat_key)
            
            # Verificar si la categoría coincide exactamente o es subcategoría
            es_match = (categoria_norm == cat_key_norm or 
                       categoria_norm.startswith(cat_key_norm + ' -'))
            
            if es_match and config.get('clasificar_por') == 'signo_monto':
                # Clasificar según el signo del monto
                if monto > 0:
                    info = config['si_positivo']
                else:
                    info = config['si_negativo']
                
                grupo_codigo = info['grupo']
                grupo_nombre = self.grupos[grupo_codigo]['nombre']
                cat_principal = info.get('categoria_principal', cat_key)
                
                # Determinar si es subcategoría (tiene " - ")
                if ' - ' in categoria:
                    subcat = categoria.split(' - ', 1)[1]
                    return (grupo_nombre, cat_principal, subcat)
                else:
                    return (grupo_nombre, cat_principal, None)
        
        return None
    
    def clasificar_dataframe(self, df: pd.DataFrame, categoria_col: str = 'Categorías', 
                            monto_col: str = 'Monto') -> pd.DataFrame:
        """
        Clasifica todas las filas de un DataFrame
        
        Args:
            df: DataFrame con los datos
            categoria_col: Nombre de la columna de categorías
            monto_col: Nombre de la columna de montos
        
        Returns:
            DataFrame con columnas adicionales: Grupo, Categoria_Principal, Subcategoria
        """
        df = df.copy()
        
        clasificaciones = df.apply(
            lambda row: self.clasificar(row[categoria_col], row[monto_col]),
            axis=1
        )
        
        df['Grupo'] = clasificaciones.apply(lambda x: x[0])
        df['Categoria_Principal'] = clasificaciones.apply(lambda x: x[1])
        df['Subcategoria'] = clasificaciones.apply(lambda x: x[2])
        
        return df
    
    def obtener_lista_grupos(self, incluir_resumen: bool = False) -> list:
        """Retorna lista de nombres de grupos únicos"""
        grupos = [g['nombre'] for g in self.grupos.values()]
        if incluir_resumen:
            grupos.append('Resumen')
        return grupos
    
    def obtener_jerarquia_completa(self) -> Dict:
        """Devuelve la jerarquía completa para construir filtros en la UI"""
        return self.jerarquia
    
    def obtener_categorias_principales(self, grupo: Optional[str] = None) -> list:
        """Obtiene lista de categorías principales, opcionalmente filtradas por grupo"""
        categorias = []
        
        for grupo_key, cats in self.jerarquia.items():
            if grupo and grupo_key != grupo:
                continue
            categorias.extend(cats.keys())
        
        return sorted(categorias)
    
    def obtener_categorias_con_subcategorias(self) -> list:
        """
        Retorna lista de categorías principales que tienen subcategorías definidas.
        Estas son filas de 'totales' en el CSV que deben excluirse para evitar doble contabilización.
        """
        categorias_totales = []
        
        if not self.jerarquia:
            return categorias_totales
        
        for grupo_key, categorias in self.jerarquia.items():
            if not categorias or not isinstance(categorias, dict):
                continue
            
            for cat_principal, info in categorias.items():
                if not info or not isinstance(info, dict):
                    continue
                
                # Si tiene subcategorías definidas, es una fila de total
                subcategorias = info.get('subcategorias', [])
                if subcategorias and len(subcategorias) > 0:
                    categorias_totales.append(cat_principal)
        
        return categorias_totales
    
    def obtener_subcategorias(self, categoria_principal: str) -> list:
        """Obtiene lista de subcategorías de una categoría principal"""
        for grupo_key, cats in self.jerarquia.items():
            if categoria_principal in cats:
                return cats[categoria_principal].get('subcategorias', [])
        return []
