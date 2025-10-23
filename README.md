# 💰 Análisis de Gastos Personales

Dashboard interactivo desarrollado con **Streamlit** para analizar gastos e ingresos personales a partir de archivos CSV.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

> 🚀 **[Guía de Inicio Rápido](docs/QUICKSTART.md)** - ¡Ejecuta la app en menos de 5 minutos!

## 📋 Características

- ✅ **Carga de datos flexible**: Soporta CSV en formato wide (categorías como filas, períodos como columnas)
- ✅ **Clasificación automática**: Identifica grupos (Básico, Discrecional, Necesario, Ingresos) mediante reglas configurables
- ✅ **Filtros avanzados**: Por fecha, grupo, categoría y monto
- ✅ **Visualizaciones interactivas**: 10+ tipos de gráficos con Plotly
- ✅ **Tablas dinámicas**: Pivot tables con formato condicional
- ✅ **Exportación**: Descarga resultados en CSV
- ✅ **Configuración mediante YAML**: Fácil de extender y personalizar
- ✅ **Score de Salud Financiera**: Métricas clave e insights automáticos

## 🎯 Dashboards Principales

1. **🏠 Home** - Vista general y bienvenida
2. **📊 Explorador de Datos** - Análisis detallado con tablas pivot
3. **📈 Dashboard Financiero** - Visualizaciones interactivas con Plotly
4. **🎯 Salud Financiera** - Score, métricas clave e insights automáticos

## 🏗️ Estructura del Proyecto

4. **🎯 Salud Financiera** - Métricas clave y score de salud financiera

```

### 🔑 Funcionalidades Destacadasexpense_analysis_app/

├── config/

#### Análisis Financiero│   └── categories_config.yaml     # Configuración de grupos y reglas

- ✅ **Score de Salud Financiera** (0-100) con componentes ponderados├── data/

- ✅ **Tasa de Ahorro** con gauge visual y recomendaciones│   └── categories_timeline.csv    # CSV de ejemplo

- ✅ **Runway de Emergencia** - Meses de supervivencia con ahorros actuales├── utils/

- ✅ **Distribución de Gastos** - Necesarios/Básicos/Discrecionales vs Ideal│   ├── config_loader.py          # Carga configuración

- ✅ **Top 5 Gastos** más altos del período│   ├── category_classifier.py     # Clasifica categorías

- ✅ **Insights Automáticos** con recomendaciones personalizadas│   ├── data_loader.py            # Carga y transforma CSV

│   └── formatters.py             # Formato de moneda y fechas

#### Visualizaciones├── components/

- 📈 Evolución temporal de ingresos y gastos│   ├── charts.py                 # Gráficos Plotly

- 🥧 Distribución por grupos y categorías│   └── sidebar.py                # Filtros sidebar

- 📊 Comparaciones período a período├── pages/

- 🏆 Rankings de categorías con promedios│   ├── 1_📊_Explorador.py        # Página de tablas

- 📉 Gráficos de área apilados│   └── 2_📈_Dashboard.py         # Página de gráficos

- 🎯 Gauges (velocímetros) para métricas clave├── app.py                        # Aplicación principal

├── Pipfile                       # Dependencias

#### Sistema de Filtros└── README.md                     # Este archivo

- 📅 Filtros por fecha con selector de rango```

- 📅 Filtros por años y meses múltiples

- 🏷️ Filtros por grupos (Necesarios, Básicos, Discrecionales, Ingresos)## 🚀 Instalación

- 🔖 Filtros por categorías principales

- 💰 Filtros por rangos de monto### Prerrequisitos

- 💾 **Persistencia de filtros** - Guardar/cargar/eliminar presets con nombres

- 🔄 Sincronización entre páginas- Python 3.11 o superior

- pipenv

#### UI/UX

- 🎨 Dropdowns con contraste mejorado para tema oscuro### Pasos

- 📊 Balance visual con estados (Superávit/Déficit/Equilibrado)

- 🌈 Colores semánticos según tipo de transacción1. **Clonar o descargar el proyecto**

- 📱 Diseño responsive adaptable

```bash

## 🏗️ Arquitectura del Proyectocd expense_analysis_app

```

```

expense_analysis_app/2. **Instalar dependencias con pipenv**

├── app.py                          # Página principal (Home)

├── pages/                          # Páginas de la app```powershell

│   ├── 1_📊_Explorador.py         # Explorador de datos con pivotpipenv install

