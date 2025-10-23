"""
Sidebar: Componente de barra lateral con filtros
"""
import streamlit as st
import pandas as pd
from typing import Tuple, List, Optional
from datetime import datetime
from utils.config_loader import ConfigLoader


class FilterSidebar:
    """Componente de sidebar con filtros dinámicos"""
    
    def __init__(self):
        self.filtros_aplicados = {}
    
    def _obtener_grupos_por_tipo(self):
        """Obtiene el mapeo de grupos a tipos desde la configuración.
        Retorna un diccionario {nombre_grupo: tipo} donde nombre_grupo es el display name."""
        from utils.config_loader import ConfigLoader
        cfg = ConfigLoader('config/categories_config.yaml')
        grupos_config = cfg.get_grupos()
        nombre_a_tipo = {}
        for grupo_key, grupo_info in grupos_config.items():
            # Usar el 'nombre' del grupo, no el key
            nombre = grupo_info.get('nombre', grupo_key)
            tipo = grupo_info.get('tipo', 'gasto')
            nombre_a_tipo[nombre] = tipo
        return nombre_a_tipo
    
    def _inicializar_session_state(self, df: pd.DataFrame):
        """Inicializa valores por defecto en session_state si no existen.
        IMPORTANTE: Solo se ejecuta la primera vez. Los valores persistirán entre páginas."""
        # Inicializar fechas solo si no existen
        if 'Fecha' in df.columns and 'rango_fechas' not in st.session_state:
            fecha_min = pd.to_datetime(df['Fecha'].min()).date()
            fecha_max = pd.to_datetime(df['Fecha'].max()).date()
            st.session_state['rango_fechas'] = (fecha_min, fecha_max)
        
        # Inicializar años y meses si no existen
        if 'Año' in df.columns and 'años_seleccionados' not in st.session_state:
            st.session_state['años_seleccionados'] = [datetime.now().year]
        
        if 'Mes' in df.columns and 'meses_seleccionados' not in st.session_state:
            # Inicializar con el mes actual solamente
            mes_actual = datetime.now().strftime('%B')
            meses_esp = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }
            st.session_state['meses_seleccionados'] = [meses_esp.get(mes_actual, 'Enero')]
        
        # Inicializar grupos si no existen (SOLO si NINGUNO existe)
        if 'Grupo' in df.columns:
            if 'gastos_grupos' not in st.session_state:
                st.session_state['gastos_grupos'] = []
            if 'ingresos_grupos' not in st.session_state:
                st.session_state['ingresos_grupos'] = []
        
        # Inicializar categorías si no existen (vacías para que el usuario seleccione)
        if 'Categorías' in df.columns:
            if 'cats_gastos' not in st.session_state:
                st.session_state['cats_gastos'] = []
            
            if 'cats_ingresos' not in st.session_state:
                st.session_state['cats_ingresos'] = []
        
        # Inicializar checkbox todos_grupos solo si no existe
        if 'todos_grupos' not in st.session_state:
            st.session_state['todos_grupos'] = False
    
    def renderizar(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Renderiza la barra lateral con todos los filtros
        
        Args:
            df: DataFrame completo con datos
        
        Returns:
            Tupla (DataFrame filtrado, diccionario de filtros aplicados)
        """
        # Aplicar filtros pendientes ANTES de crear widgets
        if '_filtros_pendientes' in st.session_state:
            filtros_pendientes = st.session_state['_filtros_pendientes']
            del st.session_state['_filtros_pendientes']
            
            # Aplicar cada filtro al session_state
            for key, value in filtros_pendientes.items():
                st.session_state[key] = value
            
            # Forzar rerun para que los widgets se actualicen
            st.rerun()
        
        # Inicializar session_state con valores por defecto
        self._inicializar_session_state(df)
        
        # Header mejorado con estilo profesional
        st.sidebar.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="margin:0; color: white; font-size: 24px; text-align: center;">
                🔍 FILTROS
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Gestión de filtros guardados (al inicio para acceso rápido)
        self._seccion_filtros_guardados()
        
        st.sidebar.markdown("---")
        
        # Subir archivo CSV
        self._seccion_upload()
        
        st.sidebar.markdown("---")
        
        # Filtros de fecha
        fecha_filtro = self._seccion_fechas(df)
        
        st.sidebar.markdown("---")
        
        # Filtros de grupos
        grupos_filtro = self._seccion_grupos(df)
        
        st.sidebar.markdown("---")
        
        # Filtros de categorías
        categorias_filtro = self._seccion_categorias(df, grupos_filtro)
        
        st.sidebar.markdown("---")
        
        # Filtros de monto
        monto_filtro = self._seccion_montos(df)
        
        st.sidebar.markdown("---")
        
        # Botones de acción
        col1, col2 = st.sidebar.columns(2)
        aplicar = col1.button("✅ Aplicar", type="primary", use_container_width=True)
        limpiar = col2.button("🔄 Limpiar", use_container_width=True)
        
        # Limpiar filtros si se solicita
        if limpiar:
            # Eliminar keys específicas de filtros pero mantener uploaded_file
            uploaded_file = st.session_state.get('uploaded_file')
            keys_to_remove = [k for k in st.session_state.keys() if k not in ['uploaded_file']]
            for key in keys_to_remove:
                del st.session_state[key]
            # Restaurar uploaded_file si existía
            if uploaded_file is not None:
                st.session_state['uploaded_file'] = uploaded_file
            st.rerun()
        
        # Aplicar filtros
        df_filtrado = self._aplicar_filtros(
            df, fecha_filtro, grupos_filtro, categorias_filtro, monto_filtro
        )
        
        # Mostrar contador de registros con mejor estilo
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
        <div style="background: rgba(33, 150, 243, 0.1); 
                    padding: 12px; 
                    border-radius: 8px;
                    border-left: 4px solid #2196F3;
                    margin: 10px 0;">
            <div style="color: #2196F3; font-weight: 600; font-size: 16px;">
                📊 {len(df_filtrado):,} registros
            </div>
            <div style="color: #666; font-size: 12px; margin-top: 4px;">
                de {len(df):,} totales
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Guardar filtros aplicados
        self.filtros_aplicados = {
            'fechas': fecha_filtro,
            'grupos': grupos_filtro,
            'categorias': categorias_filtro,
            'montos': monto_filtro
        }
        
        return df_filtrado, self.filtros_aplicados
    
    def _seccion_upload(self):
        """Sección para subir archivo CSV"""
        st.sidebar.subheader("📂 Cargar Datos")
        uploaded_file = st.sidebar.file_uploader(
            "Subir archivo CSV",
            type=['csv'],
            help="Sube tu propio archivo de gastos en formato CSV"
        )
        
        if uploaded_file is not None:
            st.session_state['uploaded_file'] = uploaded_file
            st.sidebar.success("✅ Archivo cargado")
    
    def _seccion_fechas(self, df: pd.DataFrame) -> dict:
        """Sección de filtros de fecha"""
        st.sidebar.subheader("📅 Fechas")
        
        if 'Fecha' not in df.columns:
            return {}
        
        # Obtener rango de fechas (asegurar que sean objetos date)
        fecha_min = pd.to_datetime(df['Fecha'].min()).date()
        fecha_max = pd.to_datetime(df['Fecha'].max()).date()
        
        # Inicializar en session_state si no existe (en lugar de usar 'value')
        if 'rango_fechas' not in st.session_state:
            st.session_state['rango_fechas'] = (fecha_min, fecha_max)
        
        # Validar que el valor en session_state sea válido
        if not isinstance(st.session_state['rango_fechas'], tuple):
            st.session_state['rango_fechas'] = (fecha_min, fecha_max)
        elif len(st.session_state['rango_fechas']) != 2:
            st.session_state['rango_fechas'] = (fecha_min, fecha_max)
        
        # Selector de rango (SIN 'value', solo 'key')
        rango_fechas = st.sidebar.date_input(
            "Rango de fechas",
            min_value=fecha_min,
            max_value=fecha_max,
            format="DD/MM/YYYY",
            key='rango_fechas'
        )
        
        # Selector de años
        años_disponibles = sorted(df['Año'].unique().tolist(), reverse=True)
        
        # Validar que los años seleccionados estén disponibles
        if 'años_seleccionados' in st.session_state:
            st.session_state['años_seleccionados'] = [a for a in st.session_state['años_seleccionados'] if a in años_disponibles]
        
        años_seleccionados = st.sidebar.multiselect(
            "Años",
            options=años_disponibles,
            key='años_seleccionados'
        )
        
        # Selector de meses
        if 'Mes' in df.columns:
            meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            meses_disponibles = [m for m in meses_orden if m in df['Mes'].unique()]
            
            # Validar que los meses seleccionados estén disponibles
            if 'meses_seleccionados' in st.session_state:
                st.session_state['meses_seleccionados'] = [m for m in st.session_state['meses_seleccionados'] if m in meses_disponibles]
            
            meses_seleccionados = st.sidebar.multiselect(
                "Meses",
                options=meses_disponibles,
                key='meses_seleccionados'
            )
        else:
            meses_seleccionados = []
        
        return {
            'rango': rango_fechas if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2 else (fecha_min, fecha_max),
            'años': años_seleccionados,
            'meses': meses_seleccionados
        }
    
    def _seccion_grupos(self, df: pd.DataFrame) -> List[str]:
        """Sección de filtros de grupos"""
        st.sidebar.subheader("🏷️ Grupos")

        if 'Grupo' not in df.columns:
            return []

        # Obtener grupos disponibles (excluir Resumen)
        nombre_a_tipo = self._obtener_grupos_por_tipo()
        grupos_disponibles = sorted([g for g in df['Grupo'].unique() if g != 'Resumen'])

        # Incluir 'mixto' en ambos: gastos e ingresos (para el grupo "Especiales")
        gastos_groups = [g for g in grupos_disponibles if nombre_a_tipo.get(g, 'gasto') in ['gasto', 'mixto']]
        ingresos_groups = [g for g in grupos_disponibles if nombre_a_tipo.get(g, 'gasto') in ['ingreso', 'mixto']]

        # Validar que los valores en session_state estén en las opciones disponibles
        # Si no lo están, limpiarlos para evitar que se pierdan
        if 'gastos_grupos' in st.session_state:
            st.session_state['gastos_grupos'] = [g for g in st.session_state['gastos_grupos'] if g in gastos_groups]
        if 'ingresos_grupos' in st.session_state:
            st.session_state['ingresos_grupos'] = [g for g in st.session_state['ingresos_grupos'] if g in ingresos_groups]

        # Checkbox "Todos" - NO usar 'value' cuando hay 'key'
        todos = st.sidebar.checkbox("✅ Seleccionar todos", key='todos_grupos')

        if todos:
            # Cuando "todos" está marcado, usar todos los grupos disponibles
            # pero NO actualizar session_state (para que se preserve la selección anterior)
            gastos_seleccionados = gastos_groups
            ingresos_seleccionados = ingresos_groups
        else:
            # Sección de grupos de gastos con encabezado visual
            if gastos_groups:
                
                st.sidebar.markdown("""
                <div style='background-color: rgba(231, 76, 60, 0.1); 
                            padding: 8px; 
                            border-radius: 5px; 
                            border-left: 4px solid #E74C3C;
                            margin: 10px 0px;'>
                    <span style='color:#E74C3C; font-weight:600; font-size: 14px;'>
                        📉 GASTOS
                    </span>
                </div>
                """, unsafe_allow_html=True)
                gastos_seleccionados = st.sidebar.multiselect(
                    "Grupos (gastos)", options=gastos_groups, 
                    key='gastos_grupos', label_visibility="collapsed"
                )
            else:
                gastos_seleccionados = []

            # Sección de grupos de ingresos (con encabezado verde)
            if ingresos_groups:
                st.sidebar.markdown("""
                <div style='background-color: rgba(39, 174, 96, 0.1); 
                            padding: 8px; 
                            border-radius: 5px; 
                            border-left: 4px solid #27AE60;
                            margin: 10px 0px;'>
                    <span style='color:#27AE60; font-weight:600; font-size: 14px;'>
                        📈 INGRESOS
                    </span>
                </div>
                """, unsafe_allow_html=True)
                ingresos_seleccionados = st.sidebar.multiselect(
                    "Grupos (ingresos)", options=ingresos_groups, 
                    key='ingresos_grupos', label_visibility="collapsed"
                )
            else:
                ingresos_seleccionados = []

        grupos_seleccionados = []
        grupos_seleccionados.extend(gastos_seleccionados or [])
        grupos_seleccionados.extend(ingresos_seleccionados or [])

        return grupos_seleccionados
    
    def _seccion_categorias(self, df: pd.DataFrame, grupos_filtro: List[str]) -> List[str]:
        """Sección de filtros de categorías"""
        st.sidebar.subheader("📊 Categorías")
        
        if 'Categoria_Principal' not in df.columns:
            return []
        
        # Obtener TODAS las categorías desde el YAML (no solo las que tienen datos)
        cfg = ConfigLoader('config/categories_config.yaml')
        jerarquia = cfg.config.get('jerarquia_categorias', {})
        contextuales = cfg.config.get('categorias_contextuales', {})
        grupos_config = cfg.get_grupos()
        
        # Mapear nombre de grupo a tipo
        nombre_a_tipo = {v.get('nombre'): v.get('tipo', 'gasto') for v in grupos_config.values()}
        
        # Construir lista completa de categorías desde YAML
        categorias_completas = {}  # {categoria: tipo}
        
        # De jerarquia_categorias
        for grupo_key, categorias in jerarquia.items():
            # Validar que categorias no sea None
            if not categorias or not isinstance(categorias, dict):
                continue
            
            for cat_principal, info in categorias.items():
                # Validar que info tenga la estructura esperada
                if not info or not isinstance(info, dict) or 'grupo' not in info:
                    continue
                    
                grupo_codigo = info['grupo']
                if grupo_codigo not in grupos_config:
                    continue
                    
                grupo_nombre = grupos_config[grupo_codigo]['nombre']
                tipo = nombre_a_tipo.get(grupo_nombre, 'gasto')
                categorias_completas[cat_principal] = tipo
        
        # De categorias_contextuales (Otros)
        for cat_key, config_ctx in contextuales.items():
            # "Otros" puede ser gasto o ingreso según el signo
            # Lo añadimos en ambos lados
            categorias_completas[cat_key] = 'ambos'  # Marca especial
        
        # Filtrar categorías según grupos seleccionados (si aplica)
        if grupos_filtro:
            df_filtrado = df[df['Grupo'].isin(grupos_filtro)]
            categorias_con_datos = set(df_filtrado['Categoria_Principal'].unique())
            # Intersección: solo mostrar categorías que están en YAML Y tienen datos
            categorias_disponibles = {k: v for k, v in categorias_completas.items() 
                                     if k in categorias_con_datos}
        else:
            # Mostrar todas las categorías del YAML que tengan datos
            categorias_con_datos = set(df['Categoria_Principal'].unique())
            categorias_disponibles = {k: v for k, v in categorias_completas.items() 
                                     if k in categorias_con_datos}
        
        # Separar por tipo
        categorias_gastos = sorted([k for k, v in categorias_disponibles.items() 
                                   if v in ['gasto', 'ambos']])
        categorias_ingresos = sorted([k for k, v in categorias_disponibles.items() 
                                     if v in ['ingreso', 'ambos']])
        
        # Búsqueda
        busqueda = st.sidebar.text_input(
            "🔍 Buscar categoría",
            placeholder="Escribe para buscar...",
            key='busqueda_categoria'
        )
        
        gastos_cats = categorias_gastos
        ingresos_cats = categorias_ingresos
        
        if busqueda:
            gastos_cats = [c for c in gastos_cats if busqueda.lower() in c.lower()]
            ingresos_cats = [c for c in ingresos_cats if busqueda.lower() in c.lower()]

        # Validar que las categorías seleccionadas estén disponibles
        if 'cats_gastos' in st.session_state:
            st.session_state['cats_gastos'] = [c for c in st.session_state['cats_gastos'] if c in gastos_cats]
        if 'cats_ingresos' in st.session_state:
            st.session_state['cats_ingresos'] = [c for c in st.session_state['cats_ingresos'] if c in ingresos_cats]

        # Mostrar dos multiselects: Gastos e Ingresos con encabezados visuales
        seleccionados = []

        if gastos_cats:
            st.sidebar.markdown("""
            <div style='background-color: rgba(231, 76, 60, 0.1); 
                        padding: 8px; 
                        border-radius: 5px; 
                        border-left: 4px solid #E74C3C;
                        margin: 10px 0px;'>
                <span style='color:#E74C3C; font-weight:600; font-size: 14px;'>
                    📉 GASTOS (categorías)
                </span>
            </div>
            """, unsafe_allow_html=True)
            sel_g = st.sidebar.multiselect(
                "Categorías (gastos)", options=gastos_cats,
                key='cats_gastos',
                label_visibility="collapsed"
            )
            seleccionados.extend(sel_g)

        if ingresos_cats:
            # Encabezado verde para ingresos con icono
            st.sidebar.markdown("""
            <div style='background-color: rgba(39, 174, 96, 0.1); 
                        padding: 8px; 
                        border-radius: 5px; 
                        border-left: 4px solid #27AE60;
                        margin: 10px 0px;'>
                <span style='color:#27AE60; font-weight:600; font-size: 14px;'>
                    📈 INGRESOS (categorías)
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            sel_i = st.sidebar.multiselect(
                "Categorías (ingresos)", options=ingresos_cats,
                key='cats_ingresos',
                label_visibility="collapsed"
            )
            seleccionados.extend(sel_i)

        return seleccionados
    
    def _seccion_montos(self, df: pd.DataFrame) -> dict:
        """Sección de filtros de monto"""
        st.sidebar.subheader("💰 Montos")
        
        if 'Monto' not in df.columns:
            return {}
        
        # Obtener rango de montos
        monto_min = float(df['Monto'].min())
        monto_max = float(df['Monto'].max())
        
        # Slider de rango
        rango_montos = st.sidebar.slider(
            "Rango de valores",
            min_value=monto_min,
            max_value=monto_max,
            value=(monto_min, monto_max),
            format="$%.0f",
            key='rango_montos'
        )
        
        # Filtro de monto mínimo absoluto
        monto_minimo_abs = st.sidebar.number_input(
            "Mostrar solo gastos > (valor absoluto)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            format="%.0f",
            key='monto_minimo_abs'
        )
        
        # Tipo de transacción
        tipo_transaccion = st.sidebar.radio(
            "Tipo de transacción",
            options=['Todos', 'Solo Gastos', 'Solo Ingresos'],
            index=0,
            key='tipo_transaccion'
        )
        
        return {
            'rango': rango_montos,
            'minimo_abs': monto_minimo_abs,
            'tipo': tipo_transaccion
        }
    
    def _aplicar_filtros(self, df: pd.DataFrame, fecha_filtro: dict, 
                         grupos_filtro: List[str], categorias_filtro: List[str],
                         monto_filtro: dict) -> pd.DataFrame:
        """Aplica todos los filtros al DataFrame"""
        df_filtrado = df.copy()
        
        # Filtrar por fecha
        if fecha_filtro and 'Fecha' in df_filtrado.columns:
            rango = fecha_filtro.get('rango')
            if rango and len(rango) == 2:
                df_filtrado = df_filtrado[
                    (df_filtrado['Fecha'] >= pd.Timestamp(rango[0])) &
                    (df_filtrado['Fecha'] <= pd.Timestamp(rango[1]))
                ]
            
            if fecha_filtro.get('años'):
                df_filtrado = df_filtrado[df_filtrado['Año'].isin(fecha_filtro['años'])]
            
            if fecha_filtro.get('meses'):
                df_filtrado = df_filtrado[df_filtrado['Mes'].isin(fecha_filtro['meses'])]
        
        # Filtrar por grupos
        if grupos_filtro and 'Grupo' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Grupo'].isin(grupos_filtro)]
        
        # Filtrar por categorías
        if categorias_filtro and 'Categoria_Principal' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Categoria_Principal'].isin(categorias_filtro)]
        
        # Filtrar por montos
        if monto_filtro and 'Monto' in df_filtrado.columns:
            # Rango
            if monto_filtro.get('rango'):
                rango = monto_filtro['rango']
                df_filtrado = df_filtrado[
                    (df_filtrado['Monto'] >= rango[0]) &
                    (df_filtrado['Monto'] <= rango[1])
                ]
            
            # Mínimo absoluto
            if monto_filtro.get('minimo_abs', 0) > 0:
                df_filtrado = df_filtrado[
                    df_filtrado['Monto'].abs() >= monto_filtro['minimo_abs']
                ]
            
            # Tipo de transacción
            tipo = monto_filtro.get('tipo', 'Todos')
            if tipo == 'Solo Gastos':
                df_filtrado = df_filtrado[df_filtrado['Monto'] < 0]
            elif tipo == 'Solo Ingresos':
                df_filtrado = df_filtrado[df_filtrado['Monto'] > 0]
        
        return df_filtrado
    
    def _seccion_filtros_guardados(self):
        """Sección para guardar y cargar filtros predefinidos"""
        from utils.filter_manager import FilterManager
        
        with st.sidebar.expander("💾 Filtros Guardados", expanded=False):
            filter_mgr = FilterManager()
            
            # Cargar filtros disponibles
            nombres_filtros = filter_mgr.listar_nombres_filtros()
            
            # Sección: Guardar filtro actual
            st.markdown("**Guardar Filtro Actual**")
            nombre_nuevo = st.text_input(
                "Nombre del filtro",
                placeholder="Ej: Gastos Q1 2024",
                key="nombre_filtro_nuevo",
                label_visibility="collapsed"
            )
            
            if st.button("💾 Guardar", use_container_width=True, key="btn_guardar_filtro"):
                if nombre_nuevo and nombre_nuevo.strip():
                    # Recopilar filtros actuales de session_state
                    filtros_actuales = {
                        'rango_fechas': st.session_state.get('rango_fechas'),
                        'años_seleccionados': st.session_state.get('años_seleccionados', []),
                        'meses_seleccionados': st.session_state.get('meses_seleccionados', []),
                        'gastos_grupos': st.session_state.get('gastos_grupos', []),
                        'ingresos_grupos': st.session_state.get('ingresos_grupos', []),
                        'todos_grupos': st.session_state.get('todos_grupos', False),
                        'cats_gastos': st.session_state.get('cats_gastos', []),
                        'cats_ingresos': st.session_state.get('cats_ingresos', []),
                        'monto_minimo': st.session_state.get('monto_minimo', 0),
                        'monto_maximo': st.session_state.get('monto_maximo', 0),
                        'monto_minimo_abs': st.session_state.get('monto_minimo_abs', 0),
                        'tipo_transaccion': st.session_state.get('tipo_transaccion', 'Todos')
                    }
                    
                    if filter_mgr.guardar_filtro(nombre_nuevo.strip(), filtros_actuales):
                        st.success(f"✅ Filtro '{nombre_nuevo.strip()}' guardado")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar filtro")
                else:
                    st.warning("⚠️ Ingresa un nombre para el filtro")
            
            # Sección: Cargar filtro guardado
            if nombres_filtros:
                st.markdown("---")
                st.markdown("**Cargar Filtro Guardado**")
                
                filtro_seleccionado = st.selectbox(
                    "Seleccionar filtro",
                    options=[""] + nombres_filtros,
                    key="filtro_a_cargar",
                    label_visibility="collapsed"
                )
                
                col1, col2 = st.columns(2)
                
                if col1.button("📂 Cargar", use_container_width=True, disabled=not filtro_seleccionado):
                    filtros_cargados = filter_mgr.cargar_filtro(filtro_seleccionado)
                    if filtros_cargados:
                        filter_mgr.aplicar_filtros_a_session_state(filtros_cargados)
                        filter_mgr.marcar_filtro_como_usado(filtro_seleccionado)
                        st.success(f"✅ Filtro '{filtro_seleccionado}' cargado")
                        st.rerun()
                    else:
                        st.error("❌ Error al cargar filtro")
                
                if col2.button("🗑️ Eliminar", use_container_width=True, disabled=not filtro_seleccionado):
                    if filter_mgr.eliminar_filtro(filtro_seleccionado):
                        st.success(f"✅ Filtro '{filtro_seleccionado}' eliminado")
                        st.rerun()
                    else:
                        st.error("❌ Error al eliminar filtro")
            else:
                st.info("💡 No hay filtros guardados aún")
