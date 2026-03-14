import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO E ESTILO (UI/UX PREMIUM)
st.set_page_config(page_title="Foco na Missão", layout="wide")

st.markdown("""
<style>
    header {visibility: hidden;}
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {background-color: #0E1117 !important;}
    html, body, [class*="css"] {font-family: 'Inter', sans-serif; color: #FFFFFF !important;}
    
    /* Barra Superior */
    .top-bar {background: #161A1E; padding: 10px 20px; border-bottom: 1px solid #2B3139; margin: -50px -50px 30px -50px; display: flex; justify-content: space-between; align-items: center;}
    
    /* Cards do Dashboard */
    .metric-card {background: #1C2127; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; min-height: 150px;}
    .label {color: #848E9C !important; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
    .value {font-size: 32px; font-weight: 700; margin: 10px 0; color: #FFFFFF !important;}
    .sub-label {color: #848E9C !important; font-size: 11px;}

    /* Barra de Progresso e Alerta */
    .progress-container {background: #1C2127; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; margin-top: 20px;}
    .alert-box {background: rgba(255, 165, 0, 0.1); border: 1px solid orange; color: orange; padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 15px;}
    
    /* Estilo dos Inputs */
    .reg-card {background: #1C2127; padding: 25px; border-radius: 12px; border: 1px solid #2B3139; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# 2. BANCO DE DADOS (Correção do erro de Data)
DB_FILE = "dados_missao.csv"

def inicializar_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["data", "materia", "minutos", "questoes", "acertos"])
        df.to_csv(DB_FILE, index=False)

def carregar_dados():
    inicializar_db()
    try:
        df = pd.read_csv(DB_FILE)
        if not df.empty:
            df['data'] = pd.to_datetime(df['data'], errors='coerce') # Coerce evita o erro de formato
            df = df.dropna(subset=['data']) # Remove linhas com data inválida
        return df
    except Exception:
        return pd.DataFrame(columns=["data", "materia", "minutos", "questoes", "acertos"])

def salvar_dados(m, t, q, a, d):
    df = carregar_dados()
    novo = pd.DataFrame([[d, m, t, q, a]], columns=df.columns)
    pd.concat([df, novo]).to_csv(DB_FILE, index=False)

df_estudos = carregar_dados()

# 3. SIDEBAR
with st.sidebar:
    st.markdown("<h3 style='color:#4CAF50;'>🎯 FOCO NO PAPIRO</h3>", unsafe_allow_html=True)
    menu = option_menu(None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Ranking", "Perfil"],
        icons=["grid", "pencil", "clock", "graph-up", "file-text", "trophy", "person"],
        styles={"nav-link": {"color": "#848E9C", "font-size": "14px"}, "nav-link-selected": {"background-color": "#2B3139", "color": "#4CAF50"}})

# BARRA SUPERIOR
st.markdown(f'''<div class="top-bar">
    <span style="color:#4CAF50; font-weight:bold;">FOCO NO PAPIRO</span>
    <div style="font-size:12px; color:#848E9C;">"Quem não mede, não evolui." | <span style="color:#F0B90B">🏆 Premium</span></div>
</div>''', unsafe_allow_html=True)

# 4. PÁGINAS
if menu == "Dashboard":
    st.markdown("## Olá, Guerreiro! 👋")
    st.caption(datetime.now().strftime("%A, %d de %B"))

    # Métricas Topo
    m1, m2, m3, m4 = st.columns(4)
    if not df_estudos.empty:
        h_semana = df_estudos[df_estudos['data'] >= (datetime.now() - timedelta(days=7))]['minutos'].sum() / 60
        q_semana = df_estudos[df_estudos['data'] >= (datetime.now() - timedelta(days=7))]['questoes'].sum()
        acerto_geral = (df_estudos['acertos'].sum() / df_estudos['questoes'].sum() * 100) if df_estudos['questoes'].sum() > 0 else 0
    else:
        h_semana, q_semana, acerto_geral = 0, 0, 0

    m1.markdown(f'<div class="metric-card"><div class="label">Horas na Semana</div><div class="value">{h_semana:.1f}h</div><div class="sub-label">Meta: 30h</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="label">Questões na Semana</div><div class="value">{int(q_semana)}</div><div class="sub-label">Foco total</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="label">Acerto Geral</div><div class="value">{acerto_geral:.1f}%</div><div class="sub-label">{int(df_estudos["questoes"].sum() if not df_estudos.empty else 0)} questões</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="label">Matérias</div><div class="value">{df_estudos["materia"].nunique() if not df_estudos.empty else 0}</div><div class="sub-label">Disciplinas</div></div>', unsafe_allow_html=True)

    # Progresso Semanal (Igual à imagem)
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    pct = min(h_semana / 30, 1.0)
    st.markdown(f'<div style="display:flex; justify-content:space-between;"><span class="label">Horas de Estudo (Meta semanal)</span><span class="value" style="font-size:18px;">{h_semana:.1f}h / 30h</span></div>', unsafe_allow_html=True)
    st.progress(pct)
    st.markdown(f'<p class="sub-label">{int(pct*100)}% concluído | Faltam {max(30-h_semana, 0):.1f}h</p>', unsafe_allow_html=True)
    if h_semana < 15:
        st.markdown('<div class="alert-box">⚠️ Você está abaixo do ritmo. Intensifique!</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Registrar Estudo":
    st.markdown("## Registrar Estudo")
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        with st.form("reg_form", clear_on_submit=True):
            st.markdown('<div class="label">DATA</div>', unsafe_allow_html=True)
            d = st.date_input("Data", label_visibility="collapsed")
            
            st.markdown('<div class="label">MATÉRIA</div>', unsafe_allow_html=True)
            mat = st.selectbox("Selecione", ["Português", "Matemática", "Direito Constitucional", "Direito Administrativo"], label_visibility="collapsed")
            
            st.markdown('<div class="label">DURAÇÃO E QUESTÕES</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            minutos = col1.number_input("Minutos", min_value=1)
            quest = col2.number_input("Questões", min_value=0)
            acer = col3.number_input("Acertos", min_value=0)
            
            if st.form_submit_button("🚀 SALVAR REGISTRO"):
                salvar_dados(mat, minutos, quest, acer, d)
                st.success("Missão registrada!")
                st.rerun()

    with c_right:
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Registros Recentes</div>', unsafe_allow_html=True)
        if not df_estudos.empty:
            for _, row in df_estudos.tail(5).iloc[::-1].iterrows():
                st.write(f"**{row['materia']}** - {row['minutos']}min")
                st.caption(f"{row['data'].strftime('%d/%m/%Y')}")
                st.divider()
        st.markdown('</div>', unsafe_allow_html=True)

# Adicione aqui as outras abas conforme necessário...
