# Pipeline ETL con esquema estrella (Semana 6)

Optativa III: Ciencia de Datos · UNE Plantel Centro

## Qué hace

| Archivo | Descripción |
|---|---|
| `ventas.csv` | Fuente de datos: 15 ventas (producto, categoría, precio, cantidad). Incluye a propósito una fila incompleta para probar la limpieza. |
| `etl.py` | Pipeline ETL principal (práctica). |
| `etl_api.py` | Tarea integradora: ETL que consume la API pública DummyJSON. |

## Fases del pipeline (`etl.py`)

**EXTRACT.** Lee `ventas.csv` con `pandas.read_csv` y lo convierte en un DataFrame.

**TRANSFORM.** Limpia espacios en texto, descarta filas sin precio o cantidad, crea la feature nueva `total = precio × cantidad` y construye el modelo dimensional: `dim_categoria` (categorías únicas con clave `cat_id`) y `fact_ventas` (métricas numéricas más la clave `cat_id`).

**LOAD.** Guarda ambas tablas en la base SQLite `almacen.db` con `DataFrame.to_sql`.

## Esquema estrella

```
            dim_categoria
           (cat_id, categoria)
                  │
                  │ cat_id
                  ▼
fact_ventas (producto, cat_id, precio, cantidad, total)
```

La tabla de hechos guarda lo que se mide (precio, cantidad, total); la dimensión da el contexto (a qué categoría pertenece cada venta). Así una consulta analítica solo necesita un JOIN.

## Cómo ejecutarlo

```bash
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install pandas
python etl.py
```

## Resultado de la consulta final

```
 categoria  num_ventas  unidades  ingresos
   Cómputo           4        19     46900
   Oficina           3        15     18400
     Audio           3        16     13950
Accesorios           2        24      7650
 Papelería           2        55      2850
```
![Salida del pipeline] (Salida.png)
## Tarea integradora (`etl_api.py`)

Extrae el catálogo completo de `https://dummyjson.com/products`, calcula `precio_final` (con descuento) y `valor_inventario`, y lo carga a `catalogo.db` en un esquema estrella con dos dimensiones (`dim_categoria`, `dim_marca`) y la tabla de hechos `fact_productos`. Requiere conexión a internet.
