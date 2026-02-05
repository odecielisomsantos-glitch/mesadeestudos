import streamlit as st
import json
import os
import base64

# --- 1. CONFIGURAÇÃO E ESTILO (CSS) ---
st.set_page_config(page_title="Plataforma de Leitura Pro", layout="wide")

st.markdown("""
    <style>
    /* Nome da Pasta: Grande, Negrito e Esquerda */
    .stExpander details summary p {
        font-size: 28px !important;
        font-weight: 800 !important;
        text-align: left !important;
        color: #1E1E1E !important;
        margin-left: 0px !important;
    }
    /* Estilo do Bloco de Texto */
    .caixa-leitura {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        font-size: 22px;
        line-height: 1.8;
        text-align: justify;
        color: #262730;
    }
    /* Botões das Subpastas alinhados à esquerda */
    div.stButton > button {
        text-align: left !important;
        font-weight: bold !important;
        font-size: 18px !important;
        padding-left: 20px !important;
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
    return {}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

def exibir_pdf(base64_pdf, nome_arquivo):
    # Tenta exibir o PDF
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)
    
    # Botão de segurança caso o visualizador acima falhe
    st.info("Caso o PDF não apareça acima, use o botão abaixo:")
    st.download_button("📥 Baixar / Abrir PDF Original", 
                       data=base64.b64decode(base64_pdf), 
                       file_name=f"{nome_arquivo}.pdf", 
                       mime="application/pdf")

if "db" not in st.session_state: st.session_state.db = carregar()
if "leitura_atual" not in st.session_state: st.session_state.leitura_atual = None

# --- 3. MENU LATERAL ---
st.sidebar.title("🎮 Painel")
menu = st.sidebar.radio("Ir para:", ["PDF (Leitura)", "Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO ---
if menu == "Gerenciamento":
    st.title("⚙️ Gerenciamento")
    t1, t2, t3, t4 = st.tabs(["📁 Pastas", "📂 Subpastas", "📝 Adicionar Material", "✏️ Editar/Excluir"])
    
    with t1:
        n_p = st.text_input("Nome da Nova Pasta")
        if st.button("Criar Pasta"):
            if n_p:
                st.session_state.db[n_p] = {}
                salvar(st.session_state.db); st.success(f"✅ Pasta '{n_p}' criada!"); st.rerun()

    with t2:
        p_s = st.selectbox("Na Pasta:", [""] + list(st.session_state.db.keys()), key="sel_p_sub")
        n_s = st.text_input("Nome da Nova Subpasta")
        if st.button("Vincular Subpasta"):
            if p_s and n_s:
                st.session_state.db[p_s][n_s] = {"texto": "", "pdf": "", "contagem": 0}
                salvar(st.session_state.db); st.success("✅ Subpasta vinculada!"); st.rerun()

    with t3:
        p_c = st.selectbox("Pasta:", [""] + list(st.session_state.db.keys()), key="c1")
        if p_c:
            s_c = st.selectbox("Subpasta:", [""] + list(st.session_state.db[p_c].keys()), key="c2")
            if s_c:
                tipo = st.radio("Tipo de Material:", ["Texto Digitado", "Arquivo PDF"])
                if tipo == "Texto Digitado":
                    txt = st.text_area("Cole o conteúdo:", height=250, value=st.session_state.db[p_c][s_c].get("texto", ""))
                    if st.button("Salvar Texto"):
                        st.session_state.db[p_c][s_c]["texto"] = txt
                        st.session_state.db[p_c][s_c]["pdf"] = ""
                        salvar(st.session_state.db); st.success("✅ Texto salvo!"); st.rerun()
                else:
                    upload_pdf = st.file_uploader("Suba seu PDF", type="pdf")
                    if st.button("Salvar PDF"):
                        if upload_pdf:
                            base64_pdf = base64.b64encode(upload_pdf.read()).decode('utf-8')
                            st.session_state.db[p_c][s_c]["pdf"] = base64_pdf
                            st.session_state.db[p_c][s_c]["texto"] = ""
                            salvar(st.session_state.db); st.success("✅ PDF salvo!"); st.rerun()

    with t4:
        st.subheader("Renomear ou Excluir")
        edit_p = st.selectbox("Selecionar Pasta:", [""] + list(st.session_state.db.keys()), key="ed_p")
        if edit_p:
            novo_n_p = st.text_input("Novo nome para Pasta:", value=edit_p)
            c1, c2 = st.columns(2)
            if c1.button("Salvar Nome"):
                st.session_state.db[novo_n_p] = st.session_state.db.pop(edit_p)
                salvar(st.session_state.db); st.rerun()
            if c2.button("🗑️ Excluir Pasta"):
                del st.session_state.db[edit_p]; salvar(st.session_state.db); st.rerun()
            
            st.divider()
            sub_opcoes = list(st.session_state.db[edit_p].keys())
            if sub_opcoes:
                edit_s = st.selectbox("Selecionar Subpasta:", [""] + sub_opcoes, key="ed_s")
                if edit_s:
                    novo_n_s = st.text_input("Novo nome para Subpasta:", value=edit_s)
                    cs1, cs2 = st.columns(2)
                    if cs1.button("Salvar Subpasta"):
                        st.session_state.db[edit_p][novo_n_s] = st.session_state.db[edit_p].pop(edit_s)
                        salvar(st.session_state.db); st.rerun()
                    if cs2.button("🗑️ Excluir Subpasta"):
                        del st.session_state.db[edit_p][edit_s]; salvar(st.session_state.db); st.rerun()

# --- 5. PÁGINA: PDF (LEITURA) ---
else:
    st.title("📖 Área de Estudo")
    for pasta, subpastas in st.session_state.db.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            for sub, dados in subpastas.items():
                col_btn, col_info = st.columns([4, 1])
                qtd = dados.get("contagem", 0)
                with col_btn:
                    if st.button(f"📄 {sub}", key=f"btn_{pasta}_{sub}", use_container_width=True):
                        st.session_state.leitura_atual = (pasta, sub)
                        st.rerun()
                with col_info:
                    st.markdown(f"**Lido: {qtd}x**")

    if st.session_state.leitura_atual:
        p_at, s_at = st.session_state.leitura_atual
        # Verifica se a pasta ainda existe (evita erro se foi excluída no gerenciamento)
        if p_at in st.session_state.db and s_at in st.session_state.db[p_at]:
            dados_at = st.session_state.db[p_at][s_at]
            st.divider()
            st.subheader(f"📍 Estudando: {s_at}")
            
            if dados_at.get("pdf"):
                exibir_pdf(dados_at["pdf"], s_at)
            elif dados_at.get("texto"):
                st.markdown(f'<div class="caixa-leitura">{dados_at["texto"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
            else:
                st.warning("Subpasta aberta, mas sem conteúdo cadastrado. Vá ao Gerenciamento.")

            if st.button("✅ CONCLUÍ MAIS UMA REPETIÇÃO!", use_container_width=True):
                st.session_state.db[p_at][s_at]["contagem"] = dados_at.get("contagem", 0) + 1
                salvar(st.session_state.db); st.balloons(); st.rerun()
