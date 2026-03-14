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
    
    /* Cards */
    .metric-card, .reg-card {
        background: #1C2127; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; margin-bottom: 20px;
    }
    
    /* Labels e Textos */
    .label {color: #848E9C !important; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 15px;}
    .value {font-size: 32px; font-weight: 700; margin: 10px 0; color: #FFFFFF !important;}
    .sub-label {color: #848E9C !important; font-size: 11px;}

    /* Barra de Progresso */
    .progress-container {background: #1C2127; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; margin-top: 20px;}
    .alert-box {background: rgba(255, 165, 0, 0.1); border: 1px solid orange; color: orange; padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 15px;}
</style>
""", unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (DATABASE)
DB_FILE = "dados_missao.csv"
MAT_FILE = "materias.csv"

def inicializar_arquivos():
    if not os.path.exists(DB_FILE):
        pd.DataFrame(columns=["data", "materia", "minutos", "questoes", "acertos"]).to_csv(DB_FILE, index=False)
    if not os.path.exists(MAT_FILE):
        pd.DataFrame({"materia": ["Português", "Matemática", "Direito"]}).to_csv(MAT_FILE, index=False)

def carregar_dados():
    inicializar_arquivos()
    try:
        df = pd.read_csv(DB_FILE)
        if not df.empty:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
            df = df.dropna(subset=['data'])
        return df
    except: return pd.DataFrame(columns=["data", "materia", "minutos", "questoes", "acertos"])

def carregar_materias():
    inicializar_arquivos()
    return pd.read_csv(MAT_FILE)['materia'].tolist()

def salvar_estudo(m, t, q, a, d):
    df = carregar_dados()
    novo = pd.DataFrame([[d, m, t, q, a]], columns=df.columns)
    pd.concat([df, novo]).to_csv(DB_FILE, index=False)

# 3. SIDEBAR
with st.sidebar:
    st.markdown("<h3 style='color:#4CAF50;'>🎯 FOCO NO PAPIRO</h3>", unsafe_allow_html=True)
    menu = option_menu(None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Perfil"],
        icons=["grid", "pencil", "clock", "graph-up", "person"],
        styles={"nav-link": {"color": "#848E9C", "font-size": "14px"}, "nav-link-selected": {"background-color": "#2B3139", "color": "#4CAF50"}})

df_estudos = carregar_dados()
lista_materias = carregar_materias()

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
    h_semana = df_estudos[df_estudos['data'] >= (datetime.now() - timedelta(days=7))]['minutos'].sum() / 60 if not df_estudos.empty else 0
    
    m1.markdown(f'<div class="metric-card"><div class="label">Horas na Semana</div><div class="value">{h_semana:.1f}h</div><div class="sub-label">Meta: 30h</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="label">Questões</div><div class="value">{int(df_estudos["questoes"].sum()) if not df_estudos.empty else 0}</div><div class="sub-label">Total acumulado</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="label">Acerto Geral</div><div class="value">{(df_estudos["acertos"].sum()/df_estudos["questoes"].sum()*100) if not df_estudos.empty and df_estudos["questoes"].sum() > 0 else 0:.1f}%</div><div class="sub-label">Eficiência</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="label">Matérias</div><div class="value">{len(lista_materias)}</div><div class="sub-label">Ativas</div></div>', unsafe_allow_html=True)

elif menu == "Registrar Estudo":
    st.markdown("## Registrar Estudo")
    
    col_main, col_side = st.columns([2, 1])

    with col_main:
        # DATA
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">DATA</div>', unsafe_allow_html=True)
        c_d1, c_d2 = st.columns([1, 2])
        btn_hoje = c_d1.button("📅 Hoje", use_container_width=True)
        data_sel = c_d2.date_input("Outra data", label_visibility="collapsed")
        data_final = datetime.now().date() if btn_hoje else data_sel
        st.markdown(f"Data selecionada: **{data_final.strftime('%A, %d de %B de %Y')}**")
        st.markdown('</div>', unsafe_allow_html=True)

        # MATÉRIA (Gestão Dinâmica)
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        header_mat = st.columns([4, 1])
        header_mat[0].markdown('<div class="label">MATÉRIA</div>', unsafe_allow_html=True)
        
        # Botão Editar Matérias
        if header_mat[1].button("✏️ Editar", size="small"):
            st.session_state.edit_mode = not st.session_state.get('edit_mode', False)
        
        if st.session_state.get('edit_mode', False):
            nova_mat = st.text_input("Nome da nova matéria:")
            if st.button("➕ Adicionar"):
                if nova_mat and nova_mat not in lista_materias:
                    pd.DataFrame({"materia": lista_materias + [nova_mat]}).to_csv(MAT_FILE, index=False)
                    st.rerun()
            
            mat_excluir = st.selectbox("Remover matéria:", ["Selecione..."] + lista_materias)
            if st.button("🗑️ Remover"):
                if mat_excluir != "Selecione...":
                    nova_lista = [m for m in lista_materias if m != mat_excluir]
                    pd.DataFrame({"materia": nova_lista}).to_csv(MAT_FILE, index=False)
                    st.rerun()
        
        m_escolhida = st.radio("Selecione a matéria:", lista_materias, horizontal=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        # DURAÇÃO
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">DURAÇÃO E DESEMPENHO</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        h = c1.number_input("Horas", 0, 24)
        m = c2.number_input("Min", 0, 59)
        q = c3.number_input("Questões", 0)
        a = c4.number_input("Acertos", 0)
        
        if st.button("🚀 SALVAR REGISTRO", type="primary", use_container_width=True):
            salvar_estudo(m_escolhida, (h*60)+m, q, a, data_final)
            st.success("Missão cumprida!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown('<div class="reg-card" style="min-height: 500px;">', unsafe_allow_html=True)
        st.markdown('<div class="label">Registros Recentes</div>', unsafe_allow_html=True)
        if not df_estudos.empty:
            for _, row in df_estudos.tail(6).iloc[::-1].iterrows():
                st.markdown(f"**{row['materia']}**")
                st.caption(f"{row['data'].strftime('%d/%m')} • {row['minutos']} min • {row['questoes']}q")
                st.divider()
        else:
            st.info("Nenhum registro encontrado.")
        st.markdown('</div>', unsafe_allow_html=True)
