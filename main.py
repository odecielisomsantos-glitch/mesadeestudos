import streamlit as st
import json
import os
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO E ESTILIZAÇÃO ---
st.set_page_config(page_title="Mesa de Estudos Pro", layout="wide")

st.markdown("""
    <style>
    .stExpander details summary p { font-size: 26px !important; font-weight: 800 !important; }
    /* Estilo das caixinhas flutuantes no calendário */
    .card-revisao {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        padding: 8px;
        border-radius: 5px;
        margin-bottom: 5px;
        font-size: 13px;
        font-weight: bold;
        color: #0D47A1;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .dia-vazio {
        min-height: 120px;
        border: 1px dashed #d3d3d3;
        border-radius: 10px;
        padding: 5px;
        background-color: #FAFAFA;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                # Garante que a estrutura nova exista
                if "pastas" not in data: data = {"pastas": data, "calendario": []}
                return data
        except: return {"pastas": {}, "calendario": []}
    return {"pastas": {}, "calendario": []}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar()

# --- 3. MENU LATERAL ---
st.sidebar.title("🎮 Menu")
menu = st.sidebar.radio("Ir para:", ["📖 PDF (Leitura)", "📊 Revisão e Quadro", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: REVISÃO E QUADRO ---
if menu == "📊 Revisão e Quadro":
    st.title("🔄 Centro de Inteligência e Revisão")
    db_p = st.session_state.db["pastas"]

    # --- DASHBOARD DE MÉTRICAS ---
    st.subheader("📊 Meu Progresso Real")
    col_g1, col_g2 = st.columns([1, 1])
    
    rev, n_rev, s_mat = 0, 0, 0
    for p, subs in db_p.items():
        for s, d in subs.items():
            if not d.get("texto") and not d.get("pdf"): s_mat += 1
            elif d.get("contagem", 0) > 0: rev += 1
            else: n_rev += 1

    with col_g1:
        dados_pizza = pd.DataFrame({
            "Status": ['Revisados', 'Não Revisados', 'Sem Material'],
            "Qtd": [rev, n_rev, s_mat]
        })
        fig = px.pie(dados_pizza, values='Qtd', names='Status', 
                     color='Status', color_discrete_map={'Revisados':'#4CAF50', 'Não Revisados':'#FFC107', 'Sem Material':'#F44336'},
                     hole=0.5)
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        st.markdown("### 📍 Agendar no Quadro")
        todas_sub = []
        for p, subs in db_p.items():
            for s in subs.keys(): todas_sub.append(f"{s} ({p})")
        
        assunto_plan = st.selectbox("Escolha o Assunto para agendar:", [""] + todas_sub)
        data_plan = st.date_input("Escolha o dia:", datetime.now())
        if st.button("➕ Adicionar ao Quadro"):
            if assunto_plan:
                st.session_state.db["calendario"].append({"assunto": assunto_plan, "data": str(data_plan)})
                salvar(st.session_state.db); st.success("Agendado!"); st.rerun()

    st.divider()
    
    # --- QUADRO ESTILO CALENDÁRIO ---
    st.subheader("📅 Quadro Semanal de Revisões")
    hoje = datetime.now().date()
    cols_dias = st.columns(7)
    
    for i, col in enumerate(cols_dias):
        dia_foco = hoje + timedelta(days=i)
        with col:
            st.markdown(f"**{dia_foco.strftime('%d/%m')}**")
            st.caption(f"{dia_foco.strftime('%A')}")
            
            # Container do dia
            with st.container():
                tarefas = [t for t in st.session_state.db["calendario"] if t["data"] == str(dia_foco)]
                if tarefas:
                    for t in tarefas:
                        st.markdown(f'<div class="card-revisao">{t["assunto"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="dia-vazio"></div>', unsafe_allow_html=True)

    if st.button("🧹 Limpar todo o quadro"):
        st.session_state.db["calendario"] = []
        salvar(st.session_state.db); st.rerun()

# --- 5. PÁGINA: PDF (LEITURA) ---
elif menu == "📖 PDF (Leitura)":
    st.title("📖 Área de Estudo")
    db_p = st.session_state.db["pastas"]
    for pasta, subpastas in db_p.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            for sub, dados in subpastas.items():
                with st.expander(f"📄 {sub}"):
                    if dados.get("texto"):
                        st.markdown(f'<div style="background:white; padding:20px; border-radius:10px; border:1px solid #ddd; font-size:18px; color:black;">{dados["texto"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
                    if dados.get("pdf"):
                        st.download_button(f"📥 Baixar PDF: {sub}", base64.b64decode(dados["pdf"]), f"{sub}.pdf", key=f"dl_{sub}")
                    
                    if st.button("✅ CONCLUIR LEITURA", key=f"d_{sub}", use_container_width=True):
                        db_p[pasta][sub]["contagem"] = dados.get("contagem", 0) + 1
                        salvar(st.session_state.db); st.balloons(); st.rerun()

# --- 6. PÁGINA: GERENCIAMENTO ---
else:
    st.title("⚙️ Gerenciamento")
    # (O código de gerenciamento de pastas e subpastas continua aqui como antes)
    st.info("Use esta área para criar Pastas, Subpastas e adicionar seu Material (Texto/PDF).")
    # ... código de criação ...
    db_p = st.session_state.db["pastas"]
    n_p = st.text_input("Nova Pasta")
    if st.button("Criar"):
        if n_p: db_p[n_p] = {}; salvar(st.session_state.db); st.rerun()
