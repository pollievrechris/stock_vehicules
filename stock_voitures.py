import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# -------------------------------
# 🌍 Gestion multilingue
# -------------------------------
LANGUES = {
    "FR": {
        "title": "📦 Gestion du stock du Véhicule : Stock_Véhicules",
        "import_file": "📂 Importer un fichier Excel",
        "choose_file": "Choisir un fichier Excel",
        "import_success": "✅ Fichier importé avec succès !",
        "import_error": "Erreur lors de l'import : ",
        "tab_stock": "📋 Stock",
        "tab_movements": "📦 Entrées / Sorties",
        "tab_history": "📜 Historique",
        "add_item": "➕ Ajouter un élément manuellement",
        "add_button": "Ajouter au stock",
        "stock_now": "📋 Stock actuel",
        "download_stock": "💾 Télécharger le stock en Excel",
        "movement_barcode": "📦 Gestion par code-barres",
        "scan_barcode": "Scanner ou entrer le code-barres",
        "quantity": "Quantité",
        "location": "Localisation (ex: véhicule, client, dépôt)",
        "add_qty": "➕ Ajouter au stock",
        "remove_qty": "➖ Retirer du stock",
        "no_item": "⚠️ Aucun élément trouvé avec ce code-barres.",
        "removed_item": "ℹ️ L'article {code} a été supprimé car quantité = 0",
        "added_success": "✅ Ajout de {qte} unité(s) pour {code}",
        "removed_success": "✅ Retrait de {qte} unité(s) pour {code}",
        "history": "📜 Historique des mouvements",
        "download_history": "💾 Télécharger l’historique en Excel",
        "tool": "Outil",
        "yes": "Oui",
        "no": "Non",
    },
    "EN": {
        "title": "📦 Vehicle Stock Management : Stock_Véhicules",
        "import_file": "📂 Import an Excel file",
        "choose_file": "Choose an Excel file",
        "import_success": "✅ File imported successfully!",
        "import_error": "Error during import: ",
        "tab_stock": "📋 Stock",
        "tab_movements": "📦 In / Out",
        "tab_history": "📜 History",
        "add_item": "➕ Add an item manually",
        "add_button": "Add to stock",
        "stock_now": "📋 Current stock",
        "download_stock": "💾 Download stock as Excel",
        "movement_barcode": "📦 Manage with barcode",
        "scan_barcode": "Scan or enter barcode",
        "quantity": "Quantity",
        "location": "Location (ex: vehicle, client, warehouse)",
        "add_qty": "➕ Add to stock",
        "remove_qty": "➖ Remove from stock",
        "no_item": "⚠️ No item found with this barcode.",
        "removed_item": "ℹ️ Item {code} was removed because quantity = 0",
        "added_success": "✅ Added {qte} unit(s) for {code}",
        "removed_success": "✅ Removed {qte} unit(s) for {code}",
        "history": "📜 Movement history",
        "download_history": "💾 Download history as Excel",
        "tool": "Tool",
        "yes": "Yes",
        "no": "No",
    }
}

# -------------------------------
# Sélecteur de langue
# -------------------------------
lang_choice = st.sidebar.radio("🌍 Langue / Language", ["FR", "EN"])
TR = LANGUES[lang_choice]

# -------------------------------
# Colonnes
# -------------------------------
COLONNES_STOCK = [
    "Localisation",
    "Item N°",
    "Item Description",
    "Numéro de série",
    "Logistic Groupe",
    "Type de Produit",
    "Catégorie",
    "Quantité",
    "Emplacement dans la voiture",
    "Code-barres",
    "Code PR / Suivi",
    "Tool"
]

COLONNES_HISTORIQUE = [
    "Date",
    "Action",
    "Code-barres",
    "Code PR / Suivi",
    "Quantité",
    "Localisation"
]

# -------------------------------
# Config page
# -------------------------------
st.set_page_config(page_title="Gestion du stock", page_icon="🚗", layout="wide")
st.title(TR["title"])

# -------------------------------
# Connexion SQLite (OneDrive)
# -------------------------------
DB_PATH = r"C:\Users\chris\OneDrive\Documents\stock_voitures.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Création tables si absentes
cursor.execute('''
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Localisation TEXT,
    ItemNum TEXT,
    Description TEXT,
    NumeroSerie TEXT,
    LogisticGroupe TEXT,
    TypeProduit TEXT,
    Categorie TEXT,
    Quantite INTEGER,
    Emplacement TEXT,
    CodeBarres TEXT,
    CodePR TEXT,
    Tool TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS historique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT,
    Action TEXT,
    CodeBarres TEXT,
    CodePR TEXT,
    Quantite INTEGER,
    Localisation TEXT
)
''')
conn.commit()

# -------------------------------
# Chargement initial depuis SQLite
# -------------------------------
def charger_stock():
    return pd.read_sql("SELECT * FROM stock", conn)

def charger_historique():
    return pd.read_sql("SELECT * FROM historique", conn)

if "stock" not in st.session_state:
    st.session_state.stock = charger_stock()

if "historique" not in st.session_state:
    st.session_state.historique = charger_historique()

