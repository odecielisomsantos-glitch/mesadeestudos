import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

st.set_page_config(page_title="Foco na Missão", layout="wide")

# CSS Minimalista para Fundo e Cards
st.markdown("""<style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {background-color: #0E1117 !important;}
    .card {background: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;}
    h3, p, span {color: #FFF !important;}
    hr {margin: 10px 0; border-color: #333;}
</style>""", unsafe_allow_html=True)

# --- SIDEBAR PROFISSIONAL ---
with st.sidebar:
    st.markdown("<h2 style='color: #4CAF50; text-align:center;'>🎯 FOCO NA MISSÃO</h2>", unsafe_allow_html=True)
    
    menu = option_menu(
        menu_title=None,
        options=["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Ranking", "Conquistas", "Perfil"],
        icons=["grid-1x2", "pencil-square", "stopwatch", "graph-up-arrow", "file-earmark-text", "trophy", "award", "person"],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#0E1117"},
            "icon": {"color": "#888", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"5px", "color": "#FFF"},
            "nav-link-selected": {"background-color": "transparent", "color": "#4CAF50", "font-weight": "bold", "border-left": "4px solid #4CAF50", "border-radius": "0px"},
        }
    )
    st.markdown("---")
    st.caption("🟢 Você tem acesso completo!")

# --- CONTEÚDO ---
if menu == "Dashboard":
    st.markdown("### Olá, Guerreiro! 👋")
    cols = st.columns(3)
    metrics = [("HORAS NA SEMANA", "7h 5min", "Meta: 30h"), ("QUESTÕES", "162", "75% acerto"), ("GERAL", "80%", "1866 quest.")]
    
    for col, (tit, val, foot) in zip(cols, metrics):
        col.markdown(f'<div class="card"><div style="color:gray;font-size:12px">{tit}</div><div style="font-size:25px;font-weight:bold">{val}</div><div style="color:#4CAF50;font-size:12px">{foot}</div></div>', unsafe_allow_html=True)

    st.write("---")
    st.progress(0.24)
    st.bar_chart(pd.DataFrame({'D': ['S','T','Q','Q','S','S','D'], 'H': [1, 2.5, 4, 1.5, 0, 0, 0]}), x='D', y='H', color="#4CAF50")

else:
    st.info(f"Página **{menu}** em construção.")
