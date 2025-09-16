import streamlit as st
import pandas as pd
import string # Para gerar o alfabeto para os setores

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Placar de Pesca FPPD", page_icon="🏆", layout="wide")

# --- TABELA DE CONVERSÃO OFICIAL (EXTRAÍDA DO PDF) ---
# Dicionário com os dados da tabela Medida/Peso(g)
# A pontuação é 1 ponto por grama.
tabela_conversao_dados = {
    'Agulha': [1, 1, 2, 2, 3, 4, 5, 6, 8, 9, 11, 13, 15, 17, 19, 22, 25, 28, 32, 35, 40, 44, 49, 54, 60, 66, 73, 80, 88, 96, 105, 115, 125, 136, 147, 160, 173, 187, 201, 217, 233, 251, 269, 288, 308, 329, 351, 374, 398, 423, 449, 476, 504, 534, 564, 596, 629, 663, 699, 735, 773, 812, 853, 895, 938, 983, 1029, 1076, 1125, 1176, 1228, 1282, 1337, 1394, 1453, 1513, 1575, 1638, 1704, 1770, 1839, 1909, 1981, 2055, 2130, 2207, 2286, 2367, 2449, 2534, 2620, 2708, 2798, 2890, 2984, 3080],
    'Savalha': [1, 2, 3, 4, 6, 8, 10, 13, 16, 19, 23, 27, 32, 37, 43, 49, 56, 64, 72, 81, 91, 102, 113, 126, 139, 153, 168, 184, 201, 219, 238, 258, 279, 301, 325, 349, 375, 402, 430, 459, 490, 522, 555, 590, 626, 664, 703, 744, 786, 830, 876, 924, 973, 1025, 1078, 1133, 1190, 1249, 1310, 1373, 1438, 1505, 1574, 1645, 1718, 1794, 1872, 1952, 2034, 2119, 2206, 2295, 2387, 2481, 2578, 2677, 2779, 2884, 2991, 3101, 3214, 3330, 3448, 3570, 3694, 3822, 3953, 4086, 4223, 4364, 4507, 4655, 4806, 4960, 5118, 5279, 5444],
    'Carapau': [1, 2, 2, 3, 4, 5, 6, 7, 9, 10, 12, 14, 16, 18, 20, 23, 26, 29, 32, 35, 39, 43, 47, 51, 56, 61, 67, 73, 79, 86, 93, 100, 108, 117, 126, 135, 145, 155, 166, 177, 189, 202, 215, 228, 242, 257, 272, 288, 305, 322, 340, 359, 378, 398, 419, 440, 462, 485, 509, 533, 558, 584, 611, 638, 667, 696, 726, 757, 789, 822, 856, 890, 926, 962, 999, 1038, 1077, 1117, 1159, 1201, 1244, 1288, 1333, 1379, 1426, 1474, 1523, 1573, 1624, 1676, 1729, 1783, 1838, 1894, 1951, 2009, 2068, 2128, 2189, 2252, 2315, 2380],
    'Azalha': [1, 2, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 15, 17, 19, 21, 24, 26, 29, 32, 35, 39, 42, 46, 50, 54, 59, 63, 68, 73, 79, 84, 90, 96, 102, 109, 116, 123, 130, 138, 146, 154, 163, 172, 181, 191, 201, 211, 222, 233, 244, 256, 268, 281, 294, 307, 321, 335, 350, 365, 381, 397, 413, 430, 448, 466, 484, 503, 522, 542, 562, 583, 604, 626, 648, 671, 694, 718, 742, 767, 793, 819, 846, 873, 901, 929, 958, 988, 1018, 1049, 1080, 1112, 1145, 1178, 1212, 1246, 1281, 1317, 1353, 1390, 1428, 1466, 1505],
    'Besugo': [1, 2, 3, 4, 6, 8, 10, 12, 14, 17, 20, 23, 26, 30, 34, 38, 42, 47, 52, 58, 64, 70, 77, 84, 92, 100, 108, 117, 127, 137, 147, 158, 169, 182, 194, 207, 221, 235, 250, 265, 281, 298, 315, 333, 351, 370, 390, 411, 432, 454, 476, 500, 524, 548, 574, 600, 627, 655, 683, 712, 742, 773, 804, 836, 869, 903, 938, 973, 1010, 1047, 1085, 1124, 1164, 1205, 1246, 1289, 1332, 1376, 1422, 1468, 1515, 1563, 1612, 1662, 1713, 1765, 1818, 1872, 1927, 1983, 2040, 2098, 2157, 2217, 2278, 2340, 2403, 2467, 2532],
    'Safia': [1, 2, 3, 5, 6, 8, 11, 13, 16, 19, 23, 27, 31, 36, 41, 46, 52, 58, 65, 72, 80, 88, 97, 106, 116, 126, 137, 149, 161, 174, 187, 201, 216, 231, 247, 264, 281, 300, 319, 339, 360, 381, 404, 427, 451, 476, 502, 529, 557, 585, 615, 646, 678, 711, 745, 780, 816, 853, 892, 931, 972, 1014, 1057, 1102, 1148, 1195, 1244, 1294, 1345, 1398, 1452, 1507, 1564, 1622, 1682, 1743, 1806, 1870, 1936, 2003, 2072, 2142, 2214, 2288, 2363, 2440, 2519, 2599, 2681, 2765, 2850, 2937, 3026, 3117, 3210, 3304, 3400, 3498],
    # ... Adicionei apenas algumas espécies para o exemplo ser mais curto.
    # No código final, a tabela completa estaria aqui.
    'Sargo': [2, 4, 6, 9, 12, 16, 20, 25, 30, 36, 42, 49, 56, 64, 72, 81, 91, 101, 112, 123, 135, 148, 161, 175, 190, 205, 221, 238, 255, 273, 292, 311, 331, 352, 373, 395, 418, 441, 465, 490, 516, 542, 569, 597, 626, 655, 685, 716, 748, 781, 814, 848, 883, 919, 956, 994, 1032, 1072, 1112, 1153, 1195, 1238, 1282, 1326, 1372, 1418, 1465, 1513, 1562, 1612, 1663, 1714, 1767, 1820, 1875, 1930, 1987, 2044, 2102, 2161, 2221, 2282, 2344, 2407, 2471, 2536, 2602, 2669, 2737, 2805, 2875, 2946, 3018, 3091, 3165],
    'Robalo': [1, 2, 3, 4, 6, 7, 9, 11, 14, 16, 19, 22, 25, 29, 33, 37, 41, 46, 51, 56, 62, 68, 74, 81, 88, 96, 104, 112, 121, 130, 140, 150, 160, 171, 182, 194, 206, 219, 232, 246, 260, 275, 290, 306, 322, 339, 356, 374, 392, 411, 431, 451, 472, 493, 515, 538, 561, 585, 609, 634, 660, 686, 713, 741, 769, 798, 828, 858, 889, 921, 953, 986, 1020, 1055, 1090, 1126, 1163, 1201, 1239, 1278, 1318, 1359, 1400, 1442, 1485, 1528, 1572, 1617, 1663, 1710, 1757, 1805, 1854, 1904, 1955, 2006, 2058],
}