# -------------------------------
# Import Excel
# -------------------------------
st.sidebar.subheader(TR["import_file"])
fichier_import = st.sidebar.file_uploader(TR["choose_file"], type=["xlsx"])
if fichier_import is not None:
    try:
        df_import = pd.read_excel(fichier_import)
        for col in COLONNES_STOCK:
            if col not in df_import.columns:
                df_import[col] = "" if col != "Quantité" else 0
            if col == "Tool":
                df_import[col] = TR["no"]
        st.session_state.stock = df_import[COLONNES_STOCK]
        st.session_state.stock.to_sql("stock", conn, if_exists="replace", index=False)
        st.sidebar.success(TR["import_success"])
    except Exception as e:
        st.sidebar.error(f"{TR['import_error']}{e}")

# -------------------------------
# Onglets
# -------------------------------
onglet = st.tabs([TR["tab_stock"], TR["tab_movements"], TR["tab_history"]])

# -------------------------------
# Onglet Stock
# -------------------------------
with onglet[0]:
    st.subheader(TR["add_item"])
    with st.form("ajout_element"):
        infos = {}
        for col in COLONNES_STOCK:
            if col == "Quantité":
                infos[col] = st.number_input(col, min_value=0, step=1)
            elif col == "Tool":
                checked = st.checkbox(TR["tool"])
                infos[col] = TR["yes"] if checked else TR["no"]
            else:
                infos[col] = st.text_input(col)
        submitted = st.form_submit_button(TR["add_button"])

        if submitted:
            nouvelle_ligne = pd.DataFrame([infos])
            st.session_state.stock = pd.concat([st.session_state.stock, nouvelle_ligne], ignore_index=True)
            st.session_state.stock.to_sql("stock", conn, if_exists="replace", index=False)
            st.success("✅")

    st.subheader(TR["stock_now"])
    st.session_state.stock = st.data_editor(
        st.session_state.stock,
        num_rows="dynamic",
        use_container_width=True
    )
    st.session_state.stock.to_sql("stock", conn, if_exists="replace", index=False)

    if not st.session_state.stock.empty:
        fichier_export = "stock_voitures.xlsx"
        st.session_state.stock.to_excel(fichier_export, index=False)
        with open(fichier_export, "rb") as file:
            st.download_button(TR["download_stock"], file, fichier_export)

# -------------------------------
# Onglet Entrées / Sorties
# -------------------------------
with onglet[1]:
    if not st.session_state.stock.empty:
        st.subheader(TR["movement_barcode"])
        code_barres = st.text_input(TR["scan_barcode"])
        qte = st.number_input(TR["quantity"], min_value=1, step=1, value=1)
        localisation = st.text_input(TR["location"])

        col1, col2 = st.columns(2)

        # ✅ Entrée
        with col1:
            if st.button(TR["add_qty"]):
                code_pr = ""
                if code_barres in st.session_state.stock["Code-barres"].values:
                    idx = st.session_state.stock[st.session_state.stock["Code-barres"] == code_barres].index[0]
                    st.session_state.stock.at[idx, "Quantité"] += qte
                    code_pr = st.session_state.stock.at[idx, "Code PR / Suivi"]
                else:
                    st.warning(TR["no_item"])
                
                mouvement = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Action": "Entrée" if lang_choice=="FR" else "In",
                    "Code-barres": code_barres,
                    "Code PR / Suivi": code_pr,
                    "Quantité": qte,
                    "Localisation": localisation
                }])
                st.session_state.historique = pd.concat([st.session_state.historique, mouvement], ignore_index=True)
                st.session_state.stock.to_sql("stock", conn, if_exists="replace", index=False)
                st.session_state.historique.to_sql("historique", conn, if_exists="replace", index=False)
                st.success(TR["added_success"].format(qte=qte, code=code_barres))

        # ❌ Sortie
        with col2:
            if st.button(TR["remove_qty"]):
                code_pr = ""
                if code_barres in st.session_state.stock["Code-barres"].values:
                    idx = st.session_state.stock[st.session_state.stock["Code-barres"] == code_barres].index[0]
                    st.session_state.stock.at[idx, "Quantité"] -= qte
                    code_pr = st.session_state.stock.at[idx, "Code PR / Suivi"]
                    if st.session_state.stock.at[idx, "Quantité"] <= 0:
                        st.session_state.stock = st.session_state.stock.drop(idx).reset_index(drop=True)
                        st.info(TR["removed_item"].format(code=code_barres))
                else:
                    st.warning(TR["no_item"])
                
                mouvement = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Action": "Sortie" if lang_choice=="FR" else "Out",
                    "Code-barres": code_barres,
                    "Code PR / Suivi": code_pr,
                    "Quantité": qte,
                    "Localisation": localisation
                }])
                st.session_state.historique = pd.concat([st.session_state.historique, mouvement], ignore_index=True)
                st.session_state.stock.to_sql("stock", conn, if_exists="replace", index=False)
                st.session_state.historique.to_sql("historique", conn, if_exists="replace", index=False)
                st.success(TR["removed_success"].format(qte=qte, code=code_barres))

# -------------------------------
# Onglet Historique
# -------------------------------
with onglet[2]:
    st.subheader(TR["history"])
    st.dataframe(st.session_state.historique, use_container_width=True)

    if not st.session_state.historique.empty:
        fichier_histo = "historique_mouvements.xlsx"
        st.session_state.historique.to_excel(fichier_histo, index=False)
        with open(fichier_histo, "rb") as file:
            st.download_button(TR["download_history"], file, fichier_histo)
