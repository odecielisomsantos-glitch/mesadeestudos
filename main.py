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
    
    /* Barra Superior */
    .top-bar {background: #1E2329; padding: 15px; border-radius: 8px; border: 1px solid #4CAF50; margin: -50px 0 30px 0; display: flex; justify-content: space-between;}
    
    /* Cards Profissionais */
    .metric-card, .reg-card {
        background: #1C2127; padding: 20px; border-radius: 12px; 
        border: 1px solid #2B3139; transition: 0.3s; margin-bottom: 20px;
    }
    .metric-card:hover {border-color: #4CAF50; transform: translateY(-3px);}
    
    /* Textos */
    .label {color: #A0AEC0 !important; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 10px;}
    .value {font-size: 28px; font-weight: 700; margin: 5px 0; color: #FFFFFF !important;}
    .sub {color: #4CAF50 !important; font-size: 12px; font-weight: bold;}
    
    /* Customização de Inputs */
    div[data-baseweb="select"] > div {background-color: #0E1117 !important;}
    .stButton > button {width: 100%; border-radius: 8px;}
    .stProgress > div > div > div > div { background-color: #4CAF50 !important; }
</style>
""", unsafe_allow_html=True)

# 2. BANCO DE DADOS (CSV Permanente)
DB_FILE = "dados_missao.csv"
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["data", "materia", "minutos", "questoes", "acertos"]).to_csv(DB_FILE, index=False)

def carregar_dados(): 
    df = pd.read_csv(DB_FILE)
    df['data'] = pd.to_datetime(df['data'])
    return df

def salvar_dados(m, t, q, a, d=None):
    df = carregar_dados()
    data_final = d if d else datetime.now().strftime("%Y-%m-%d")
    novo = pd.DataFrame([[data_final, m, t, q, a]], columns=df.columns)
    pd.concat([df, novo]).to_csv(DB_FILE, index=False)

df_estudos = carregar_dados()

# 3. SIDEBAR
with st.sidebar:
    st.markdown("<h2 style='color:#4CAF50; text-align:center;'>🎯 FOCO</h2>", unsafe_allow_html=True)
    menu = option_menu(None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho"],
        icons=["grid", "pencil", "clock", "graph-up"],
        styles={
            "container": {"background-color": "#0E1117"},
            "nav-link": {"color": "#FFF", "font-size": "15px"},
            "nav-link-selected": {"background-color": "#2B3139", "color": "#4CAF50", "border-left": "4px solid #4CAF50"}
        })
    st.caption("🟢 Você tem acesso completo!")

st.markdown('<div class="top-bar"><span style="color:#4CAF50; font-weight:bold;">FOCO NA MISSÃO</span></div>', unsafe_allow_html=True)

# 4. LÓGICA DE FILTRAGEM
def filtrar(df, p):
    if df.empty: return df
    h = datetime.now()
    if p == "Hoje": return df[df['data'].dt.date == h.date()]
    if p == "Semana": return df[df['data'] >= (h - timedelta(days=h.weekday()))]
    if p == "Mês": return df[df['data'].dt.month == h.month]
    if p == "Ano": return df[df['data'].dt.year == h.year]
    return df

# 5. PÁGINAS
if menu == "Dashboard":
    st.markdown("### Olá, Guerreiro! 👋")
    st.caption(datetime.now().strftime("%A, %d de %B de %Y"))
    
    if df_estudos.empty:
        st.info("Nenhum dado encontrado. Comece a registrar seus estudos!")
    else:
        c1, c2, c3 = st.columns(3)
        q_tot = df_estudos['questoes'].sum()
        metrics = [
            ("Horas na Semana", f"{df_estudos['minutos'].sum()/60:.1f}h", "Meta: 30h"),
            ("Questões na Semana", q_tot, f"{df_estudos['acertos'].sum()} acertos"),
            ("Acerto Geral", f"{(df_estudos['acertos'].sum()/q_tot*100) if q_tot>0 else 0:.1f}%", f"{q_tot} questões")
        ]
        for col, (t, v, s) in zip([c1, c2, c3], metrics):
            col.markdown(f'<div class="metric-card"><div class="label">{t}</div><div class="value">{v}</div><div class="sub">{s}</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown("### Horas por Dia")
        df_daily = df_estudos.groupby(df_estudos['data'].dt.date)['minutos'].sum() / 60
        st.bar_chart(df_daily, color="#4CAF50")

elif menu == "Registrar Estudo":
    st.markdown("## Registrar Estudo")
    st.caption("Registre cada sessão de estudo para acompanhar sua evolução")

    col_main, col_side = st.columns([2, 1])

    with col_main:
        # DATA
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">DATA</div>', unsafe_allow_html=True)
        c_d1, c_d2 = st.columns([1, 2])
        btn_hoje = c_d1.button("📅 Hoje")
        data_input = c_d2.date_input("Selecionar data", label_visibility="collapsed")
        data_final = datetime.now().date() if btn_hoje else data_input
        st.markdown(f"Data selecionada: **{data_final.strftime('%A, %d de %m de %Y')}**")
        st.markdown('</div>', unsafe_allow_html=True)

        # MATÉRIA
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">MATÉRIA</div>', unsafe_allow_html=True)
        materias = ["Português", "Matemática", "Direito Constitucional", "Direito Administrativo", "Raciocínio Lógico", "Informática", "Direito Penal"]
        m_sel = st.radio("Escolha a matéria", materias, horizontal=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        # DURAÇÃO
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">DURAÇÃO</div>', unsafe_allow_html=True)
        ch, cm, cs = st.columns(3)
        h = ch.number_input("Horas", 0, 24)
        m = cm.number_input("Minutos", 0, 59)
        s = cs.number_input("Segundos", 0, 59)
        total_m = (h * 60) + m + (s / 60)
        
        st.write(" ")
        if st.button("🚀 SALVAR REGISTRO", type="primary"):
            salvar_dados(m_sel, int(total_m), 0, 0, data_final.strftime("%Y-%m-%d"))
            st.success("Estudo registrado com sucesso!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        # REGISTROS RECENTES
        st.markdown('<div class="reg-card" style="min-height:435px;">', unsafe_allow_html=True)
        st.markdown('<div class="label">Registros Recentes</div>', unsafe_allow_html=True)
        if df_estudos.empty:
            st.markdown('<p style="color:#848E9C; font-size:13px;">Nenhum registro ainda.</p>', unsafe_allow_html=True)
        else:
            for _, row in df_estudos.tail(5).iloc[::-1].iterrows():
                st.markdown(f"**{row['materia']}**")
                st.caption(f"{row['data'].strftime('%d/%m')} • {row['minutos']} min")
                st.divider()
        st.markdown('<p style="color:#4CAF50; font-style:italic; font-size:11px;">"Tudo é registrado. Tudo é calculado."</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Desempenho":
    st.markdown("### 📈 Desempenho")
    per = st.select_slider("", ["Hoje", "Semana", "Mês", "Ano", "Todo"], "Semana")
    df_f = filtrar(df_estudos.copy(), per)
    
    if not df_f.empty:
        c1, c2, c3, c4 = st.columns(4)
        h_tot = df_f['minutos'].sum()/60
        specs = [
            ("Total Horas", f"{h_tot:.1f}h", f"{df_f['minutos'].sum()}m"), 
            ("Média Diária", f"{h_tot/df_f['data'].nunique():.1f}h", "Ritmo"), 
            ("Matérias", df_f['materia'].nunique(), "Disciplinas"), 
            ("Registros", len(df_f), "Sessões")
        ]
        for col, (t, v, s) in zip([c1, c2, c3, c4], specs):
            col.markdown(f'<div class="metric-card"><div class="label">{t}</div><div class="value">{v}</div><div class="sub">{s}</div></div>', unsafe_allow_html=True)
        
        st.markdown("#### Horas por Matéria")
        df_mat = df_f.groupby('materia')['minutos'].sum() / 60
        st.bar_chart(df_mat, color="#4CAF50")
    else:
        st.warning("Sem dados para este período.")
