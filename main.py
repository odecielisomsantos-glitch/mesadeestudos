import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO E ESTILO (UI/UX PREMIUM)
st.set_page_config(page_title="Foco no Papiro", layout="wide")

st.markdown("""
<style>
    header {visibility: hidden;}
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {background-color: #0E1117 !important;}
    html, body, [class*="css"] {font-family: 'Inter', sans-serif; color: #FFFFFF !important;}
    
    .top-bar {background: #161A1E; padding: 10px 20px; border-bottom: 1px solid #2B3139; margin: -50px -50px 30px -50px; display: flex; justify-content: space-between; align-items: center;}
    
    .metric-card, .reg-card {
        background: #1C2127; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; margin-bottom: 20px;
    }
    
    .label {color: #848E9C !important; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;}
    .value {font-size: 32px; font-weight: 700; margin: 10px 0; color: #FFFFFF !important;}
    .sub-label {color: #848E9C !important; font-size: 11px;}

    /* Alerta de ritmo */
    .alert-box {background: rgba(255, 165, 0, 0.1); border: 1px solid orange; color: orange; padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 15px;}
</style>
""", unsafe_allow_html=True)

# 2. GESTÃO DE DADOS
DB_FILE = "dados_missao.csv"
MAT_FILE = "materias.csv"

def inicializar():
    if not os.path.exists(DB_FILE):
        pd.DataFrame(columns=["data", "materia", "minutos", "questoes", "acertos"]).to_csv(DB_FILE, index=False)
    if not os.path.exists(MAT_FILE):
        pd.DataFrame({"materia": ["Português", "Matemática", "Direito Constitucional", "Direito Administrativo", "Raciocínio Lógico", "Informática"]}).to_csv(MAT_FILE, index=False)

def carregar_dados():
    inicializar()
    df = pd.read_csv(DB_FILE)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    return df.dropna(subset=['data'])

def carregar_materias():
    inicializar()
    return pd.read_csv(MAT_FILE)['materia'].tolist()

df_estudos = carregar_dados()
lista_materias = carregar_materias()

# 3. SIDEBAR
with st.sidebar:
    st.markdown("<h3 style='color:#4CAF50;'>🎯 FOCO NO PAPIRO</h3>", unsafe_allow_html=True)
    menu = option_menu(None, ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Perfil"],
        icons=["grid", "pencil", "clock", "graph-up", "file-text", "person"],
        styles={"nav-link": {"color": "#848E9C", "font-size": "14px"}, "nav-link-selected": {"background-color": "#2B3139", "color": "#4CAF50"}})

st.markdown(f'''<div class="top-bar"><span style="color:#4CAF50; font-weight:bold;">FOCO NO PAPIRO</span><div style="font-size:12px; color:#848E9C;">"Quem não mede, não evolui."</div></div>''', unsafe_allow_html=True)

# 4. PÁGINAS
if menu == "Dashboard":
    st.markdown(f"## Olá, Guerreiro! 👋")
    st.caption(datetime.now().strftime("%A, %d de %B"))
    
    # Cards (Simulando imagem 4b9042)
    m1, m2, m3 = st.columns(3)
    h_sem = df_estudos[df_estudos['data'] >= (datetime.now() - timedelta(days=7))]['minutos'].sum() / 60 if not df_estudos.empty else 0
    m1.markdown(f'<div class="metric-card"><div class="label">Horas na Semana</div><div class="value">{int(h_sem)}h {int((h_sem%1)*60)}min</div><div class="sub-label">Meta: 30h</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="label">Questões na Semana</div><div class="value">{int(df_estudos["questoes"].sum() if not df_estudos.empty else 0)}</div><div class="sub-label">75% de acerto</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="label">Acerto Geral</div><div class="value">80%</div><div class="sub-label">1866 questões</div></div>', unsafe_allow_html=True)

elif menu == "Registrar Estudo":
    st.markdown("## Registrar Estudo")
    st.caption("Registre cada sessão de estudo para acompanhar sua evolução")

    col_main, col_recent = st.columns([2, 1])

    with col_main:
        # DATA
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">DATA</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        btn_hoje = c1.button("📅 Hoje", use_container_width=True)
        data_sel = c2.date_input("Selecionar data", label_visibility="collapsed")
        data_final = datetime.now().date() if btn_hoje else data_sel
        st.markdown(f"Data selecionada: **{data_final.strftime('%A, %d de %B de %Y')}**")
        st.markdown('</div>', unsafe_allow_html=True)

        # MATÉRIA (Baseado na imagem 40abde)
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        c_header = st.columns([4, 1])
        c_header[0].markdown('<div class="label">MATÉRIA</div>', unsafe_allow_html=True)
        if c_header[1].button("✏️ Editar", help="Clique para adicionar ou remover matérias"):
            st.session_state.edit = not st.session_state.get('edit', False)
        
        if st.session_state.get('edit', False):
            with st.expander("Gerenciar Lista", expanded=True):
                nova = st.text_input("Nova matéria:")
                if st.button("➕ Adicionar"):
                    if nova:
                        pd.DataFrame({"materia": lista_materias + [nova]}).to_csv(MAT_FILE, index=False)
                        st.rerun()
                remover = st.selectbox("Remover:", ["Selecione..."] + lista_materias)
                if st.button("🗑️ Excluir"):
                    pd.DataFrame({"materia": [m for m in lista_materias if m != remover]}).to_csv(MAT_FILE, index=False)
                    st.rerun()

        m_escolhida = st.radio("Escolha:", lista_materias, horizontal=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        # DURAÇÃO (Layout idêntico à imagem 40abde)
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">DURAÇÃO</div>', unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        h = t1.number_input("Horas", 0, 24, 0)
        m = t2.number_input("Minutos", 0, 59, 0)
        s = t3.number_input("Segundos", 0, 59, 0)
        st.markdown(f"<p style='text-align:center; color:#848E9C;'>Total: <b>{(h*60)+m}min</b></p>", unsafe_allow_html=True)
        
        if st.button("🚀 SALVAR REGISTRO", type="primary", use_container_width=True):
            novo_d = pd.DataFrame([[data_final, m_escolhida, (h*60)+m, 0, 0]], columns=df_estudos.columns)
            pd.concat([df_estudos, novo_d]).to_csv(DB_FILE, index=False)
            st.success("Estudo registrado!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_recent:
        st.markdown('<div class="reg-card" style="min-height:450px;">', unsafe_allow_html=True)
        st.markdown('<div class="label">Registros Recentes</div>', unsafe_allow_html=True)
        if not df_estudos.empty:
            for _, row in df_estudos.tail(5).iloc[::-1].iterrows():
                st.markdown(f"**{row['materia']}**")
                st.caption(f"{row['data'].strftime('%d/%m')} • {row['minutos']} min")
                st.divider()
        else:
            st.info("Nenhum registro ainda.")
        st.markdown('</div>', unsafe_allow_html=True)
