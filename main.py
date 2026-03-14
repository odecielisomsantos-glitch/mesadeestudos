import streamlit as st
import pandas as pd

st.set_page_config(page_title="Foco na Missão", layout="wide")

# CSS Compacto e Profissional
st.markdown("""<style>
    [data-testid="stAppViewContainer"] {background-color: #0E1117;}
    [data-testid="stSidebar"] {background-color: #111 !important; border-right: 1px solid #333;}
    /* Botões da Sidebar */
    .stButton > button {
        width: 100%; border: none; background: transparent; color: #888;
        text-align: left; padding: 10px 0; font-size: 16px; transition: 0.3s;
    }
    .stButton > button:hover {color: #4CAF50; background: #1E1E1E;}
    .card {background: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;}
    h1, h2, h3, p, span {color: #FFF !important;}
</style>""", unsafe_allow_html=True)

# --- SIDEBAR PROFISSIONAL ---
with st.sidebar:
    st.markdown("<h2 style='color: #4CAF50;'>🎯 FOCO NA MISSÃO</h2>", unsafe_allow_html=True)
    st.write(" ") # Espaçamento
    
    # Navegação por botões (Estilo App)
    if "pg" not in st.session_state: st.session_state.pg = "Dashboard"
    
    options = {"🏠 Dashboard": "Dashboard", "📝 Registrar": "Registrar", "⏱️ Cronômetro": "Cronômetro", "📈 Desempenho": "Desempenho", "👤 Perfil": "Perfil"}
    
    for label, name in options.items():
        if st.button(label):
            st.session_state.pg = name
            st.rerun()

# --- CONTEÚDO ---
menu = st.session_state.pg

if menu == "Dashboard":
    st.markdown(f"### Olá, Guerreiro! 👋")
    cols = st.columns(3)
    metrics = [("HORAS NA SEMANA", "7h 5min", "Meta: 30h"), ("QUESTÕES", "162", "75% acerto"), ("GERAL", "80%", "1866 quest.")]
    
    for col, (tit, val, foot) in zip(cols, metrics):
        col.markdown(f'<div class="card"><div style="color:gray;font-size:12px">{tit}</div><div style="font-size:25px;font-weight:bold">{val}</div><div style="color:#4CAF50;font-size:12px">{foot}</div></div>', unsafe_allow_html=True)

    st.write("---")
    st.progress(0.24)
    st.bar_chart(pd.DataFrame({'D': ['S','T','Q','Q','S','S','D'], 'H': [1, 2.5, 4, 1.5, 0, 0, 0]}), x='D', y='H', color="#4CAF50")
