import streamlit as st
import json
import os
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_quill import st_quill  # Importando o novo editor

# --- 1. CONFIGURAÇÃO E ESTILO (CSS) ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide")

st.markdown("""
    <style>
    /* Pastas e Títulos */
    .stExpander details summary p { font-size: 26px !important; font-weight: 800 !important; text-align: left !important; color: #1E1E1E !important; }
    
    /* Estilo do Editor de Texto (Quill) para parecer leitura */
    .stQuill {
        background-color: #FFFFFF;
        border-radius: 15px;
        border: 1px solid #E0E0E0;
        font-size: 20px; /* Fonte ligeiramente menor para o editor */
        line-height: 1.8;
        text-align: justify;
        color: #262730;
    }
    .ql-container.ql-snow { border: none !important; }
    .ql-toolbar.ql-snow {
        border: none !important;
        border-bottom: 1px solid #E0E0E0 !important;
        background-color: #f8f9fa;
        border-radius: 15px 15px 0 0;
    }
    .ql-editor { padding: 35px !important; }

    /* Cards do Calendário */
    .card-revisao-pendente { background-color: #FFF9C4; border-left: 5px solid #FBC02D; padding: 8px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; font-weight: bold; color: #827717; }
    .card-revisao-concluida { background-color: #C8E6C9; border-left: 5px solid #4CAF50; padding: 8px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; font-weight: bold; color: #1B5E20; }
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

# --- 3. MENU LATERAL (PORTUGUÊS) ---
st.sidebar.title("🎮 Menu Principal")
menu = st.sidebar.radio("Ir para:", ["📖 Leitura de Materiais", "📊 Revisão e Quadro", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciamento de Conteúdo")
    t1, t2, t3, t4 = st.tabs(["📁 Criar Pasta", "📂 Criar Subpasta", "📝 Adicionar Material", "✏️ Editar/Excluir"])
    db_p = st.session_state.db["pastas"]
    
    with t1:
        n_p = st.text_input("Nome da Nova Pasta (Ex: PMPE)")
        if st.button("Criar Pasta"):
            if n_p:
                db_p[n_p] = {}
                salvar(st.session_state.db); st.success("✅ Pasta criada!"); st.rerun()

    with t2:
        p_s = st.selectbox("Selecione a Pasta Pai:", [""] + list(db_p.keys()))
        n_s = st.text_input("Nome do Assunto (Subpasta)")
        if st.button("Criar Subpasta"):
            if p_s and n_s:
                db_p[p_s][n_s] = {"texto": "", "pdf": "", "contagem": 0, "ultima_data": ""}
                salvar(st.session_state.db); st.success("✅ Assunto vinculado!"); st.rerun()

    with t3:
        p_c = st.selectbox("Pasta:", [""] + list(db_p.keys()), key="g1")
        s_c = st.selectbox("Subpasta:", [""] + list(db_p[p_c].keys()) if p_c else [], key="g2")
        if s_c:
            st.info("💡 Dica: Cole o texto puro aqui. Você poderá grifá-lo na área de leitura.")
            txt_in = st.text_area("Texto do material:", height=250, value=db_p[p_c][s_c].get("texto", ""))
            pdf_in = st.file_uploader("Subir arquivo PDF", type="pdf")
            if st.button("💾 Salvar Material"):
                db_p[p_c][s_c]["texto"] = txt_in
                if pdf_in: db_p[p_c][s_c]["pdf"] = base64.b64encode(pdf_in.read()).decode('utf-8')
                salvar(st.session_state.db); st.success("✅ Material salvo!"); st.rerun()

    with t4:
        edit_p = st.selectbox("Escolha uma pasta para editar/excluir:", [""] + list(db_p.keys()))
        if edit_p and st.button("🗑️ Deletar Pasta Completa"):
            del db_p[edit_p]; salvar(st.session_state.db); st.rerun()

# --- 5. PÁGINA: REVISÃO E QUADRO ---
elif menu == "📊 Revisão e Quadro":
    st.title("📊 Centro de Inteligência e Revisão")
    db_p = st.session_state.db["pastas"]
    
    # --- GRÁFICO DE CORES ---
    rev, pend, s_mat = 0, 0, 0
    for p, subs in db_p.items():
        for s, d in subs.items():
            if not d.get("texto") and not d.get("pdf"): s_mat += 1
            elif d.get("contagem", 0) > 0: rev += 1
            else: pend += 1
    
    fig = px.pie(values=[rev, pend, s_mat], 
                 names=['Revisadas', 'Pendentes', 'Sem Material'],
                 color=['Revisadas', 'Pendentes', 'Sem Material'],
                 color_discrete_map={'Revisadas':'#28a745', 'Pendentes':'#ffc107', 'Sem Material':'#dc3545'},
                 hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📅 Quadro Semanal de Revisão")
    
    col_ag, col_dt = st.columns(2)
    with col_ag:
        as_opcoes = [f"{s} | {p}" for p, subs in db_p.items() for s in subs.keys()]
        as_sel = st.selectbox("Escolha o Assunto:", [""] + as_opcoes)
    with col_dt:
        dt_sel = st.date_input("Para o dia:", datetime.now())
    
    if st.button("📌 Fixar no Quadro"):
        if as_sel:
            st.session_state.db["calendario"].append({"assunto": as_sel, "data": str(dt_sel), "concluido": False})
            salvar(st.session_state.db); st.rerun()

    cols = st.columns(7)
    for i, col in enumerate(cols):
        dia = datetime.now().date() + timedelta(days=i)
        with col:
            st.markdown(f"**{dia.strftime('%d/%m')}**")
            with st.container(border=True):
                tarefas = [t for t in st.session_state.db["calendario"] if t["data"] == str(dia)]
                for idx, t in enumerate(tarefas):
                    estilo = "card-revisao-concluida" if t.get("concluido") else "card-revisao-pendente"
                    st.markdown(f'<div class="{estilo}">{t["assunto"]}</div>', unsafe_allow_html=True)
                    if not t.get("concluido"):
                        if st.button("✅", key=f"check_{dia}_{idx}"):
                            t["concluido"] = True
                            salvar(st.session_state.db); st.rerun()

# --- 6. PÁGINA: LEITURA (COM GRIFO INTERATIVO) ---
else:
    st.title("📖 Área de Leitura")
    db_p = st.session_state.db["pastas"]
    
    for pasta, subpastas in db_p.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            for sub, dados in subpastas.items():
                with st.expander(f"📄 {sub}"):
                    # --- EDITOR DE TEXTO COM GRIFOS ---
                    texto_atual = dados.get("texto", "")
                    
                    if texto_atual:
                        # Barra de ferramentas minimalista: só cor de fundo e limpar formatação
                        toolbar_config = [
                            [{'background': ['#FFF176', '#A5D6A7', '#F48FB1', 'white']}], # Amarelo, Verde, Rosa
                            ['clean'] # Borracha para limpar
                        ]
                        
                        st.caption("🖍️ **Modo de Estudo:** Selecione o texto e escolha uma cor na barra acima para grifar.")
                        # O componente st_quill substitui a caixa de texto estática
                        novo_conteudo_html = st_quill(
                            value=texto_atual,
                            toolbar=toolbar_config,
                            key=f"quill_{pasta}_{sub}",
                            html=True, # Salva como HTML para manter os grifos
                            readonly=False # Permite edição/grifo
                        )
                        
                        # Botão para salvar os grifos feitos
                        if st.button("💾 Salvar Marcações no Texto", key=f"sv_{sub}"):
                            db_p[pasta][sub]["texto"] = novo_conteudo_html
                            salvar(st.session_state.db)
                            st.success("Grifos salvos com sucesso!")
                            st.rerun()
                    else:
                        st.info("Este assunto ainda não possui texto para leitura.")

                    # --- ÁREA DO PDF ---
                    if dados.get("pdf"):
                        st.divider()
                        st.write("📂 **Documento PDF Anexado:**")
                        st.download_button(f"📥 Baixar PDF Original: {sub}", base64.b64decode(dados["pdf"]), f"{sub}.pdf", key=f"dl_{sub}")
                        st.markdown(f'<iframe src="data:application/pdf;base64,{dados["pdf"]}" width="100%" height="800"></iframe>', unsafe_allow_html=True)

                    st.divider()
                    # Botão de Conclusão
                    if st.button("✅ CONCLUÍR LEITURA", key=f"fin_{sub}", use_container_width=True):
                        db_p[pasta][sub]["contagem"] = dados.get("contagem", 0) + 1
                        salvar(st.session_state.db); st.balloons(); st.rerun()
