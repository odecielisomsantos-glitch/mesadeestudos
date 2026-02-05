import streamlit as st
import json
import os
import base64
from datetime import datetime

# --- 1. CONFIGURAÇÃO E ESTILO (CSS) ---
st.set_page_config(page_title="Plataforma de Leitura Pro", layout="wide")

st.markdown("""
    <style>
    /* Pasta Principal: Grande e Negrito */
    .stExpander details summary p {
        font-size: 26px !important;
        font-weight: 800 !important;
        text-align: left !important;
        color: #1E1E1E !important;
    }
    /* Subtópico: Um pouco menor, mas ainda em destaque */
    .stExpander .stExpander details summary p {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #4F4F4F !important;
    }
    .caixa-leitura {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        font-size: 20px;
        line-height: 1.6;
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
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

if "db" not in st.session_state: st.session_state.db = carregar()

# --- 3. MENU LATERAL ---
st.sidebar.title("🎮 Menu Principal")
menu = st.sidebar.radio("Ir para:", ["📖 PDF (Leitura)", "🔄 Revisão Ativa", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciamento de Conteúdo")
    t1, t2, t3, t4 = st.tabs(["📁 Pastas", "📂 Subpastas", "📝 Material", "✏️ Editar/Excluir"])
    
    with t1:
        n_p = st.text_input("Nome da Nova Pasta")
        if st.button("Criar Pasta"):
            if n_p:
                st.session_state.db[n_p] = {}
                salvar(st.session_state.db); st.success(f"Pasta '{n_p}' criada!"); st.rerun()

    with t2:
        p_s = st.selectbox("Na Pasta:", [""] + list(st.session_state.db.keys()))
        n_s = st.text_input("Nome da Nova Subpasta (Assunto)")
        if st.button("Vincular Subpasta"):
            if p_s and n_s:
                st.session_state.db[p_s][n_s] = {"texto": "", "pdf": "", "contagem": 0, "ultima_data": ""}
                salvar(st.session_state.db); st.success("Subpasta vinculada!"); st.rerun()

    with t3:
        p_c = st.selectbox("Pasta:", [""] + list(st.session_state.db.keys()), key="m1")
        if p_c:
            s_c = st.selectbox("Subpasta:", [""] + list(st.session_state.db[p_c].keys()), key="m2")
            if s_c:
                st.write("---")
                txt_input = st.text_area("Texto do material:", height=150, value=st.session_state.db[p_c][s_c].get("texto", ""))
                pdf_input = st.file_uploader("Subir arquivo PDF (Opcional)", type="pdf")
                
                if st.button("💾 Salvar Material Completo"):
                    st.session_state.db[p_c][s_c]["texto"] = txt_input
                    if pdf_input:
                        b64 = base64.b64encode(pdf_input.read()).decode('utf-8')
                        st.session_state.db[p_c][s_c]["pdf"] = b64
                    salvar(st.session_state.db); st.success("Material salvo!"); st.rerun()

    with t4:
        st.subheader("Modificar Estrutura")
        ed_p = st.selectbox("Selecionar Pasta:", [""] + list(st.session_state.db.keys()))
        if ed_p:
            novo_n_p = st.text_input("Novo nome Pasta:", value=ed_p)
            col1, col2 = st.columns(2)
            if col1.button("Renomear"):
                st.session_state.db[novo_n_p] = st.session_state.db.pop(ed_p)
                salvar(st.session_state.db); st.rerun()
            if col2.button("🗑️ Deletar"):
                del st.session_state.db[ed_p]; salvar(st.session_state.db); st.rerun()

# --- 5. PÁGINA: REVISÃO ATIVA ---
elif menu == "🔄 Revisão Ativa":
    st.title("🔄 Controle de Revisões")
    st.write("Aqui estão os assuntos organizados pela urgência de leitura.")
    
    revisoes = []
    for p, sub_dict in st.session_state.db.items():
        for s, d in sub_dict.items():
            u_data = d.get("ultima_data", "")
            if u_data:
                dias = (datetime.now() - datetime.strptime(u_data, "%Y-%m-%d %H:%M:%S")).days
                revisoes.append({"assunto": s, "pasta": p, "dias": dias, "status": f"🚩 Há {dias} dias"})
            else:
                revisoes.append({"assunto": s, "pasta": p, "dias": 999, "status": "⚪ Nunca lido"})
    
    # Ordenar pelos mais antigos (mais dias)
    revisoes = sorted(revisoes, key=lambda x: x['dias'], reverse=True)
    
    if revisoes:
        for r in revisoes:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{r['assunto']}** ({r['pasta']})")
                c2.info(r['status'])
    else:
        st.info("Nenhum assunto cadastrado para revisão.")

# --- 6. PÁGINA: PDF (LEITURA) ---
else:
    st.title("📖 Área de Leitura")
    
    for pasta, subpastas in st.session_state.db.items():
        # PASTA PRINCIPAL
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            if not subpastas:
                st.write("Nenhum assunto nesta pasta.")
            
            for sub, dados in subpastas.items():
                # SUBTÓPICO (Abertura com a mesma interação)
                with st.expander(f"📄 {sub}"):
                    # Informações de leitura no topo do conteúdo
                    st.write(f"📊 **Leituras realizadas:** {dados.get('contagem', 0)}x")
                    
                    # 1. Parte do Texto
                    if dados.get("texto"):
                        st.markdown(f'<div class="caixa-leitura">{dados["texto"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
                    
                    # 2. Parte do PDF
                    if dados.get("pdf"):
                        st.divider()
                        st.write("📂 **Documento PDF Anexado:**")
                        # Botão de download (garantia de acesso)
                        st.download_button(f"📥 Baixar PDF: {sub}", base64.b64decode(dados["pdf"]), f"{sub}.pdf", key=f"dl_{pasta}_{sub}")
                        # Tentativa de visualização
                        exibir_pdf(dados["pdf"])
                    
                    if not dados.get("texto") and not dados.get("pdf"):
                        st.warning("Assunto sem conteúdo. Adicione no Gerenciamento.")

                    # Botão de Conclusão dentro do expander
                    st.write("")
                    if st.button("✅ MARCAR LEITURA CONCLUÍDA", key=f"done_{pasta}_{sub}", use_container_width=True):
                        st.session_state.db[pasta][sub]["contagem"] = dados.get("contagem", 0) + 1
                        st.session_state.db[pasta][sub]["ultima_data"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        salvar(st.session_state.db)
                        st.balloons()
                        st.rerun()
