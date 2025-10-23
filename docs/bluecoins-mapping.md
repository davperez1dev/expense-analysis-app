# 📱 Mapeo de Categorías BlueCoins

Este documento describe cómo mapear las categorías exportadas desde la aplicación móvil **BlueCoins** al formato utilizado por Expense Analysis App.

## 🔄 Estructura de Exportación BlueCoins

BlueCoins organiza las transacciones en una jerarquía de 3 niveles:

```
TIPO (GASTOS / INGRESOS)
  └── Categoría Principal
      └── Subcategoría
```

## 📋 Mapeo Completo

### GASTOS

#### 🟣 Necesarios (N-) - Gastos Indispensables

| BlueCoins | Expense Analysis App | Subcategorías |
|-----------|---------------------|---------------|
| N-Alimentación | N-Alimentación | Comidas Varias |
| N-Obligaciones Legales | N-Obligaciones Legales | AFIP/Rentas |
| N-Salud | N-Salud | Actividad Física y Bienestar, Atención Médica, Medicamentos y Otros, Medicina Prepaga |
| N-Vivienda | N-Vivienda | Mantenimiento Casa, Servicios |

#### 🔵 Básicos (B-) - Gastos Esenciales del Hogar

| BlueCoins | Expense Analysis App | Subcategorías |
|-----------|---------------------|---------------|
| B-Cuidado Personal | B-Cuidado Personal | Aseo/Cosméticos, Ropa y Calzado |
| B-Educación | B-Educación | Cursos, Libros y Suministros, Recursos Online |
| B-Entretenimiento y Recreación | B-Entretenimiento y Recreación | Dispositivos Electrónico, Ocio/Comer Fuera, Servicios Nube |
| B-Servicios Financieros | B-Servicios Financieros | Administrativo |
| B-Transporte | B-Transporte | Combustible, Estacionamiento, Mantenimiento Auto, Transporte Público |

#### 🟠 Discrecionales (D-) - Gastos Opcionales

| BlueCoins | Expense Analysis App | Subcategorías |
|-----------|---------------------|---------------|
| D-Gustos y Extras | D-Gustos y Extras | Chucherias, Mascota, Regalos |
| D-Muebles y Otros | D-Muebles y Otros | Electrodomésticos, Herramientas, Muebles, Repuestos |
| D-Viajes y Vacaciones | D-Viajes y Vacaciones | Viajes |
| D-Donacion/Caridad | D-Donacion/Caridad | Donación varias |

#### ⚙️ Especiales (Sin Prefijo) - Categorías Contextuales

| BlueCoins | Expense Analysis App | Tipo | Subcategorías |
|-----------|---------------------|------|---------------|
| Inversiones | Inversiones | Mixto | Mineria-Cripto |
| Préstamos | Préstamos | Mixto | Pago préstamo sacado, Préstamo a Deber |
| TrabajoClientes | TrabajoClientes | Mixto | Cobro Deuda Ajuste Saldo, Compra Materiales para Avance trabajo, Pago Mano obra a tercero, Trabajo-Transporte |
| Otros | Otros | Mixto | Otros, Tarjeta Crédito Prestada Gastos |

### INGRESOS

#### 🟢 Ingreso Regular (R-) - Recurrentes y Predecibles

| BlueCoins | Expense Analysis App | Subcategorías |
|-----------|---------------------|---------------|
| R-Sueldo | R-Sueldo | Consultoria-Dev, Infraestructura IT, Negocio Familiar (Gestión y Soporte IT), Soporte técnico |
| R-IngresoPasivo | R-IngresoPasivo | Acciones, CEDEAR, Bonos, FCI, etc., Importe Pasivo Generado, Interés Préstamo Negocio Familiar |

#### 🟢 Ingreso Ocasional (O-) - Esporádicos No Recurrentes

| BlueCoins | Expense Analysis App | Subcategorías |
|-----------|---------------------|---------------|
| O-IngresoExtra | O-IngresoExtra | Venta Equipos/Componentes |

#### ⚙️ Otros Ingresos (Sin Prefijo)

| BlueCoins | Expense Analysis App | Subcategorías |
|-----------|---------------------|---------------|
| Otros | Otros | Otros, Anticipo p/ compra equipos/materiales, Devolución por Compra Equipos Gastados, Dinero pedido, Recibido en Cta para Pagar Algo, Otros Tarjeta Crédito Prestada Ingresos |

