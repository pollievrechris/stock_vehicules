import sqlite3
import pandas as pd

DB_PATH = "stock_voitures.db"

def afficher_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Liste les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("📋 Tables trouvées :", [t[0] for t in tables])

    for table in tables:
        print(f"\n--- Aperçu de {table[0]} ---")
        df = pd.read_sql_query(f"SELECT * FROM {table[0]} LIMIT 10", conn)
        print(df)

    conn.close()

if __name__ == "__main__":
    afficher_tables()