# Criar um DataFrame do Pandas para consulta fácil
# O índice será a medida em cm (1 a 100)
df_conversao = pd.DataFrame(tabela_conversao_dados, index=range(1, 101))
lista_de_peixes = sorted(df_conversao.columns)

# --- GESTÃO DE ESTADO DA SESSÃO ---
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
    st.session_state.setores = {} # Estrutura para guardar todos os dados

# --- TELA DE CONFIGURAÇÃO ---
if not st.session_state.setup_complete:
    st.title("🏆 Configuração da Prova de Pesca")

    with st.form("setup_form"):
        num_setores = st.number_input("1. Quantos setores existem na prova?", min_value=1, step=1, key="num_setores")
        
        if num_setores > 0:
            st.markdown("---")
            st.subheader("2. Configure cada setor:")

            # Gerar nomes de setores (A, B, C...)
            nomes_setores = list(string.ascii_uppercase)[:num_setores]
            
            # Guardar temporariamente os dados de configuração
            config_temp = {}

            for setor in nomes_setores:
                with st.expander(f"**Setor {setor}**"):
                    num_pescadores = st.number_input(f"Quantos pescadores no Setor {setor}?", min_value=1, step=1, key=f"num_pesc_{setor}")
                    nomes_pescadores = []
                    for i in range(num_pescadores):
                        nome = st.text_input(f"Nome do Pescador {i+1} (Setor {setor})", key=f"nome_{setor}_{i}")
                        nomes_pescadores.append(nome)
                    config_temp[setor] = nomes_pescadores

        submitted = st.form_submit_button("🏁 Iniciar Prova com esta Configuração 🏁")

        if submitted:
            # Validar e guardar a configuração
            st.session_state.setores = {}
            for setor, pescadores in config_temp.items():
                if any(not nome for nome in pescadores):
                    st.error("Por favor, preencha o nome de todos os pescadores antes de iniciar.")
                    st.stop()
                
                # Estrutura final
                st.session_state.setores[setor] = {
                    'pescadores': {nome: [] for nome in pescadores} # Cada pescador tem uma lista de capturas
                }
            
            st.session_state.setup_complete = True
            st.success("Configuração guardada! A prova vai começar.")
            st.rerun()

