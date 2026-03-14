import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

st.set_page_config(page_title="Foco na Missão", layout="wide")

# CSS Minimalista e ajustes de topo
st.markdown("""<style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {background-color: #0E1117 !important;}
    .top-bar {background-color: #FFFFFF; padding: 10px; border-radius: 5px; margin-bottom: 25px; display: flex; align-items: center;}
    .top-title {color: #0E1117 !important; font-weight: bold; font-size: 20px; margin-left: 10px;}
    .card {background: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;}
    h3, p, span {color: #FFF !important;}
</style>""", unsafe_allow_html=True)

# --- SIDEBAR SEM TÍTULO ---
with st.sidebar:
    st.write(" ") # Respiro no topo
    menu = option_menu(
        None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Ranking", "Conquistas", "Perfil"],
        icons=["grid-1x2", "pencil-square", "stopwatch", "graph-up-arrow", "file-earmark-text", "trophy", "award", "person"],
        styles={
            "container": {"background-color": "#0E1117"},
            "nav-link": {"font-size": "15px", "color": "#FFF", "margin":"4px"},
            "nav-link-selected": {"background-color": "transparent", "color": "#4CAF50", "border-left": "4px solid #4CAF50", "border-radius": "0px"}
        }
    )
    st.markdown("---")
    st.caption("🟢 Você tem acesso completo!")

# --- CABEÇALHO NA PÁGINA PRINCIPAL (BARRA BRANCA) ---
st.markdown("""
    <div class="top-bar">
        <span style="font-size: 24px;">🎯</span>
        <span class="top-title">FOCO NA MISSÃO</span>
    </div>
    """, unsafe_allow_html=True)

# --- CONTEÚDO ---
if menu == "Dashboard":
    st.markdown("### Olá, Guerreiro! 👋")
    cols = st.columns(3)
    metrics = [("HORAS NA SEMANA", "7h 5min", "Meta: 30h"), ("QUESTÕES", "162", "75% acerto"), ("GERAL", "80%", "1866 quest.")]
    
    for col, (tit, val, foot) in zip(cols, metrics):
        col.markdown(f'<div class="card"><div style="color:gray;font-size:11px">{tit}</div><div style="font-size:24px;font-weight:bold">{val}</div><div style="color:#4CAF50;font-size:11px">{foot}</div></div>', unsafe_allow_html=True)

    st.write("---")
    st.progress(0.24)
    st.bar_chart(pd.DataFrame({'D': ['S','T','Q','Q','S','S','D'], 'H': [1, 2.5, 4, 1.5, 0, 0, 0]}), x='D', y='H', color="#4CAF50")
