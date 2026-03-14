import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# Configuração de alta fidelidade
st.set_page_config(page_title="Foco na Missão", layout="wide", initial_sidebar_state="expanded")

# CSS Minimalista Premium
st.markdown("""
<style>
    /* Reset e Fundo */
    header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {background-color: #0B0E11 !important;}
    [data-testid="stSidebar"] {background-color: #0E1117 !important; border-right: 1px solid #1E2329;}
    
    /* Fontes e Textos */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif; color: #EAECEF !important;}

    /* Top Bar Estilizada */
    .top-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 20px; background: #161A1E; border-bottom: 1px solid #2B3139;
        margin: -50px -50px 30px -50px;
    }

    /* Cards Minimalistas Interativos */
    .st-emotion-cache-12w0qpk {gap: 1.5rem;} /* Espaçamento entre colunas */
    .metric-card {
        background: #1E2329; padding: 20px; border-radius: 12px;
        border: 1px solid #2B3139; transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #4CAF50; transform: translateY(-3px);
        box-shadow: 0px 4px 15px rgba(76, 175, 80, 0.1);
    }
    .label {color: #848E9C; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
    .value {font-size: 28px; font-weight: 700; margin: 8px 0; color: #F0B90B !important;} /* Destaque no valor */
    .sub {color: #4CAF50; font-size: 12px; font-weight: 500;}

    /* Progress Bar Custom */
    .stProgress > div > div > div > div { background-color: #4CAF50 !important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#4CAF50; padding-left:15px;'>🎯 FOCO</h2>", unsafe_allow_html=True)
    menu = option_menu(None, 
        ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Ranking", "Conquistas", "Perfil"],
        icons=["grid", "pencil", "clock", "graph-up", "file-text", "trophy", "medal", "person"],
        styles={
            "container": {"background-color": "transparent", "padding": "10px"},
            "nav-link": {"color": "#848E9C", "font-size": "14px", "text-align": "left", "margin":"5px"},
            "nav-link-selected": {"background-color": "#2B3139", "color": "#4CAF50", "border-left": "3px solid #4CAF50"}
        }
    )

# --- CONTEÚDO PRINCIPAL ---
# Simulação da Barra Superior da imagem
st.markdown(f'''
    <div class="top-bar">
        <span style="font-weight:700; color:#4CAF50;">FOCO NA MISSÃO</span>
        <div style="font-size:12px; color:#848E9C;">"Quem não mede, não evolui." | <span style="color:#F0B90B">🏆 Premium</span></div>
    </div>
''', unsafe_allow_html=True)

if menu == "Dashboard":
    st.markdown("### Olá, Guerreiro! 👋")
    st.caption("Sábado, 7 de Fevereiro")
    
    # Layout de métricas em 4 colunas (como na sua segunda foto)
    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        ("Horas na Semana", "7h 5min", "Meta: 30h"),
        ("Questões", "162", "75% de acerto"),
        ("Acerto Geral", "80%", "1866 questões"),
        ("Matérias", "6", "2 críticas")
    ]
    
    for col, (tit, val, sub) in zip([m1, m2, m3, m4], metrics):
        col.markdown(f'''
            <div class="metric-card">
                <div class="label">{tit}</div>
                <div class="value">{val}</div>
                <div class="sub">{sub}</div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("### ") # Espaçamento
    
    # Grid Inferior: Progresso + Sugestões
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.markdown('''<div class="metric-card">
            <div class="label">Progresso Semanal</div>
            <div style="display:flex; justify-content:space-between; margin-top:15px;">
                <span class="sub">24% concluído</span>
                <span style="color:#848E9C; font-size:12px;">Faltam 22h 55min</span>
            </div>
        </div>''', unsafe_allow_html=True)
        st.progress(0.24)
        
        # Gráfico (Simulando o da imagem)
        st.markdown("### Horas por Dia")
        df = pd.DataFrame({'Dia': ['Seg','Ter','Qua','Qui','Sex','Sab','Dom'], 'Horas': [1, 2.5, 4, 1.5, 0, 0, 0]})
        st.bar_chart(df, x='Dia', y='Horas', color="#4CAF50")

    with c_right:
        st.markdown('''<div class="metric-card" style="height: 100%;">
            <div class="label">💡 Sugestões para Hoje</div>
            <div style="margin-top:20px; border-bottom:1px solid #2B3139; padding-bottom:10px;">
                <p style="margin:0; font-weight:600;">Português</p>
                <p style="margin:0; font-size:11px; color:#848E9C;">Não estudado há 15 dias</p>
            </div>
            <div style="margin-top:15px;">
                <p style="margin:0; font-weight:600;">Raciocínio Lógico</p>
                <p style="margin:0; font-size:11px; color:#848E9C;">Mantenha a constância</p>
            </div>
        </div>''', unsafe_allow_html=True)

else:
    st.info(f"Interface **{menu}** carregada com sucesso.")
