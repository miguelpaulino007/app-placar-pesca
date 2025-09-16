import streamlit as st
import pandas as pd
import string

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Placar de Pesca FPPD", page_icon="🏆", layout="wide")

# --- CARREGAMENTO DOS DADOS ---
# Esta é a nova abordagem: ler o ficheiro CSV. É mais robusta e à prova de erros.
try:
    # O ficheiro CSV tem medidas de 1 a 100, mas o index do pandas começa em 0.
    # Por isso, subtraímos 1 à medida quando formos procurar o valor.
    df_conversao = pd.read_csv("tabela_pontos.csv")
    lista_de_peixes = sorted(df_conversao.columns)
except FileNotFoundError:
    st.error("ERRO CRÍTICO: O ficheiro 'tabela_pontos.csv' não foi encontrado no repositório do GitHub. Por favor, crie o ficheiro como indicado nas instruções.")
    st.stop()

# --- GESTÃO DE ESTADO DA SESSÃO ---
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
    st.session_state.setores = {}

# --- TELA DE CONFIGURAÇÃO ---
if not st.session_state.setup_complete:
    st.title("🏆 Configuração da Prova de Pesca")

    with st.form("setup_form"):
        num_setores = st.number_input("1. Quantos setores existem na prova?", min_value=1, step=1, key="num_setores")
        
        config_temp = {}
        if num_setores > 0:
            st.markdown("---")
            st.subheader("2. Configure cada setor:")
            nomes_setores = list(string.ascii_uppercase)[:num_setores]
            
            for setor in nomes_setores:
                with st.expander(f"**Setor {setor}**"):
                    num_pescadores = st.number_input(f"Quantos pescadores no Setor {setor}?", min_value=1, step=1, key=f"num_pesc_{setor}")
                    nomes_pescadores = []
                    if num_pescadores > 0:
                        for i in range(num_pescadores):
                            nome = st.text_input(f"Nome do Pescador {i+1} (Setor {setor})", key=f"nome_{setor}_{i}")
                            nomes_pescadores.append(nome)
                        config_temp[setor] = nomes_pescadores

        submitted = st.form_submit_button("🏁 Iniciar Prova com esta Configuração 🏁")

        if submitted:
            st.session_state.setores = {}
            valid = True
            if not config_temp:
                st.warning("Por favor, configure pelo menos um setor.")
                valid = False

            for setor, pescadores in config_temp.items():
                if not pescadores or any(not nome.strip() for nome in pescadores):
                    st.error(f"Por favor, preencha o nome de todos os pescadores no Setor {setor} antes de iniciar.")
                    valid = False
                    break
                st.session_state.setores[setor] = {'pescadores': {nome: [] for nome in pescadores}}
            
            if valid:
                st.session_state.setup_complete = True
                st.success("Configuração guardada! A prova vai começar.")
                st.rerun()

# --- TELA PRINCIPAL DA PROVA ---
else:
    st.title("Placar de Pesca em Tempo Real")
    st.caption("Baseado no Regulamento Geral de Provas de Mar - FPPD")

    nomes_setores_configurados = list(st.session_state.setores.keys())
    abas = st.tabs([f"**Setor {nome}**" for nome in nomes_setores_configurados])

    for i, setor_nome in enumerate(nomes_setores_configurados):
        with abas[i]:
            setor_data = st.session_state.setores[setor_nome]
            pescadores_no_setor = list(setor_data['pescadores'].keys())
            
            st.header(f"Registo de Capturas - Setor {setor_nome}")

            with st.form(f"form_captura_{setor_nome}", clear_on_submit=True):
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                pescador_selecionado = col1.selectbox("Pescador", pescadores_no_setor, key=f"sel_pesc_{setor_nome}", label_visibility="collapsed")
                peixe_selecionado = col2.selectbox("Espécie de Peixe", lista_de_peixes, key=f"sel_peixe_{setor_nome}", label_visibility="collapsed")
                medida_cm = col3.number_input("Medida (cm)", min_value=1, max_value=100, step=1, key=f"medida_{setor_nome}", label_visibility="collapsed", placeholder="cm")
                add_button = col4.form_submit_button("➕ Adicionar")

                if add_button and pescador_selecionado and peixe_selecionado and medida_cm:
                    # Acessar a linha correta (medida - 1) e a coluna (nome do peixe)
                    pontos = df_conversao.loc[medida_cm - 1, peixe_selecionado]
                    nova_captura = {"Peixe": peixe_selecionado, "Medida (cm)": medida_cm, "Pontos (g)": int(pontos)}
                    st.session_state.setores[setor_nome]['pescadores'][pescador_selecionado].append(nova_captura)
                    st.success(f"Captura de {pescador_selecionado} ({peixe_selecionado}, {medida_cm}cm) registada com {int(pontos)} pontos!")

            st.markdown("---")
            st.header(f"Placar do Setor {setor_nome}")

            placar_setor = []
            for pescador, capturas in setor_data['pescadores'].items():
                total_pontos = sum(c['Pontos (g)'] for c in capturas)
                placar_setor.append({'Pescador': pescador, 'Pontuação': total_pontos, 'Capturas': capturas})
            
            placar_setor_ordenado = sorted(placar_setor, key=lambda x: x['Pontuação'], reverse=True)

            for item in placar_setor_ordenado:
                pescador = item['Pescador']
                capturas = item['Capturas']
                total_pontos = item['Pontuação']

                with st.expander(f"**{pescador}** - Pontos: {total_pontos}", expanded=True):
                    if not capturas:
                        st.info("Nenhuma captura registada.")
                    else:
                        df_capturas_pescador = pd.DataFrame(capturas)
                        st.dataframe(df_capturas_pescador)
                        total_peixes = len(df_capturas_pescador)
                        
                        col_metric1, col_metric2 = st.columns(2)
                        col_metric1.metric("Pontuação Total (g)", f"{total_pontos} Pts")
                        col_metric2.metric("Nº de Exemplares", f"{total_peixes}")

    # --- BOTÃO DE REINICIAR ---
    st.sidebar.title("Opções")
    if st.sidebar.button("🚨 Terminar Prova e Reiniciar 🚨"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
