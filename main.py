import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

st.set_page_config(page_title="Foco na Missão", layout="wide")

# CSS Ninja: Ajustando cores para Dark Grey e eliminando fundos brancos
st.markdown("""<style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main {background-color: #0E1117 !important;}
    /* Barra Superior - Agora em Cinza Escuro */
    .top-bar {background-color: #1E1E1E; padding: 12px; border-radius: 8px; border: 1px solid #333; margin-bottom: 20px;}
    .top-title {color: #4CAF50 !important; font-weight: bold; font-size: 20px; margin-left: 10px;}
    /* Cards e Gráficos */
    .card {background: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;}
    h3, p, span, label {color: #FFF !important;}
    /* Remove bordas brancas de componentes do Streamlit */
    div[data-testid="stForm"] {border: 1px solid #333;}
</style>""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.write(" ")
    menu = option_menu(
        None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Ranking", "Conquistas", "Perfil"],
        icons=["grid-1x2", "pencil-square", "stopwatch", "graph-up-arrow", "file-earmark-text", "trophy", "award", "person"],
        styles={
            "container": {"background-color": "#0E1117"},
            "nav-link": {"font-size": "15px", "color": "#FFF"},
            "nav-link-selected": {"background-color": "#1E1E1E", "color": "#4CAF50", "border-left": "4px solid #4CAF50", "border-radius": "0px"}
        }
    )
    st.caption("🟢 Acesso Completo")

# --- CABEÇALHO ESCURO ---
st.markdown('<div class="top-bar"><span class="top-title">🎯 FOCO NA MISSÃO</span></div>', unsafe_allow_html=True)

# --- CONTEÚDO ---
if menu == "Dashboard":
    st.markdown("### Olá, Guerreiro! 👋")
    cols = st.columns(3)
    metrics = [("HORAS NA SEMANA", "7h 5min", "Meta: 30h"), ("QUESTÕES", "162", "75% acerto"), ("GERAL", "80%", "1866 quest.")]
    
    for col, (tit, val, foot) in zip(cols, metrics):
        col.markdown(f'<div class="card"><div style="color:gray;font-size:11px">{tit}</div><div style="font-size:24px;font-weight:bold">{val}</div><div style="color:#4CAF50;font-size:11px">{foot}</div></div>', unsafe_allow_html=True)

    st.write("---")
    st.progress(0.24)
    
    # Gráfico com dados simulados
    df = pd.DataFrame({'D': ['S','T','Q','Q','S','S','D'], 'H': [1, 2.5, 4, 1.5, 0, 0, 0]})
    st.bar_chart(df, x='D', y='H', color="#4CAF50")

elif menu == "Registrar Estudo":
    st.markdown("### 📝 Registrar Missão")
    with st.form("reg"):
        st.selectbox("Matéria", ["Matemática", "Português", "Direito"])
        st.number_input("Questões Feitas", 0)
        if st.form_submit_button("Salvar"): st.success("Registrado!")
