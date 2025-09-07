import sqlite3, pandas as pd

conn = sqlite3.connect("stock_voitures.db")

print("\n--- Stock ---")
df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
print(df_stock.head())
print("Nombre de lignes :", len(df_stock))

print("\n--- Historique ---")
df_histo = pd.read_sql_query("SELECT * FROM historique", conn)
print(df_histo.head())
print("Nombre de lignes :", len(df_histo))

conn.close()