## 🔧 Proceso de Importación

### Paso 1: Exportar desde BlueCoins

1. Abre BlueCoins
2. Ve a **Menú** → **Exportar**
3. Selecciona formato **CSV**
4. Elige el rango de fechas
5. Descarga el archivo

### Paso 2: Transformar a Formato Wide

El CSV de BlueCoins viene en formato **long** (una fila por transacción):

```csv
Fecha,Categoría,Monto
2024-01-15,B-Transporte > Combustible,-50000
2024-01-15,R-Sueldo > Consultoria-Dev,500000
```

Debes transformarlo a formato **wide** (categorías como filas, períodos como columnas):

```csv
Categorías,2024-01,2024-02,2024-03
B-Transporte,-150000,-120000,-145000
R-Sueldo,500000,500000,500000
```

### Paso 3: Aplicar Convención de Prefijos

Asegúrate de que cada categoría tenga el prefijo correcto:

- **N-** para Necesarios
- **B-** para Básicos
- **D-** para Discrecionales
- **R-** para Ingreso Regular
- **O-** para Ingreso Ocasional
- **Sin prefijo** para Especiales (Inversiones, Préstamos, TrabajoClientes, Otros)

### Paso 4: Signos de Montos

- **Gastos:** Valores negativos (ej: -50000)
- **Ingresos:** Valores positivos (ej: 500000)

### Paso 5: Importar en Expense Analysis App

1. Guarda el CSV transformado en `data/categories_timeline.csv`
2. Ejecuta `streamlit run app.py`
3. La aplicación clasificará automáticamente las categorías según los prefijos

## 📊 Ejemplo de Transformación

**BlueCoins Export (Long Format):**

```csv
Fecha,Categoría,Subcategoría,Monto,Tipo
2024-01-05,B-Transporte,Combustible,-45000,Gasto
2024-01-10,N-Alimentación,Comidas Varias,-120000,Gasto
2024-01-31,R-Sueldo,Consultoria-Dev,500000,Ingreso
2024-02-05,B-Transporte,Combustible,-40000,Gasto
2024-02-10,N-Alimentación,Comidas Varias,-115000,Gasto
2024-02-28,R-Sueldo,Consultoria-Dev,500000,Ingreso
```

**Expense Analysis App Format (Wide):**

```csv
Categorías,2024-01,2024-02
B-Transporte,-45000,-40000
N-Alimentación,-120000,-115000
R-Sueldo,500000,500000
```

## 🎯 Reglas de Clasificación Automática

La aplicación utiliza las siguientes reglas en `config/categories_config.yaml`:

```yaml
grupos:
  necesario:
    prefijo: "N-"
    tipo: "gasto"
  
  basico:
    prefijo: "B-"
    tipo: "gasto"
  
  discrecional:
    prefijo: "D-"
    tipo: "gasto"
  
  ingreso_regular:
    prefijo: "R-"
    tipo: "ingreso"
  
  ingreso_ocasional:
    prefijo: "O-"
    tipo: "ingreso"
  
  especiales:
    prefijo: null  # Sin prefijo
    tipo: "mixto"  # Clasificado por signo del monto
```

## ❓ FAQ

### ¿Puedo usar nombres personalizados?

Sí, puedes editar `config/categories_config.yaml` para agregar o modificar categorías.

### ¿Qué pasa si no uso los prefijos?

Las categorías sin prefijo reconocido se clasificarán como "Especiales" y su tipo (gasto/ingreso) se determinará por el signo del monto.

### ¿Puedo tener subcategorías?

Sí, las subcategorías se definen en la jerarquía YAML. En el CSV, solo necesitas la categoría principal con prefijo.

### ¿Cómo manejo categorías mixtas?

Usa tipo `"mixto"` en la configuración. La aplicación clasificará cada transacción como gasto o ingreso según el signo del monto.

## 🛠️ Scripts de Ayuda

Próximamente agregaremos scripts Python para automatizar la conversión de BlueCoins export a formato wide.

---

📌 **Nota:** Esta documentación se basa en BlueCoins v11.x. Si usas una versión diferente, el formato de exportación puede variar ligeramente.
