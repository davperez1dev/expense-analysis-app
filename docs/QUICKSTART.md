# 🚀 Guía de Inicio Rápido

Esta guía te ayudará a tener la aplicación funcionando en menos de 5 minutos.

## 📋 Requisitos Previos

- **Python 3.9 o superior** ([Descargar aquí](https://www.python.org/downloads/))
- **Git** ([Descargar aquí](https://git-scm.com/downloads))
- **pipenv** (opcional pero recomendado)

### Verificar Instalación

```bash
python --version  # Debe mostrar Python 3.9+
git --version     # Debe mostrar Git 2.x+
```

## 🔧 Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/davperez1dev/expense-analysis-app.git
cd expense-analysis-app
```

### Paso 2: Instalar Dependencias

**Opción A: Con pipenv (Recomendado)**

```bash
# Instalar pipenv si no lo tienes
pip install pipenv

# Instalar dependencias del proyecto
pipenv install

# Activar el entorno virtual
pipenv shell
```

**Opción B: Con pip**

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install streamlit pandas plotly pyyaml python-dateutil
```

### Paso 3: Ejecutar la Aplicación

```bash
# Con pipenv
pipenv run streamlit run app.py

# O si estás dentro del entorno virtual
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📊 Preparar tus Datos

### Formato del CSV

El archivo debe estar en formato **wide** (categorías como filas, períodos como columnas):

```csv
Categorías,2024-01,2024-02,2024-03
N-Alimentación,-150000,-145000,-160000
B-Transporte,-80000,-75000,-82000
R-Sueldo,500000,500000,500000
```

### Ubicación del Archivo

Coloca tu archivo CSV en:
```
expense_analysis_app/
└── data/
    └── categories_timeline.csv  ← Aquí
```

### Convención de Nombres

Usa prefijos para clasificar automáticamente:

| Prefijo | Tipo | Ejemplo |
|---------|------|---------|
| `N-` | Necesarios | `N-Alimentación` |
| `B-` | Básicos | `B-Transporte` |
| `D-` | Discrecionales | `D-Viajes` |
| `R-` | Ingreso Regular | `R-Sueldo` |
| `O-` | Ingreso Ocasional | `O-IngresoExtra` |

**Importante:** Los gastos deben ser negativos (-) y los ingresos positivos (+)

## 🎯 Primeros Pasos

### 1. Explorar los Dashboards

- **🏠 Home**: Vista general del proyecto
- **📊 Explorador**: Tablas pivot y análisis detallado
- **📈 Dashboard**: Gráficos interactivos y visualizaciones
- **🎯 Salud Financiera**: Métricas clave y score

### 2. Aplicar Filtros

En el sidebar (izquierda) puedes filtrar por:
- 📅 Rango de fechas
- 📅 Años y meses específicos
- 🏷️ Grupos (Necesarios, Básicos, Discrecionales)
- 🔖 Categorías principales
- 💰 Rangos de monto

### 3. Guardar Filtros Favoritos

1. Configura tus filtros
2. Expande "💾 Filtros Guardados"
3. Escribe un nombre (ej: "Gastos Esenciales 2024")
4. Haz clic en "💾 Guardar"

Para cargar: selecciona el filtro y haz clic en "📂 Cargar"

## 🎨 Personalización

### Modificar Categorías

Edita `config/categories_config.yaml`:

```yaml
grupos:
  mi_grupo:
    codigo: "M"
    prefijo: "M-"
    nombre: "Mi Grupo Personalizado"
    color: "#FF6B6B"
    tipo: "gasto"
```

### Cambiar Colores de Gráficos

Los colores en `categories_config.yaml` se aplican automáticamente a todos los gráficos.

## ❓ Solución de Problemas

### Error: "Module not found"

```bash
# Reinstalar dependencias
pipenv install --dev
# o
pip install -r requirements.txt
```

### Error: "No such file or directory: categories_timeline.csv"

Asegúrate de que el archivo esté en `data/categories_timeline.csv`

### La aplicación no carga datos

1. Verifica que el CSV tenga el formato correcto (wide)
2. Revisa que las categorías tengan los prefijos correctos (N-, B-, D-, R-, O-)
3. Confirma que los montos tengan el signo correcto (- para gastos, + para ingresos)

### Filtros no se guardan

Los filtros se guardan en `config/saved_filters.json`. Asegúrate de tener permisos de escritura en esa carpeta.

## 📚 Recursos Adicionales

- **[README.md](../README.md)** - Documentación completa
- **[docs/bluecoins-mapping.md](./bluecoins-mapping.md)** - Integración con BlueCoins
- **[Documentación de Streamlit](https://docs.streamlit.io/)**

## 💡 Consejos Pro

1. **Usa filtros guardados**: Ahorra tiempo guardando tus vistas favoritas
2. **Revisa el Score de Salud**: Página "🎯 Salud Financiera" tiene métricas clave
3. **Compara períodos**: En Dashboard, usa la pestaña "Comparación" para ver evolución
4. **Top 5 Gastos**: Identifica rápidamente tus mayores gastos del período

## 🆘 Ayuda

Si encuentras problemas:

1. Revisa esta guía
2. Consulta el [README completo](../README.md)
3. Abre un [Issue en GitHub](https://github.com/davperez1dev/expense-analysis-app/issues)

---

✨ **¡Listo! Ya puedes empezar a analizar tus finanzas personales.**
