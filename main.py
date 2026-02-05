import streamlit as st
import json
import os
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide")

st.markdown("""
    <style>
    /* Cabeçalhos das Pastas: Esquerda, Negrito e Grande */
    .stExpander details summary p {
        font-size: 28px !important;
        font-weight: 800 !important;
        text-align: left !important;
        color: #1E1E1E !important;
    }
    .caixa-leitura {
        background-color: #FFFFFF;
        padding: 35px;
        border-radius: 15px;
        border: 1px solid #E0E0E0;
        font-size: 22px;
        line-height: 1.8;
        text-align: justify;
        color: #262730;
    }
    /* Estilo dos marcadores de texto */
    mark.amarelo { background-color: #FFF176; color: black; padding: 2px 4px; border-radius: 3px; }
    mark.verde { background-color: #A5D6A7; color: black; padding: 2px 4px; border-radius: 3px; }
    mark.rosa { background-color: #F48FB1; color: black; padding: 2px 4px; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if "pastas" not in data: data = {"pastas": data, "calendario": []}
                return data
        except: return {"pastas": {}, "calendario": []}
    return {"pastas": {}, "calendario": []}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar()

# --- 3. MENU LATERAL ---
st.sidebar.title("🎮 Menu Principal")
menu = st.sidebar.radio("Ir para:", ["📖 PDF (Leitura)", "🔄 Revisão e Quadro", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO (O RETORNO DAS ABAS) ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciamento de Conteúdo")
    t1, t2, t3, t4 = st.tabs(["📁 Criar Pasta", "📂 Criar Subpasta", "📝 Adicionar Material", "✏️ Editar/Excluir"])
    db_p = st.session_state.db["pastas"]
    
    with t1:
        n_p = st.text_input("Nome da Nova Pasta (Concurso/Matéria)")
        if st.button("Criar Pasta"):
            if n_p:
                db_p[n_p] = {}
                salvar(st.session_state.db); st.success(f"✅ Pasta '{n_p}' criada!"); st.rerun()

    with t2:
        p_s = st.selectbox("Selecione a Pasta Pai:", [""] + list(db_p.keys()))
        n_s = st.text_input("Nome do Assunto (Subpasta)")
        if st.button("Vincular Subpasta"):
            if p_s and n_s:
                db_p[p_s][n_s] = {"texto": "", "pdf": "", "contagem": 0, "ultima_data": ""}
                salvar(st.session_state.db); st.success("✅ Subpasta criada!"); st.rerun()

    with t3:
        col_p, col_s = st.columns(2)
        with col_p: p_c = st.selectbox("Pasta:", [""] + list(db_p.keys()), key="g1")
        with col_s: 
            s_c = st.selectbox("Subpasta:", [""] + list(db_p[p_c].keys()) if p_c else [], key="g2")
        
        if s_c:
            st.divider()
            txt_in = st.text_area("Texto do material (Dica: Use <mark class='amarelo'>texto</mark> para grifar)", 
                                 height=250, value=db_p[p_c][s_c].get("texto", ""))
            pdf_in = st.file_uploader("Subir arquivo PDF", type="pdf")
            if st.button("💾 Salvar Material Completo"):
                db_p[p_c][s_c]["texto"] = txt_in
                if pdf_in:
                    db_p[p_c][s_c]["pdf"] = base64.b64encode(pdf_in.read()).decode('utf-8')
                salvar(st.session_state.db); st.success("✅ Tudo salvo!"); st.rerun()

    with t4:
        st.subheader("Modificar ou Excluir")
        edit_p = st.selectbox("Escolha para editar:", [""] + list(db_p.keys()))
        if edit_p:
            novo_n = st.text_input("Renomear pasta:", value=edit_p)
            c1, c2 = st.columns(2)
            if c1.button("Salvar Novo Nome"):
                db_p[novo_n] = db_p.pop(edit_p)
                salvar(st.session_state.db); st.rerun()
            if c2.button("🗑️ Deletar Pasta Completa"):
                del db_p[edit_p]; salvar(st.session_state.db); st.rerun()

# --- 5. PÁGINA: REVISÃO E QUADRO ---
elif menu == "🔄 Revisão e Quadro":
    st.title("📊 Centro de Inteligência")
    db_p = st.session_state.db["pastas"]
    
    # Gráfico de Progresso
    rev, n_rev, s_mat = 0, 0, 0
    for p, subs in db_p.items():
        for s, d in subs.items():
            if not d.get("texto") and not d.get("pdf"): s_mat += 1
            elif d.get("contagem", 0) > 0: rev += 1
            else: n_rev += 1
    
    fig = px.pie(values=[rev, n_rev, s_mat], names=['Revisados', 'Pendente', 'Sem Material'],
                 color_discrete_sequence=['#4CAF50', '#FFC107', '#F44336'], hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("📅 Quadro de Revisão")
    # Seletor para agendar
    col_a, col_d = st.columns(2)
    with col_a:
        lista_assuntos = [f"{s} ({p})" for p, subs in db_p.items() for s in subs.keys()]
        as_sel = st.selectbox("Agendar Assunto:", [""] + lista_assuntos)
    with col_d:
        dt_sel = st.date_input("Para o dia:", datetime.now())
    
    if st.button("📌 Fixar no Quadro"):
        st.session_state.db["calendario"].append({"assunto": as_sel, "data": str(dt_sel)})
        salvar(st.session_state.db); st.rerun()
        
    cols = st.columns(7)
    for i, col in enumerate(cols):
        dia = datetime.now().date() + timedelta(days=i)
        with col:
            st.markdown(f"**{dia.strftime('%d/%m')}**")
            with st.container(border=True):
                tarefas = [t for t in st.session_state.db["calendario"] if t["data"] == str(dia)]
                for t in tarefas:
                    st.markdown(f'<div style="background:#E3F2FD; padding:5px; border-radius:5px; font-size:12px; margin-bottom:5px; border-left:3px solid #2196F3;">{t["assunto"]}</div>', unsafe_allow_html=True)

# --- 6. PÁGINA: PDF (LEITURA) ---
else:
    st.title("📖 Área de Leitura")
    db_p = st.session_state.db["pastas"]
    
    for pasta, subpastas in db_p.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            for sub, dados in subpastas.items():
                with st.expander(f"📄 {sub}"):
                    # CANETINHA/GRIFO (Manual de Ajuda)
                    with st.popover("🖍️ Ferramenta de Grifo"):
                        st.write("Copie e envolva seu texto com as tags abaixo no Gerenciamento para grifar:")
                        st.code("<mark class='amarelo'>Seu texto aqui</mark>")
                        st.code("<mark class='verde'>Seu texto aqui</mark>")
                        st.code("<mark class='rosa'>Seu texto aqui</mark>")
                    
                    # Conteúdo Texto
                    if dados.get("texto"):
                        st.markdown(f'<div class="caixa-leitura">{dados["texto"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
                    
                    # Conteúdo PDF
                    if dados.get("pdf"):
                        st.divider()
                        st.download_button(f"📥 Baixar PDF Original: {sub}", base64.b64decode(dados["pdf"]), f"{sub}.pdf", key=f"dl_{sub}")
                        st.markdown(f'<iframe src="data:application/pdf;base64,{dados["pdf"]}" width="100%" height="800"></iframe>', unsafe_allow_html=True)

                    if st.button("✅ CONCLUÍR LEITURA", key=f"btn_{sub}", use_container_width=True):
                        db_p[pasta][sub]["contagem"] = dados.get("contagem", 0) + 1
                        salvar(st.session_state.db); st.balloons(); st.rerun()
