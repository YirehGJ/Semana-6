"""
Tarea integradora - Semana 6
Pipeline ETL que consume la API pública DummyJSON y carga a SQLite (esquema estrella).
Solo usa librería estándar + pandas.
"""
import json
import sqlite3
import urllib.request
import pandas as pd

URL = "https://dummyjson.com/products?limit=0"   # limit=0 => todos los productos

# ===================== EXTRACT =====================
with urllib.request.urlopen(URL, timeout=30) as resp:
    datos = json.load(resp)
df = pd.json_normalize(datos["products"])
print(f"[EXTRACT] {len(df)} productos desde la API")

# ==================== TRANSFORM ====================
df = df[["id", "title", "category", "brand", "price", "discountPercentage", "rating", "stock"]].copy()
df["brand"] = df["brand"].fillna("Sin marca")                 # algunos productos no traen marca
df = df.dropna(subset=["price", "stock"])
df["precio_final"] = (df["price"] * (1 - df["discountPercentage"] / 100)).round(2)  # feature nueva
df["valor_inventario"] = (df["precio_final"] * df["stock"]).round(2)               # feature nueva

dim_categoria = pd.DataFrame({"categoria": sorted(df["category"].unique())})
dim_categoria["cat_id"] = range(1, len(dim_categoria) + 1)

dim_marca = pd.DataFrame({"marca": sorted(df["brand"].unique())})
dim_marca["marca_id"] = range(1, len(dim_marca) + 1)

fact = (df.merge(dim_categoria, left_on="category", right_on="categoria")
          .merge(dim_marca, left_on="brand", right_on="marca"))
fact_productos = fact[["id", "title", "cat_id", "marca_id", "price",
                       "discountPercentage", "precio_final", "rating", "stock", "valor_inventario"]]

# ======================= LOAD =======================
conn = sqlite3.connect("catalogo.db")
dim_categoria.to_sql("dim_categoria", conn, if_exists="replace", index=False)
dim_marca.to_sql("dim_marca", conn, if_exists="replace", index=False)
fact_productos.to_sql("fact_productos", conn, if_exists="replace", index=False)
print("[LOAD] catalogo.db lista")

query = """
SELECT c.categoria, COUNT(*) AS productos,
       ROUND(AVG(f.rating), 2) AS rating_prom,
       ROUND(SUM(f.valor_inventario), 2) AS valor_inventario
FROM fact_productos f
JOIN dim_categoria c ON f.cat_id = c.cat_id
GROUP BY c.categoria
ORDER BY valor_inventario DESC
LIMIT 10
"""
print(pd.read_sql(query, conn).to_string(index=False))
conn.close()
