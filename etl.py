"""
Pipeline ETL - Semana 6 (Ingeniería de datos)
Fuente: ventas.csv  ->  Destino: almacen.db (SQLite, esquema estrella)
"""
import pandas as pd
import sqlite3

# ===================== EXTRACT =====================
# Leer los datos crudos desde la fuente (archivo CSV)
df = pd.read_csv("ventas.csv")
print(f"[EXTRACT] Extraídas {len(df)} filas")

# ==================== TRANSFORM ====================
# 1) Limpieza: quitar espacios y descartar filas con datos faltantes
df["producto"] = df["producto"].str.strip()
df["categoria"] = df["categoria"].str.strip()
filas_antes = len(df)
df = df.dropna(subset=["precio", "cantidad"])
df["cantidad"] = df["cantidad"].astype(int)
print(f"[TRANSFORM] Filas descartadas por datos incompletos: {filas_antes - len(df)}")

# 2) Feature nueva: ingreso total por venta
df["total"] = df["precio"] * df["cantidad"]

# 3) Modelado dimensional (esquema estrella)
#    Dimensión: categorías únicas con su clave sustituta
dim_categoria = pd.DataFrame({"categoria": sorted(df["categoria"].unique())})
dim_categoria["cat_id"] = range(1, len(dim_categoria) + 1)

#    Tabla de hechos: métricas numéricas + clave hacia la dimensión
fact = df.merge(dim_categoria, on="categoria")
fact_ventas = fact[["producto", "cat_id", "precio", "cantidad", "total"]]
print(f"[TRANSFORM] dim_categoria: {len(dim_categoria)} filas | fact_ventas: {len(fact_ventas)} filas")

# ======================= LOAD =======================
conn = sqlite3.connect("almacen.db")
dim_categoria.to_sql("dim_categoria", conn, if_exists="replace", index=False)
fact_ventas.to_sql("fact_ventas", conn, if_exists="replace", index=False)
print("[LOAD] Tablas cargadas en almacen.db")

# ========== Consulta analítica (estrella en acción) ==========
query = """
SELECT d.categoria,
       COUNT(*)      AS num_ventas,
       SUM(f.cantidad) AS unidades,
       SUM(f.total)  AS ingresos
FROM fact_ventas f
JOIN dim_categoria d ON f.cat_id = d.cat_id
GROUP BY d.categoria
ORDER BY ingresos DESC
"""
print("\nIngresos por categoría:")
print(pd.read_sql(query, conn).to_string(index=False))
conn.close()
