import streamlit as st
import json
import os
import base64

# --- 1. CONFIGURAÇÃO E ESTILO (CSS) ---
st.set_page_config(page_title="Plataforma de Leitura Pro", layout="wide")

st.markdown("""
    <style>
    .stExpander details summary p {
        font-size: 26px !important;
        font-weight: 800 !important;
        text-align: left !important;
        color: #1E1E1E !important;
    }
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
    div.stButton > button {
        text-align: left !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

def exibir_pdf(base64_pdf):
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

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
                salvar(st.session_state.db); st.success("Pasta criada!"); st.rerun()

    with t2:
        p_s = st.selectbox("Na Pasta:", list(st.session_state.db.keys()), key="sel_p_sub")
        n_s = st.text_input("Nome da Nova Subpasta")
        if st.button("Vincular Subpasta"):
            if n_s:
                st.session_state.db[p_s][n_s] = {"texto": "", "pdf": "", "contagem": 0}
                salvar(st.session_state.db); st.success("Subpasta vinculada!"); st.rerun()

    with t3:
        p_c = st.selectbox("Pasta:", list(st.session_state.db.keys()), key="c1")
        s_c = st.selectbox("Subpasta:", list(st.session_state.db.get(p_c, {}).keys()), key="c2")
        
        tipo = st.radio("Tipo de Material:", ["Texto Digitado", "Arquivo PDF"])
        
        if tipo == "Texto Digitado":
            txt = st.text_area("Cole o conteúdo:", height=250, value=st.session_state.db[p_c][s_c].get("texto", ""))
            if st.button("Salvar Texto"):
                st.session_state.db[p_c][s_c]["texto"] = txt
                st.session_state.db[p_c][s_c]["pdf"] = "" # Limpa PDF se salvar texto
                salvar(st.session_state.db); st.success("Texto salvo!"); st.rerun()
        else:
            upload_pdf = st.file_uploader("Suba seu PDF", type="pdf")
            if st.button("Salvar PDF"):
                if upload_pdf:
                    base64_pdf = base64.b64encode(upload_pdf.read()).decode('utf-8')
                    st.session_state.db[p_c][s_c]["pdf"] = base64_pdf
                    st.session_state.db[p_c][s_c]["texto"] = "" # Limpa texto se salvar PDF
                    salvar(st.session_state.db); st.success("PDF salvo com sucesso!"); st.rerun()

    with t4:
        st.subheader("Renomear ou Excluir")
        edit_p = st.selectbox("Selecionar Pasta:", [""] + list(st.session_state.db.keys()))
        if edit_p:
            novo_nome_p = st.text_input("Novo nome para a Pasta:", value=edit_p)
            col_ed1, col_ed2 = st.columns(2)
            if col_ed1.button("Salvar Alteração de Pasta"):
                st.session_state.db[novo_nome_p] = st.session_state.db.pop(edit_p)
                salvar(st.session_state.db); st.success("Pasta renomeada!"); st.rerun()
            if col_ed2.button("🗑️ Excluir Pasta"):
                del st.session_state.db[edit_p]
                salvar(st.session_state.db); st.warning("Pasta excluída!"); st.rerun()
            
            st.divider()
            sub_lista = list(st.session_state.db[edit_p].keys())
            if sub_lista:
                edit_s = st.selectbox("Selecionar Subpasta:", [""] + sub_lista)
                if edit_s:
                    novo_nome_s = st.text_input("Novo nome para a Subpasta:", value=edit_s)
                    col_eds1, col_eds2 = st.columns(2)
                    if col_eds1.button("Salvar Alteração de Subpasta"):
                        st.session_state.db[edit_p][novo_nome_s] = st.session_state.db[edit_p].pop(edit_s)
                        salvar(st.session_state.db); st.success("Subpasta renomeada!"); st.rerun()
                    if col_eds2.button("🗑️ Excluir Subpasta"):
                        del st.session_state.db[edit_p][edit_s]
                        salvar(st.session_state.db); st.warning("Subpasta excluída!"); st.rerun()

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
        dados_at = st.session_state.db[p_at][s_at]
        
        st.divider()
        st.subheader(f"📍 Estudando: {s_at}")
        
        # Lógica de exibição: PDF ou Texto
        if dados_at.get("pdf"):
            exibir_pdf(dados_at["pdf"])
        elif dados_at.get("texto"):
            st.markdown(f'<div class="caixa-leitura">{dados_at["texto"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        else:
            st.warning("Nenhum conteúdo cadastrado.")

        if st.button("✅ CONCLUÍ MAIS UMA REPETIÇÃO!", use_container_width=True):
            st.session_state.db[p_at][s_at]["contagem"] = dados_at.get("contagem", 0) + 1
            salvar(st.session_state.db); st.balloons(); st.rerun()
