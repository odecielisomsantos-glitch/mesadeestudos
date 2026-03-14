import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

st.set_page_config(page_title="Foco na Missão", layout="wide")

# CSS Avançado: Esconde barra superior nativa e ajusta fontes
st.markdown("""<style>
    /* Esconde a barra branca nativa do topo e o menu */
    header {visibility: hidden;}
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main {background-color: #0E1117 !important;}
    
    /* Fontes maiores e mais brancas para leitura clara */
    h3, p, span, label, div {color: #FFFFFF !important; font-family: 'sans serif';}
    .top-bar {background-color: #1E1E1E; padding: 15px; border-radius: 8px; border: 1px solid #4CAF50; margin-top: -50px;}
    .top-title {color: #4CAF50 !important; font-weight: bold; font-size: 22px; margin-left: 10px;}
    
    /* Cards com texto bem destacado */
    .card {background: #1E1E1E; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;}
    .c-label {color: #BBBBBB !important; font-size: 14px; font-weight: bold;}
    .c-value {color: #FFFFFF !important; font-size: 30px; font-weight: bold; margin: 5px 0;}
    .c-footer {color: #4CAF50 !important; font-size: 14px; font-weight: bold;}
    
    /* Ajuste de inputs para não sumirem no escuro */
    input, select, textarea {background-color: #1E1E1E !important; color: white !important;}
</style>""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.write("### ")
    menu = option_menu(
        None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Ranking", "Conquistas", "Perfil"],
        icons=["grid-1x2", "pencil-square", "stopwatch", "graph-up-arrow", "file-earmark-text", "trophy", "award", "person"],
        styles={
            "container": {"background-color": "#0E1117"},
            "nav-link": {"font-size": "16px", "color": "#FFF", "text-align": "left"},
            "nav-link-selected": {"background-color": "#1E1E1E", "color": "#4CAF50", "border-left": "4px solid #4CAF50", "border-radius": "0px"}
        }
    )
    st.markdown("---")
    st.markdown("<span style='color:#4CAF50'>●</span> Acesso Completo", unsafe_allow_html=True)

# --- CABEÇALHO ESCURO (Substitui a barra branca) ---
st.markdown('<div class="top-bar"><span class="top-title">🎯 FOCO NA MISSÃO</span></div>', unsafe_allow_html=True)

# --- CONTEÚDO ---
if menu == "Dashboard":
    st.write(" ")
    st.markdown("## Olá, Guerreiro! 👋")
    
    cols = st.columns(3)
    metrics = [("HORAS NA SEMANA", "7h 5min", "Meta: 30h"), ("QUESTÕES", "162", "75% acerto"), ("GERAL", "80%", "1866 quest.")]
    
    for col, (tit, val, foot) in zip(cols, metrics):
        col.markdown(f'''<div class="card">
            <div class="c-label">{tit}</div>
            <div class="c-value">{val}</div>
            <div class="c-footer">{foot}</div>
        </div>''', unsafe_allow_html=True)

    st.write("---")
    st.markdown("### Progresso Semanal")
    st.progress(0.24)
    
    # Gráfico ajustado: o segredo é usar o tema do Streamlit
    st.markdown("### Horas por Dia")
    df = pd.DataFrame({'Dia': ['Seg','Ter','Qua','Qui','Sex','Sab','Dom'], 'Horas': [1, 2.5, 4, 1.5, 0, 0, 0]})
    st.bar_chart(df, x='Dia', y='Horas', color="#4CAF50")

elif menu == "Registrar Estudo":
    st.markdown("## 📝 Registrar Missão")
    with st.container():
        materia = st.selectbox("Escolha a Matéria", ["Matemática", "Português", "Direito"])
        qtd = st.number_input("Quantidade de Questões", 0)
        if st.button("Salvar Registro"):
            st.success(f"Estudo de {materia} salvo!")
