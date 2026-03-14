import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO E ESTILO (UI/UX)
st.set_page_config(page_title="Foco na Missão", layout="wide")

st.markdown("""
<style>
    header {visibility: hidden;}
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {background-color: #0E1117 !important;}
    html, body, [class*="css"] {font-family: 'Inter', sans-serif; color: #FFFFFF !important;}
    .top-bar {background: #1E2329; padding: 15px; border-radius: 8px; border: 1px solid #4CAF50; margin: -50px 0 30px 0; display: flex; justify-content: space-between;}
    .metric-card {background: #1C2127; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; transition: 0.3s;}
    .metric-card:hover {border-color: #4CAF50; transform: translateY(-3px);}
    .label {color: #A0AEC0 !important; font-size: 12px; font-weight: 600; text-transform: uppercase;}
    .value {font-size: 28px; font-weight: 700; margin: 5px 0; color: #FFFFFF !important;}
    .sub {color: #4CAF50 !important; font-size: 12px; font-weight: bold;}
    .stProgress > div > div > div > div { background-color: #4CAF50 !important; }
</style>
""", unsafe_allow_html=True)

# 2. BANCO DE DADOS (CSV Permanente)
DB_FILE = "dados_missao.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["data", "materia", "minutos", "questoes", "acertos"]).to_csv(DB_FILE, index=False)

def carregar_dados(): return pd.read_csv(DB_FILE)
def salvar_dados(m, t, q, a):
    df = carregar_dados()
    novo = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), m, t, q, a]], columns=df.columns)
    pd.concat([df, novo]).to_csv(DB_FILE, index=False)

df_estudos = carregar_dados()

# 3. SIDEBAR
with st.sidebar:
    st.markdown("<h2 style='color:#4CAF50; text-align:center;'>🎯 FOCO</h2>", unsafe_allow_html=True)
    menu = option_menu(None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho"],
        icons=["grid", "pencil", "clock", "graph-up"],
        styles={"nav-link": {"color": "#FFF", "font-size": "15px"}, "nav-link-selected": {"background-color": "#2B3139", "color": "#4CAF50"}})
    st.caption("🟢 Acesso Completo")

st.markdown('<div class="top-bar"><span style="color:#4CAF50; font-weight:bold;">FOCO NA MISSÃO</span></div>', unsafe_allow_html=True)

# 4. LÓGICA DE FILTRAGEM
def filtrar(df, p):
    if df.empty: return df
    df['data'] = pd.to_datetime(df['data'])
    h = datetime.now()
    if p == "Hoje": return df[df['data'].dt.date == h.date()]
    if p == "Semana": return df[df['data'] >= (h - timedelta(days=h.weekday()))]
    if p == "Mês": return df[df['data'].dt.month == h.month]
    if p == "Ano": return df[df['data'].dt.year == h.year]
    return df

# 5. PÁGINAS
if menu == "Dashboard":
    st.markdown("### Olá, Guerreiro! 👋")
    if df_estudos.empty:
        st.info("Nenhum dado encontrado. Comece a registrar seus estudos!")
    else:
        c1, c2, c3 = st.columns(3)
        metrics = [("Horas Totais", f"{df_estudos['minutos'].sum()/60:.1f}h", "Total acumulado"),
                   ("Questões", df_estudos['questoes'].sum(), "Resolvidas"),
                   ("Aproveitamento", f"{(df_estudos['acertos'].sum()/df_estudos['questoes'].sum()*100) if df_estudos['questoes'].sum()>0 else 0:.1f}%", "Média de acertos")]
        for col, (t, v, s) in zip([c1, c2, c3], metrics):
            col.markdown(f'<div class="metric-card"><div class="label">{t}</div><div class="value">{v}</div><div class="sub">{s}</div></div>', unsafe_allow_html=True)
        st.write("---")
        st.bar_chart(df_estudos.groupby('data')['minutos'].sum(), color="#4CAF50")

elif menu == "Registrar Estudo":
    st.markdown("### 📝 Nova Missão")
    with st.form("reg", clear_on_submit=True):
        m = st.selectbox("Matéria", ["Português", "Matemática", "Direito", "Informática"])
        t = st.number_input("Minutos", 1)
        q = st.number_input("Questões", 0)
        a = st.number_input("Acertos", 0)
        if st.form_submit_button("Salvar Registro"):
            salvar_dados(m, t, q, a)
            st.success("Salvo!")
            st.rerun()

elif menu == "Desempenho":
    st.markdown("### 📈 Desempenho")
    per = st.select_slider("", ["Hoje", "Semana", "Mês", "Ano", "Todo"], "Semana")
    df_f = filtrar(df_estudos.copy(), per)
    if not df_f.empty:
        c1, c2, c3, c4 = st.columns(4)
        h_tot = df_f['minutos'].sum()/60
        specs = [("Total Horas", f"{h_tot:.1f}h", f"{df_f['minutos'].sum()}m"), ("Média Diária", f"{h_tot/df_f['data'].nunique():.1f}h", "Ritmo"), ("Matérias", df_f['materia'].nunique(), "Disciplinas"), ("Registros", len(df_f), "Sessões")]
        for col, (t, v, s) in zip([c1, c2, c3, c4], specs):
            col.markdown(f'<div class="metric-card"><div class="label">{t}</div><div class="value">{v}</div><div class="sub">{s}</div></div>', unsafe_allow_html=True)
        st.bar_chart(df_f.groupby('materia')['minutos'].sum()/60, color="#4CAF50")
    else: st.warning("Sem dados para este período.")
