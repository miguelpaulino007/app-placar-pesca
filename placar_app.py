# Nome do Ficheiro: placar_app.py

import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURAÇÃO DA FIREBASE ---
try:
    # A CORREÇÃO ESTÁ AQUI: convertemos o objeto para um dicionário
    cred_dict = dict(st.secrets["firebase_credentials"])
except Exception:
    st.error("As credenciais da Firebase não foram encontradas. Configure os 'Secrets' no Streamlit Cloud.")
    st.stop()

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- Configuração da Página e Atualização Automática ---
st.set_page_config(page_title="Placar de Pesca em Tempo Real", page_icon="🎣", layout="centered")
st_autorefresh(interval=15000, key="datarefresher") # Atualiza a cada 15 segundos

# --- Título ---
st.title("🎣 Placar de Pesca em Tempo Real")

# --- Sistema de Pontos (Pode editar aqui!) ---
sistema_de_pontos = {
    "Sargo": {"base": 15, "bonus_por_100g": 1},
    "Dourada": {"base": 25, "bonus_por_100g": 2},
    "Robalo": {"base": 40, "bonus_por_100g": 3},
    "Sardinha": {"base": 5, "bonus_por_100g": 1},
    "Peixe-Porco": {"base": 10, "bonus_por_100g": 1},
    "Choco": {"base": 20, "bonus_por_100g": 1.5},
}
lista_de_peixes = sorted(list(sistema_de_pontos.keys()))

# --- Formulário de Registo ---
with st.form("registo_peixe", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    peixe = col1.selectbox("Peixe", lista_de_peixes)
    peso = col2.number_input("Peso (g)", min_value=1, step=10)
    submitted = col3.form_submit_button("Adicionar")

    if submitted:
        info = sistema_de_pontos[peixe]
        pontos = round(info["base"] + (peso / 100) * info["bonus_por_100g"], 2)
        nova_captura = {"Peixe": peixe, "Peso (g)": peso, "Pontos": pontos, "timestamp": firestore.SERVER_TIMESTAMP}
        db.collection("capturas").add(nova_captura)
        st.success(f"{peixe} de {peso}g adicionado!")
        st_autorefresh(interval=1000, limit=1, key="imediato")

# --- Placar Geral ---
st.markdown("---")
st.subheader("Placar Geral")

docs = db.collection("capturas").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
capturas = [doc.to_dict() for doc in docs]

if capturas:
    df = pd.DataFrame(capturas)[["Peixe", "Peso (g)", "Pontos"]]
    st.dataframe(df)
    total_pontos = df["Pontos"].sum()
    st.metric("🏆 PONTUAÇÃO TOTAL", f"{total_pontos:.2f} Pontos")
else:
    st.info("Nenhuma captura registada ainda.")

# --- Botão para Limpar Placar ---
if st.button("🚨 Limpar Placar 🚨"):
    for doc in db.collection("capturas").stream():
        doc.reference.delete()
    st.success("Placar limpo!")
    st_autorefresh(interval=1000, limit=1, key="limpeza")
