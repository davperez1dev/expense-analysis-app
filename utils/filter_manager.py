"""
Gestor de Filtros Guardados
Permite guardar, cargar y gestionar conjuntos de filtros con nombres personalizados
"""
import json
import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, date
import pandas as pd


class FilterManager:
    """Gestiona la persistencia de filtros guardados"""
    
    def __init__(self, config_path: str = "config/saved_filters.json"):
        """
        Inicializa el gestor de filtros
        
        Args:
            config_path: Ruta al archivo de configuración de filtros
        """
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Asegura que el archivo de configuración exista"""
        if not self.config_path.exists():
            self.config_path.write_text(json.dumps({}, indent=2))
    
    def _serializar_filtros(self, filtros: Dict) -> Dict:
        """
        Convierte objetos no serializables a JSON (date, datetime, Timestamp)
        
        Args:
            filtros: Diccionario con valores de filtros
            
        Returns:
            Diccionario con valores serializables
        """
        filtros_serializables = {}
        for key, value in filtros.items():
            if isinstance(value, (date, datetime, pd.Timestamp)):
                filtros_serializables[key] = value.isoformat()
            elif isinstance(value, tuple) and len(value) == 2:
                # Convertir tuplas de fechas (como rango_fechas)
                filtros_serializables[key] = [
                    v.isoformat() if isinstance(v, (date, datetime, pd.Timestamp)) else v
                    for v in value
                ]
            else:
                filtros_serializables[key] = value
        return filtros_serializables
    
    def _deserializar_filtros(self, filtros: Dict) -> Dict:
        """
        Convierte strings ISO de vuelta a objetos date
        
        Args:
            filtros: Diccionario con valores serializados
            
        Returns:
            Diccionario con objetos date restaurados
        """
        filtros_deserializados = {}
        for key, value in filtros.items():
            if key == 'rango_fechas' and isinstance(value, list) and len(value) == 2:
                # Convertir lista de strings ISO a tupla de dates
                try:
                    filtros_deserializados[key] = tuple(
                        datetime.fromisoformat(v).date() if isinstance(v, str) else v
                        for v in value
                    )
                except:
                    filtros_deserializados[key] = value
            else:
                filtros_deserializados[key] = value
        return filtros_deserializados
    
    def guardar_filtro(self, nombre: str, filtros: Dict) -> bool:
        """
        Guarda un conjunto de filtros con un nombre
        
        Args:
            nombre: Nombre descriptivo para el conjunto de filtros
            filtros: Diccionario con los valores de los filtros
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            filtros_guardados = self.cargar_todos_filtros()
            
            # Serializar filtros (convertir dates a strings)
            filtros_serializables = self._serializar_filtros(filtros)
            
            # Agregar metadata
            filtros_guardados[nombre] = {
                'filtros': filtros_serializables,
                'fecha_creacion': datetime.now().isoformat(),
                'fecha_modificacion': datetime.now().isoformat()
            }
            
            # Guardar al archivo
            self.config_path.write_text(json.dumps(filtros_guardados, indent=2, ensure_ascii=False))
            return True
        except Exception as e:
            st.error(f"Error al guardar filtro: {e}")
            return False
    
    def cargar_filtro(self, nombre: str) -> Optional[Dict]:
        """
        Carga un conjunto de filtros por nombre
        
        Args:
            nombre: Nombre del conjunto de filtros
            
        Returns:
            Diccionario con los filtros o None si no existe
        """
        filtros_guardados = self.cargar_todos_filtros()
        
        if nombre in filtros_guardados:
            filtros_serializados = filtros_guardados[nombre]['filtros']
            # Deserializar (convertir strings ISO de vuelta a dates)
            return self._deserializar_filtros(filtros_serializados)
        return None
    
    def cargar_todos_filtros(self) -> Dict:
        """
        Carga todos los filtros guardados
        
        Returns:
            Diccionario con todos los filtros guardados
        """
        try:
            if self.config_path.exists():
                return json.loads(self.config_path.read_text())
            return {}
        except Exception as e:
            st.error(f"Error al cargar filtros: {e}")
            return {}
    
    def listar_nombres_filtros(self) -> List[str]:
        """
        Lista los nombres de todos los filtros guardados
        
        Returns:
            Lista de nombres de filtros
        """
        filtros = self.cargar_todos_filtros()
        return sorted(filtros.keys())
    
    def eliminar_filtro(self, nombre: str) -> bool:
        """
        Elimina un conjunto de filtros
        
        Args:
            nombre: Nombre del conjunto de filtros a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            filtros_guardados = self.cargar_todos_filtros()
            
            if nombre in filtros_guardados:
                del filtros_guardados[nombre]
                self.config_path.write_text(json.dumps(filtros_guardados, indent=2, ensure_ascii=False))
                return True
            return False
        except Exception as e:
            st.error(f"Error al eliminar filtro: {e}")
            return False
    
    def obtener_ultimo_filtro_usado(self) -> Optional[str]:
        """
        Obtiene el nombre del último filtro usado
        
        Returns:
            Nombre del último filtro o None
        """
        if 'ultimo_filtro_usado' in st.session_state:
            return st.session_state['ultimo_filtro_usado']
        return None
    
    def marcar_filtro_como_usado(self, nombre: str):
        """
        Marca un filtro como el último usado
        
        Args:
            nombre: Nombre del filtro
        """
        st.session_state['ultimo_filtro_usado'] = nombre
    
    def aplicar_filtros_a_session_state(self, filtros: Dict):
        """
        Aplica los filtros cargados al session_state de Streamlit
        IMPORTANTE: Marca los filtros para aplicar en el próximo rerun, 
        evitando conflictos con widgets ya instanciados
        
        Args:
            filtros: Diccionario con los valores de los filtros
        """
        # No aplicar directamente, sino marcar para aplicar en próximo ciclo
        st.session_state['_filtros_pendientes'] = filtros
