import streamlit as st
import json
import os
import base64
from datetime import datetime

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Plataforma de Estudos Avançada", layout="wide")

st.markdown("""
    <style>
    .stExpander details summary p {
        font-size: 26px !important;
        font-weight: 800 !important;
        text-align: left !important;
    }
    .caixa-leitura {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        font-size: 22px;
        line-height: 1.8;
        text-align: justify;
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

def exibir_pdf(base64_pdf):
    # Tentativa com iframe (mais compatível)
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

if "db" not in st.session_state: st.session_state.db = carregar()
if "leitura_atual" not in st.session_state: st.session_state.leitura_atual = None

# --- 3. NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação", ["📖 PDF (Leitura)", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Painel de Controle")
    t1, t2, t3, t4 = st.tabs(["📁 Pastas", "📂 Subpastas", "📝 Material", "✏️ Editar/Excluir"])
    
    with t1:
        n_p = st.text_input("Nome da Pasta")
        if st.button("Criar Pasta"):
            if n_p:
                st.session_state.db[n_p] = {}
                salvar(st.session_state.db); st.success("Criada!"); st.rerun()

    with t2:
        p_s = st.selectbox("Na Pasta:", [""] + list(st.session_state.db.keys()))
        n_s = st.text_input("Nome da Subpasta")
        if st.button("Vincular Subpasta"):
            if p_s and n_s:
                st.session_state.db[p_s][n_s] = {"texto": "", "pdf": "", "contagem": 0, "ultima_data": ""}
                salvar(st.session_state.db); st.success("Vinculada!"); st.rerun()

    with t3:
        p_c = st.selectbox("Pasta:", [""] + list(st.session_state.db.keys()), key="m1")
        if p_c:
            s_c = st.selectbox("Subpasta:", [""] + list(st.session_state.db[p_c].keys()), key="m2")
            if s_c:
                tipo = st.radio("Tipo:", ["Texto", "PDF"])
                if tipo == "Texto":
                    txt = st.text_area("Texto:", height=200, value=st.session_state.db[p_c][s_c].get("texto", ""))
                    if st.button("Salvar Texto"):
                        st.session_state.db[p_c][s_c]["texto"] = txt
                        st.session_state.db[p_c][s_c]["pdf"] = ""
                        salvar(st.session_state.db); st.success("Salvo!"); st.rerun()
                else:
                    file = st.file_uploader("Upload PDF", type="pdf")
                    if st.button("Salvar PDF"):
                        if file:
                            b64 = base64.b64encode(file.read()).decode('utf-8')
                            st.session_state.db[p_c][s_c]["pdf"] = b64
                            st.session_state.db[p_c][s_c]["texto"] = ""
                            salvar(st.session_state.db); st.success("PDF Salvo!"); st.rerun()

    with t4:
        st.subheader("Editar Nomes")
        ed_p = st.selectbox("Pasta para editar:", [""] + list(st.session_state.db.keys()))
        if ed_p:
            novo_p = st.text_input("Novo nome Pasta:", value=ed_p)
            if st.button("Renomear Pasta"):
                st.session_state.db[novo_p] = st.session_state.db.pop(ed_p)
                salvar(st.session_state.db); st.rerun()
            if st.button("🗑️ Deletar Pasta"):
                del st.session_state.db[ed_p]; salvar(st.session_state.db); st.rerun()

# --- 5. PÁGINA: PDF (LEITURA) ---
else:
    st.title("📖 Minha Mesa de Estudos")

    # --- NOVO: SISTEMA DE REVISÃO SUGERIDA ---
    with st.expander("🔔 REVISÕES SUGERIDAS (Assuntos esquecidos)", expanded=False):
        revisoes = []
        for p, sub_dict in st.session_state.db.items():
            for s, d in sub_dict.items():
                if d.get("ultima_data"):
                    dias = (datetime.now() - datetime.strptime(d["ultima_data"], "%Y-%m-%d %H:%M:%S")).days
                    if dias >= 1: revisoes.append(f"🚩 **{s}** ({p}) - Sem ler há {dias} dias")
                else:
                    revisoes.append(f"⚪ **{s}** ({p}) - Nunca lido")
        
        if revisoes:
            for r in revisoes[:5]: st.write(r) # Mostra as 5 mais urgentes
        else: st.write("✅ Tudo em dia!")

    st.divider()

    # Listagem de Pastas
    for pasta, subpastas in st.session_state.db.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            for sub, dados in subpastas.items():
                c1, c2 = st.columns([4, 1])
                with c1:
                    if st.button(f"📄 {sub}", key=f"l_{pasta}_{sub}", use_container_width=True):
                        st.session_state.leitura_atual = (pasta, sub)
                        st.rerun()
                with c2:
                    st.write(f"📊 {dados.get('contagem', 0)}x")

    # Exibição do Material
    if st.session_state.leitura_atual:
        p, s = st.session_state.leitura_atual
        if p in st.session_state.db and s in st.session_state.db[p]:
            info = st.session_state.db[p][s]
            st.divider()
            st.subheader(f"📍 Lendo: {s}")
            
            # Exibir PDF ou Texto
            if info.get("pdf"):
                exibir_pdf(info["pdf"])
                st.info("💡 Se o PDF não carregar, use o botão abaixo:")
                st.download_button("📥 Baixar PDF para leitura externa", base64.b64decode(info["pdf"]), f"{s}.pdf")
            elif info.get("texto"):
                st.markdown(f'<div class="caixa-leitura">{info["texto"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
            
            if st.button("✅ CONCLUÍ MAIS UMA LEITURA", use_container_width=True):
                st.session_state.db[p][s]["contagem"] = info.get("contagem", 0) + 1
                st.session_state.db[p][s]["ultima_data"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                salvar(st.session_state.db); st.balloons(); st.rerun()