│   ├── 2_📈_Dashboard.py          # Dashboard con gráficos```

│   └── 3_🎯_Salud_Financiera.py  # Métricas de salud financiera

├── components/                     # Componentes reutilizables3. **Activar el entorno virtual**

│   ├── sidebar.py                 # Sidebar con filtros

│   └── charts.py                  # Builder de gráficos Plotly```powershell

├── utils/                          # Utilidades y helperspipenv shell

│   ├── data_loader.py             # Carga y transformación de CSV```

│   ├── config_loader.py           # Carga de configuración YAML

│   ├── category_classifier.py     # Clasificación de categorías4. **Copiar tu archivo CSV**

│   ├── formatters.py              # Formateo de moneda y valores

│   └── filter_manager.py          # Persistencia de filtrosColoca tu archivo CSV en la carpeta `data/` con el nombre `categories_timeline.csv`, o súbelo desde la interfaz.

├── config/                         # Configuración

│   ├── categories_config.yaml     # Jerarquía de categorías y grupos**Formato esperado del CSV:**

│   └── saved_filters.json         # Filtros guardados por el usuario

└── data/                           # Datos```csv

    └── categories_timeline.csv    # Dataset en formato wide"Categorías","1/1/2024-31/1/2024","1/2/2024-29/2/2024",...

```"B-Transporte",-50000,-60000,...

"N-Alimentación",-80000,-75000,...

## 📋 Estructura de Grupos y Categorías"Sueldo",200000,220000,...

```

### Gastos

## ▶️ Ejecución

**🟣 Necesarios (N-)** - Gastos indispensables para vivir (Ideal: 50%)

- N-Alimentación### Ejecutar la aplicación

- N-Salud

- N-Vivienda```powershell

- N-Obligaciones Legalesstreamlit run app.py

```

**🔵 Básicos (B-)** - Gastos esenciales del hogar (Ideal: 30%)

- B-Cuidado PersonalLa aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

- B-Educación

- B-Entretenimiento y Recreación## 📊 Uso de la Aplicación

- B-Servicios Financieros

- B-Transporte### Página Principal (Home)



**🟠 Discrecionales (D-)** - Gastos opcionales (Ideal: 20%)- Muestra resumen general de datos cargados

- D-Gustos y Extras- KPIs principales: Total Ingresos, Gastos, Ganancia Neta

- D-Muebles y Otros- Información de navegación

- D-Viajes y Vacaciones

- D-Donación/Caridad### 📊 Explorador de Datos



### Ingresos**Funcionalidades:**



**🟢 Ingreso Regular (R-)**1. **Filtros en Sidebar:**

- R-Sueldo   - 📅 Fechas: Rango, años, meses (con atajos 3M, 6M, 1A)

- R-Ingreso Pasivo   - 🏷️ Grupos: Básico, Discrecional, Necesario, Ingresos, Especiales

   - 📊 Categorías: Búsqueda y selección múltiple

**🟢 Ingreso Ocasional (O-)**   - 💰 Montos: Rango, mínimo absoluto, tipo de transacción

- O-Ingreso Extra   

   > 💡 **Nota**: Los filtros persisten automáticamente al cambiar entre páginas (Explorador ↔ Dashboard)

### Especiales (sin prefijo)

- Inversiones2. **Tabs de Visualización:**

- Préstamos   - **Tabla Pivot**: Vista matricial categorías × períodos

- TrabajoClientes   - **Vista Detallada**: Listado de transacciones

- Otros   - **Resumen por Grupo**: Agregación con porcentajes



## 🚀 Instalación y Uso3. **Exportación**: Descarga CSV de cualquier vista



### Requisitos### 📈 Dashboard de Análisis

- Python 3.9+

- pipenv (recomendado) o pip**Funcionalidades:**



### Instalación1. **🎯 Visión General:**

   - Gráfico de dona: Distribución por grupo

```bash   - Gráfico waterfall: Flujo Ingresos → Gastos

# Clonar repositorio   - Líneas: Ingresos vs Gastos mensual

git clone https://github.com/[tu-usuario]/expense_analysis_app.git

cd expense_analysis_app2. **📈 Evolución Temporal:**

   - Líneas: Evolución de gastos por grupo

# Instalar dependencias con pipenv   - Área apilada: Composición temporal

pipenv install   - Barras apiladas: Distribución mensual



# O con pip3. **📊 Análisis de Categorías:**

pip install -r requirements.txt   - Pareto: Top 10 categorías más costosas

```   - Heatmap: Intensidad de gasto por período

   - Ranking: Tabla detallada de categorías

