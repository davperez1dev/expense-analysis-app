"""
ConfigLoader: Carga y valida el archivo de configuración YAML
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigLoader:
    """Carga y gestiona la configuración desde el archivo YAML"""
    
    def __init__(self, config_path: str = "config/categories_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga el archivo YAML de configuración"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"Configuración cargada desde: {self.config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Archivo de configuración no encontrado: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error al parsear YAML: {e}")
            raise
    
    def _validate_config(self):
        """Valida que la configuración tenga la estructura correcta"""
        required_keys = ['grupos', 'jerarquia_categorias', 'filas_resumen']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Falta clave requerida en configuración: {key}")
        
        logger.info("Configuración validada correctamente")
    
    def get_grupos(self) -> Dict[str, Dict]:
        """Retorna el diccionario de grupos"""
        return self.config.get('grupos', {})
    
    def get_grupo_info(self, grupo_codigo: str) -> Dict:
        """Retorna información de un grupo específico"""
        return self.config.get('grupos', {}).get(grupo_codigo, {})
    
    def get_reglas(self) -> List[Dict]:
        """Retorna las reglas de clasificación ordenadas por prioridad (DEPRECATED - usar jerarquia_categorias)"""
        return sorted(
            self.config.get('reglas_clasificacion', []),
            key=lambda x: x.get('prioridad', 999)
        )
    
    def get_jerarquia_categorias(self) -> Dict:
        """Retorna la jerarquía completa de categorías y subcategorías"""
        return self.config.get('jerarquia_categorias', {})
    
    def get_categorias_contextuales(self) -> Dict:
        """Retorna las categorías contextuales (como 'Otros')"""
        return self.config.get('categorias_contextuales', {})
    
    def get_filas_resumen(self) -> List[str]:
        """Retorna la lista de filas que son resúmenes"""
        return self.config.get('filas_resumen', [])
    
    def get_formato_moneda(self) -> Dict:
        """Retorna la configuración de formato de moneda"""
        return self.config.get('formato_moneda', {
            'simbolo': '$',
            'separador_miles': ',',
            'separador_decimal': '.',
            'decimales': 2,
            'posicion_simbolo': 'antes'
        })
    
    def get_colores_valores(self) -> Dict:
        """Retorna los colores para valores positivos/negativos"""
        return self.config.get('colores_valores', {})
    
    def get_colores_subcategorias(self) -> List[str]:
        """Retorna la paleta de colores para subcategorías"""
        return self.config.get('colores_subcategorias', [])
    
    def get_jerarquia(self) -> Dict:
        """Retorna la configuración de jerarquía visual (formato_visual)"""
        return self.config.get('formato_visual', {})
    
    def get_colores_graficos(self) -> Dict:
        """Retorna los colores para gráficos por grupo"""
        return self.config.get('colores_graficos', {})
    
    def get_color_grupo(self, grupo_nombre: str) -> str:
        """Retorna el color asociado a un grupo por su nombre"""
        for grupo_data in self.get_grupos().values():
            if grupo_data.get('nombre') == grupo_nombre:
                return grupo_data.get('color', '#95A5A6')
        return '#95A5A6'  # Color por defecto
    
    def get_version(self) -> str:
        """Retorna la versión de la configuración"""
        return self.config.get('version', 'unknown')