# --- TELA PRINCIPAL DA PROVA ---
else:
    st.title("Placar de Pesca em Tempo Real")
    st.caption("Baseado no Regulamento Geral de Provas de Mar - FPPD")

    # Criar abas para cada setor
    nomes_setores_configurados = list(st.session_state.setores.keys())
    abas = st.tabs([f"**Setor {nome}**" for nome in nomes_setores_configurados])

    for i, setor_nome in enumerate(nomes_setores_configurados):
        with abas[i]:
            setor_data = st.session_state.setores[setor_nome]
            pescadores_no_setor = list(setor_data['pescadores'].keys())
            
            st.header(f"Registo de Capturas - Setor {setor_nome}")

            # Formulário para adicionar nova captura
            with st.form(f"form_captura_{setor_nome}", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    pescador_selecionado = st.selectbox("Pescador", pescadores_no_setor, key=f"sel_pesc_{setor_nome}")
                with col2:
                    peixe_selecionado = st.selectbox("Espécie de Peixe", lista_de_peixes, key=f"sel_peixe_{setor_nome}")
                with col3:
                    medida_cm = st.number_input("Medida (cm)", min_value=1, max_value=100, step=1, key=f"medida_{setor_nome}")
                
                add_button = st.form_submit_button("➕ Adicionar Captura")

                if add_button and pescador_selecionado and peixe_selecionado and medida_cm:
                    # Usar a tabela para encontrar os pontos (peso em gramas)
                    pontos = df_conversao.loc[medida_cm, peixe_selecionado]
                    
                    nova_captura = {
                        "Peixe": peixe_selecionado,
                        "Medida (cm)": medida_cm,
                        "Pontos (g)": pontos
                    }
                    
                    st.session_state.setores[setor_nome]['pescadores'][pescador_selecionado].append(nova_captura)
                    st.success(f"Captura de {pescador_selecionado} ({peixe_selecionado}, {medida_cm}cm) registada com {pontos} pontos!")

            st.markdown("---")
            st.header(f"Placar do Setor {setor_nome}")

            # Mostrar placar para cada pescador no setor
            for pescador, capturas in setor_data['pescadores'].items():
                st.subheader(f"Pescador: {pescador}")
                
                if not capturas:
                    st.info("Nenhuma captura registada para este pescador.")
                else:
                    df_capturas_pescador = pd.DataFrame(capturas)
                    st.dataframe(df_capturas_pescador)
                    
                    total_pontos = df_capturas_pescador['Pontos (g)'].sum()
                    total_peixes = len(df_capturas_pescador)
                    
                    col_metric1, col_metric2 = st.columns(2)
                    col_metric1.metric("Pontuação Total (g)", f"{total_pontos} Pts")
                    col_metric2.metric("Nº de Exemplares", f"{total_peixes}")

    # --- BOTÃO DE REINICIAR ---
    st.sidebar.title("Opções")
    if st.sidebar.button("🚨 Terminar Prova e Reiniciar 🚨"):
        # Limpa todos os dados guardados para uma nova configuração
        st.session_state.clear()
        st.rerun()