### Ejecución

4. **💵 Análisis de Ingresos:**

```bash   - Composición por fuente

# Con pipenv   - Evolución temporal

pipenv run streamlit run app.py   - Tabla resumen



# O con streamlit directamente5. **⚖️ Comparativas:**

streamlit run app.py   - Comparación entre grupos

```   - Concentración: Top 5 vs Resto



La aplicación se abrirá en `http://localhost:8501`## ⚙️ Configuración



## 📊 Formato de Datos### Personalizar Grupos y Categorías



### CSV de Entrada (Wide Format)Edita el archivo `config/categories_config.yaml`:



El archivo `data/categories_timeline.csv` debe tener el siguiente formato:```yaml

grupos:

```csv  nuevo_grupo:

Categorías,2023-01,2023-02,2023-03,...    codigo: "X"

N-Alimentación,150000,145000,160000,...    prefijo: "X-"

B-Transporte,80000,75000,82000,...    nombre: "Mi Grupo"

R-Sueldo,500000,500000,500000,...    descripcion: "Descripción del grupo"

```    color: "#FF5733"

    tipo: "gasto"  # o "ingreso"

- **Primera columna:** Nombre de la categoría (con prefijo)

- **Columnas siguientes:** Períodos en formato `YYYY-MM`reglas_clasificacion:

- **Valores:** Montos (negativos para gastos, positivos para ingresos)  - tipo: "prefijo"

    prioridad: 1

### Importación desde BlueCoins    patrones:

      - prefijo: "X-"

Si usas la app **BlueCoins**, puedes exportar el CSV con la estructura de categorías provista. La aplicación mapea automáticamente:        grupo: "nuevo_grupo"

```

- Prefijos B-, D-, N- para gastos

- Prefijos R-, O- para ingresos### Personalizar Formato de Moneda

- Categorías sin prefijo como "Especiales"

En `config/categories_config.yaml`:

Ver `docs/bluecoins-mapping.md` para detalles completos.

```yaml

## 🎨 Personalizaciónformato_moneda:

  simbolo: "$"        # Cambiar a "€", "USD", etc.

### Modificar Categorías  separador_miles: ","

  separador_decimal: "."

Edita `config/categories_config.yaml`:  decimales: 2

  posicion_simbolo: "antes"  # o "despues"

```yaml```

grupos:

  tu_nuevo_grupo:## 🎨 Estructura de Grupos Predefinidos

    codigo: "X"

    prefijo: "X-"### Grupos Principales

    nombre: "Tu Grupo"

    descripcion: "Descripción del grupo"| Código | Prefijo | Nombre | Tipo | Color |

    color: "#HEXCOLOR"|--------|---------|---------|------|-------|

    tipo: "gasto"  # o "ingreso" o "mixto"| B | B- | Básico | Gasto | 🔵 Azul |

| D | D- | Discrecional | Gasto | 🟠 Naranja |

jerarquia_categorias:| N | N- | Necesario | Gasto | 🟣 Morado |

  tu_nuevo_grupo:| I | - | Ingresos | Ingreso | 🟢 Verde |

    "X-Categoría Principal":| E | - | Especiales | Gasto | 🟡 Amarillo |

      grupo: "tu_nuevo_grupo"

      subcategorias:### Categorías Especiales

        - "Subcategoría 1"

        - "Subcategoría 2"- **Préstamos**: Pago préstamo, Préstamo a deber

```- **TrabajoClientes**: Compra materiales, Pago mano obra, etc.

- **Sueldo**: Consultoría, Infraestructura IT, etc.

### Ajustar Colores de Gráficos- **Otros**: Clasificados por signo (+ = Ingreso, - = Gasto)



Los colores se definen en `categories_config.yaml` y se usan automáticamente en todos los gráficos.## 📦 Dependencias



## 📈 Métricas Financieras```toml

[packages]

### Score de Salud Financiera (0-100)pandas = "*"

streamlit = "*"

El score se calcula con tres componentes:plotly = "*"

numpy = "*"

