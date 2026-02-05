import streamlit as st
import json
import os
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Plataforma de Estudos Pro", layout="wide")

st.markdown("""
    <style>
    .stExpander details summary p { font-size: 26px !important; font-weight: 800 !important; text-align: left !important; }
    .card-revisao {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        font-size: 14px;
        font-weight: bold;
        color: #0D47A1;
    }
    .dia-calendario {
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 10px;
        min-height: 150px;
        background-color: #F8F9FA;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {"pastas": {}, "calendario": []}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: 
    data = carregar()
    # Garantir estrutura nova
    if "pastas" not in data: data = {"pastas": data, "calendario": []}
    st.session_state.db = data

# --- 3. MENU LATERAL ---
st.sidebar.title("🎮 Menu Principal")
menu = st.sidebar.radio("Ir para:", ["📖 PDF (Leitura)", "🔄 Revisão Ativa", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciamento")
    t1, t2, t3, t4 = st.tabs(["📁 Pastas", "📂 Subpastas", "📝 Material", "✏️ Editar/Excluir"])
    db_p = st.session_state.db["pastas"]
    
    with t1:
        n_p = st.text_input("Nome da Nova Pasta")
        if st.button("Criar Pasta"):
            if n_p:
                db_p[n_p] = {}
                salvar(st.session_state.db); st.success("Criada!"); st.rerun()

    with t2:
        p_s = st.selectbox("Na Pasta:", [""] + list(db_p.keys()))
        n_s = st.text_input("Nome da Subpasta")
        if st.button("Vincular Subpasta"):
            if p_s and n_s:
                db_p[p_s][n_s] = {"texto": "", "pdf": "", "contagem": 0, "ultima_data": ""}
                salvar(st.session_state.db); st.success("Vinculada!"); st.rerun()

    with t3:
        p_c = st.selectbox("Pasta:", [""] + list(db_p.keys()), key="m1")
        if p_c:
            s_c = st.selectbox("Subpasta:", [""] + list(db_p[p_c].keys()), key="m2")
            if s_c:
                txt_i = st.text_area("Texto:", height=150, value=db_p[p_c][s_c].get("texto", ""))
                pdf_i = st.file_uploader("PDF", type="pdf")
                if st.button("💾 Salvar Material"):
                    db_p[p_c][s_c]["texto"] = txt_i
                    if pdf_i: db_p[p_c][s_c]["pdf"] = base64.b64encode(pdf_i.read()).decode('utf-8')
                    salvar(st.session_state.db); st.success("Salvo!"); st.rerun()

    with t4:
        ed_p = st.selectbox("Editar Pasta:", [""] + list(db_p.keys()))
        if ed_p and st.button("🗑️ Deletar Pasta"):
            del db_p[ed_p]; salvar(st.session_state.db); st.rerun()

# --- 5. PÁGINA: REVISÃO ATIVA (QUADRO E GRÁFICOS) ---
elif menu == "🔄 Revisão Ativa":
    st.title("🔄 Quadro Estratégico de Revisão")
    db_p = st.session_state.db["pastas"]
    
    # --- DASHBOARD DE MÉTRICAS ---
    col_g1, col_g2 = st.columns([1, 1])
    
    rev, n_rev, s_mat = 0, 0, 0
    for p, subs in db_p.items():
        for s, d in subs.items():
            if not d.get("texto") and not d.get("pdf"): s_mat += 1
            elif d.get("contagem", 0) > 0: rev += 1
            else: n_rev += 1

    with col_g1:
        st.subheader("📊 Status dos Assuntos")
        fig = px.pie(values=[rev, n_rev, s_mat], 
                     names=['Revisados', 'Não Revisados', 'Sem Material'],
                     color_discrete_sequence=['#4CAF50', '#FFC107', '#F44336'],
                     hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        st.subheader("📌 Planejar Revisão")
        # Criar tarefa de revisão
        todas_sub = []
        for p, subs in db_p.items():
            for s in subs.keys(): todas_sub.append(f"{s} ({p})")
        
        assunto_plan = st.selectbox("Escolha o Assunto:", todas_sub)
        data_plan = st.date_input("Para qual dia?", datetime.now())
        if st.button("📍 Agendar no Quadro"):
            st.session_state.db["calendario"].append({"assunto": assunto_plan, "data": str(data_plan)})
            salvar(st.session_state.db); st.success("Agendado!"); st.rerun()

    st.divider()
    
    # --- QUADRO ESTILO CALENDÁRIO (Próximos 7 Dias) ---
    st.subheader("📅 Planejamento Semanal")
    cols_dias = st.columns(7)
    hoje = datetime.now().date()
    
    for i, col in enumerate(cols_dias):
        dia_foco = hoje + timedelta(days=i)
        with col:
            st.markdown(f"**{dia_foco.strftime('%d/%m')}**")
            st.markdown(f"*{dia_foco.strftime('%a')}*")
            
            with st.container(border=True):
                # Filtrar tarefas do dia
                tarefas = [t for t in st.session_state.db["calendario"] if t["data"] == str(dia_foco)]
                if tarefas:
                    for t in tarefas:
                        st.markdown(f'<div class="card-revisao">{t["assunto"]}</div>', unsafe_allow_html=True)
                else:
                    st.write("---")

    if st.button("🧹 Limpar Quadro Completo"):
        st.session_state.db["calendario"] = []
        salvar(st.session_state.db); st.rerun()

# --- 6. PÁGINA: PDF (LEITURA) ---
else:
    st.title("📖 Área de Leitura")
    db_p = st.session_state.db["pastas"]
    for pasta, subpastas in db_p.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            for sub, dados in subpastas.items():
                with st.expander(f"📄 {sub}"):
                    st.write(f"📊 **Leituras:** {dados.get('contagem', 0)}x")
                    if dados.get("texto"):
                        st.markdown(f'<div style="background:white; padding:20px; border-radius:10px; border:1px solid #ddd; font-size:18px;">{dados["texto"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
                    if dados.get("pdf"):
                        st.download_button(f"📥 Baixar PDF: {sub}", base64.b64decode(dados["pdf"]), f"{sub}.pdf", key=f"dl_{sub}")
                    
                    if st.button("✅ CONCLUÍR", key=f"d_{sub}", use_container_width=True):
                        db_p[pasta][sub]["contagem"] = dados.get("contagem", 0) + 1
                        db_p[pasta][sub]["ultima_data"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        salvar(st.session_state.db); st.balloons(); st.rerun()
