import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
from datetime import datetime

# 1. Configurações Iniciais e CSS de Alto Contraste
st.set_page_config(page_title="Foco na Missão", layout="wide")

st.markdown("""
<style>
    header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {background-color: #0E1117 !important;}
    [data-testid="stSidebar"] {background-color: #161A1E !important; border-right: 1px solid #333;}
    
    /* Fontes e Visibilidade */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #FFFFFF !important; }
    .top-bar { background: #1E2329; padding: 15px; border-radius: 8px; border: 1px solid #4CAF50; margin: -50px 0 30px 0; display: flex; justify-content: space-between; }
    
    /* Cards Profissionais */
    .metric-card {
        background: #1C2127; padding: 20px; border-radius: 12px;
        border: 1px solid #2B3139; transition: 0.3s;
    }
    .metric-card:hover { border-color: #4CAF50; transform: translateY(-3px); }
    .label { color: #A0AEC0 !important; font-size: 13px; font-weight: 600; text-transform: uppercase; }
    .value { font-size: 32px; font-weight: 700; margin: 10px 0; color: #FFFFFF !important; }
    .sub { color: #4CAF50 !important; font-size: 13px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (Persistência Permanente) ---
DB_FILE = "dados_missao.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["data", "materia", "minutos", "questoes", "acertos"])

def salvar_estudo(materia, min, quest, acert):
    df = carregar_dados()
    novo = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), materia, min, quest, acert]], columns=df.columns)
    pd.concat([df, novo]).to_csv(DB_FILE, index=False)

df_estudos = carregar_dados()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#4CAF50; text-align:center;'>🎯 FOCO</h2>", unsafe_allow_html=True)
    menu = option_menu(None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho"],
        icons=["grid", "pencil", "clock", "graph-up"],
        styles={"nav-link": {"color": "#FFF", "font-size": "15px"}, "nav-link-selected": {"background-color": "#2B3139", "color": "#4CAF50"}})

# --- BARRA SUPERIOR ---
st.markdown(f'<div class="top-bar"><span style="color:#4CAF50; font-weight:bold;">FOCO NA MISSÃO</span><span style="font-size:12px; color:#A0AEC0;">"O que não é medido, não é gerenciado."</span></div>', unsafe_allow_html=True)

# --- LÓGICA DAS PÁGINAS ---
if menu == "Dashboard":
    st.markdown("### Bem-vindo, Guerreiro! 👋")
    
    # Cálculo em tempo real dos dados inseridos
    if not df_estudos.empty:
        total_horas = df_estudos['minutos'].sum() / 60
        total_quest = df_estudos['questoes'].sum()
        pct_acerto = (df_estudos['acertos'].sum() / total_quest * 100) if total_quest > 0 else 0
        total_materias = df_estudos['materia'].nunique()
    else:
        total_horas, total_quest, pct_acerto, total_materias = 0, 0, 0, 0

    # Cards (Dinâmicos)
    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        ("Horas Totais", f"{total_horas:.1f}h", f"Min: {df_estudos['minutos'].sum() if not df_estudos.empty else 0}"),
        ("Questões", f"{total_quest}", f"Acerto: {pct_acerto:.1f}%"),
        ("Aproveitamento", f"{pct_acerto:.1f}%", f"{df_estudos['acertos'].sum() if not df_estudos.empty else 0} acertos"),
        ("Matérias", f"{total_materias}", "Exploradas")
    ]
    
    for col, (tit, val, sub) in zip([m1, m2, m3, m4], metrics):
        col.markdown(f'<div class="metric-card"><div class="label">{tit}</div><div class="value">{val}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)

    st.write("---")
    if df_estudos.empty:
        st.info("💡 Nenhum dado registrado. Vá em 'Registrar Estudo' para começar a sua missão!")
    else:
        st.bar_chart(df_estudos, x='data', y='minutos', color="#4CAF50")

elif menu == "Registrar Estudo":
    st.markdown("### 📝 Registrar Missão")
    with st.form("form_estudo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        materia = col1.selectbox("Matéria", ["Português", "Matemática", "Direito", "Raciocínio Lógico"])
        tempo = col2.number_input("Minutos Estudados", min_value=1)
        q_feitas = col1.number_input("Questões Resolvidas", min_value=0)
        q_acertos = col2.number_input("Acertos", min_value=0)
        
        if st.form_submit_button("Salvar na Base"):
            if q_acertos > q_feitas:
                st.error("Acertos não podem ser maiores que as questões!")
            else:
                salvar_estudo(materia, tempo, q_feitas, q_acertos)
                st.success("Missão Cumprida! Dados salvos com sucesso.")
                st.rerun()