1. **Tasa de Ahorro (40%)** - % de ingresos ahorradospyyaml = "*"

   - 40 pts: ≥30%openpyxl = "*"

   - 30 pts: ≥20%python-dateutil = "*"

   - 20 pts: ≥10%```



2. **Runway de Emergencia (30%)** - Meses de supervivencia## 🐛 Troubleshooting

   - 30 pts: ≥6 meses

   - 20 pts: ≥3 meses### Error: "Archivo de configuración no encontrado"

   - 10 pts: ≥1 mes

Verifica que exista `config/categories_config.yaml`

3. **Balance de Categorías (30%)** - Cercanía al ideal 50/30/20

   - Compara tu distribución Necesarios/Básicos/Discrecionales vs ideal### Error: "No se pudo cargar el CSV"



### Categorías de Score- Verifica que el CSV esté en formato UTF-8

- Asegúrate de que la primera columna se llame "Categorías"

- 🟢 **80-100:** Excelente- Verifica que las fechas estén en formato "DD/MM/YYYY-DD/MM/YYYY"

- 🟢 **60-79:** Bueno

- 🟡 **40-59:** Regular### Los filtros no persisten al cambiar de página

- 🔴 **0-39:** Necesita Mejora

- Esto se resolvió en la versión actual usando `st.session_state`

## 🛠️ Tecnologías Utilizadas- Si experimentas problemas, prueba limpiar el caché del navegador

- Ver documentación en `CAMBIOS_PERSISTENCIA_FILTROS.md`

- **[Streamlit](https://streamlit.io/)** - Framework de aplicaciones web

- **[Plotly](https://plotly.com/python/)** - Gráficos interactivos### Warning: "Categorías duplicadas detectadas"

- **[Pandas](https://pandas.pydata.org/)** - Manipulación de datos

- **[PyYAML](https://pyyaml.org/)** - Configuración- El sistema detecta automáticamente nombres de categorías duplicados en el CSV

- **[Python-dateutil](https://dateutil.readthedocs.io/)** - Manejo de fechas- Renombra las categorías duplicadas para que sean únicas

- Ejemplo: "Mantenimiento" → "Mantenimiento Auto" / "Mantenimiento Casa"

## 📝 Próximas Características

### Los imports de Plotly/Streamlit no se resuelven en el editor

- [ ] Proyección de patrimonio a 5 años

- [ ] Goal tracking con progress barsEsto es normal si no has instalado las dependencias. Ejecuta:

- [ ] Detección automática de gastos recurrentes

- [ ] Análisis estacional con heatmap```powershell

- [ ] Comparación año vs añopipenv install

- [ ] Export de reportes en PDF```

- [ ] Modo multi-moneda

## 🔧 Desarrollo

## 🤝 Contribuciones

### Ejecutar en modo desarrollo

Las contribuciones son bienvenidas. Por favor:

```powershell

1. Fork el proyectostreamlit run app.py --server.runOnSave true

2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)```

3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)

4. Push a la branch (`git push origin feature/AmazingFeature`)### Agregar nuevas reglas de clasificación

5. Abre un Pull Request

1. Edita `config/categories_config.yaml`

## 📄 Licencia2. Agrega tu regla en `reglas_clasificacion`

3. Reinicia la aplicación (se recargará automáticamente)

Este proyecto está bajo la Licencia MIT.

## 📝 Notas

## 👤 Autor

- Los montos negativos representan **gastos**

**David** - Análisis de Finanzas Personales- Los montos positivos representan **ingresos**

- Las filas "Gastos", "Ingresos" y "Ganancia Neta" se excluyen del análisis detallado

## 🙏 Agradecimientos- Los filtros se aplican en cascada (fecha → grupo → categoría → monto)

- Los filtros persisten automáticamente entre páginas usando `st.session_state`

- Inspirado en aplicaciones como Mint, YNAB y Personal Capital- El sistema valida automáticamente duplicados en categorías al cargar el CSV

- Comunidad de Streamlit por el excelente framework

- BlueCoins por la estructura de categorías## 📚 Documentación Adicional



---- **`CAMBIOS_PERSISTENCIA_FILTROS.md`**: Detalles técnicos sobre la implementación de persistencia de filtros

- **`CAMBIOS_VALIDACION_DUPLICADOS.md`**: Información sobre la validación de categorías duplicadas

⭐ **Si este proyecto te resulta útil, considera darle una estrella en GitHub!**- **`data/README.md`**: Formato esperado del CSV y ejemplos


## 📄 Licencia

Este proyecto es de código abierto para uso personal.

## 👨‍💻 Autor

Desarrollado con ❤️ usando Python, Streamlit y Plotly.

---

💡 **Tip**: Usa el botón "🔄 Limpiar" en la barra lateral para resetear todos los filtros.
