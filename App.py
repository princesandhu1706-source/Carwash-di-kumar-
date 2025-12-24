import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configurazione pagina
st.set_page_config(page_title="Gestionale Autolavaggio Pro", layout="wide")

DB_FILE = "registro_lavaggi.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # Assicuriamoci che la colonna data sia leggibile correttamente
        df['Data_Formattata'] = pd.to_datetime(df['Data e Ora'], dayfirst=True).dt.date
        return df
    return pd.DataFrame(columns=["Data e Ora", "Marca", "Tipo Lavaggio", "Importo", "Pagamento", "Data_Formattata"])

df = load_data()

st.title("🚗 Monitoraggio Autolavaggio 2025")

# --- BARRA LATERALE: INSERIMENTO ---
st.sidebar.header("Nuovo Lavaggio")

with st.sidebar.form("form_lavaggio", clear_on_submit=True):
    marche_auto = sorted([
        "Alfa Romeo", "Audi", "BMW", "Citroen", "Cupra", "Dacia", "DS", "Ferrari", "Fiat", 
        "Ford", "Honda", "Hyundai", "Jaguar", "Jeep", "Kia", "Lancia", "Land Rover", 
        "Lexus", "Maserati", "Mazda", "Mercedes-Benz", "MG", "Mini", "Mitsubishi", 
        "Nissan", "Opel", "Peugeot", "Porsche", "Renault", "Seat", "Skoda", "Smart", 
        "Suzuki", "Tesla", "Toyota", "Volkswagen", "Volvo", "Altro"
    ])
    
    marca = st.selectbox("Seleziona Marca", marche_auto)
    tipo_lavaggio = st.selectbox("Tipo Lavaggio", ["Solo dentro", "Solo fuori", "Dentro fuori", "Lavaggio sedili"])
    
    importi_base = ["8", "10", "15", "17", "18", "20", "25", "30", "80", "90", "Altro"]
    importo_scelto = st.selectbox("Importo (€)", importi_base)
    
    importo_finale = importo_scelto
    if importo_scelto == "Altro":
        importo_finale = st.number_input("Inserisci importo personalizzato", min_value=0, value=0)
    
    pagamento = st.selectbox("Metodo Pagamento", ["Contanti", "Satispay", "Carta di Credito"])
    
    submit = st.form_submit_button("Registra Lavaggio")

if submit:
    ora_attuale_dt = datetime.now()
    nuova_riga = {
        "Data e Ora": ora_attuale_dt.strftime("%d/%m/%Y %H:%M:%S"),
        "Marca": marca,
        "Tipo Lavaggio": tipo_lavaggio,
        "Importo": float(importo_finale),
        "Pagamento": pagamento,
        "Data_Formattata": ora_attuale_dt.date()
    }
    new_df = pd.DataFrame([nuova_riga])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.rerun()

# --- SEZIONE FILTRO GIORNALIERO ---
st.markdown("---")
st.header("🔍 Ricerca per Giorno")

# Seleziona la data da visualizzare (default oggi 24/12/2025)
data_selezionata = st.date_input("Scegli un giorno per vedere i lavaggi", datetime.now().date())

# Filtriamo i dati in base alla data scelta
df_filtrato = df[df['Data_Formattata'].astype(str) == str(data_selezionata)]

if not df_filtrato.empty:
    incasso_giorno = df_filtrato["Importo"].sum()
    auto_giorno = len(df_filtrato)
    
    col_a, col_b = st.columns(2)
    col_a.metric(f"Incasso del {data_selezionata.strftime('%d/%m/%Y')}", f"{incasso_giorno} €")
    col_b.metric(f"Auto lavate il {data_selezionata.strftime('%d/%m/%Y')}", auto_giorno)
    
    st.dataframe(df_filtrato[["Data e Ora", "Marca", "Tipo Lavaggio", "Importo", "Pagamento"]].iloc[::-1], use_container_width=True)
else:
    st.info(f"Nessun lavaggio registrato per il giorno {data_selezionata.strftime('%d/%m/%Y')}")

# --- GESTIONE ERRORI ---
st.sidebar.markdown("---")
st.sidebar.header("Gestione Errori")
if st.sidebar.button("CANCELLA ULTIMA AUTO"):
    if not df.empty:
        df = df.drop(df.index[-1])
        df.to_csv(DB_FILE, index=False)
        st.sidebar.warning("Ultima registrazione eliminata!")
        st.rerun()

# --- EXPORT ---
st.sidebar.markdown("---")
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Scarica Tutto (Excel/CSV)", csv, "registro_completo.csv", "text/csv")

