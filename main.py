import streamlit as st
import json
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gerenciador de Leitura", layout="wide", page_icon="📖")
DB_FILE = "dados_estudos_v2.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def salvar_dados(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar_dados()
if "f_sel" not in st.session_state: st.session_state.f_sel = None # Pasta selecionada
if "s_sel" not in st.session_state: st.session_state.s_sel = None # Subpasta selecionada

# --- BARRA LATERAL ---
st.sidebar.title("🎮 Painel")
menu = st.sidebar.radio("Ir para:", ["PDF (Leitura)", "Gerenciamento"])

# --- PÁGINA: GERENCIAMENTO ---
if menu == "Gerenciamento":
    st.title("⚙️ Gerenciar Conteúdo")
    
    tab1, tab2, tab3 = st.tabs(["📁 Criar Pasta", "📂 Criar Subpasta", "📝 Adicionar Texto"])
    
    with tab1:
        n_pasta = st.text_input("Nome da Matéria/Pasta")
        if st.button("Criar Pasta"):
            if n_pasta and n_pasta not in st.session_state.db:
                st.session_state.db[n_pasta] = {}
                salvar_dados(st.session_state.db)
                st.success(f"✅ Pasta '{n_pasta}' criada!")
                st.rerun()

    with tab2:
        p_escolhida = st.selectbox("Selecione a Pasta Pai:", list(st.session_state.db.keys()))
        n_sub = st.text_input("Nome do Assunto/Subpasta")
        if st.button("Criar Subpasta"):
            if n_sub:
                st.session_state.db[p_escolhida][n_sub] = ""
                salvar_dados(st.session_state.db)
                st.success(f"✅ Subpasta '{n_sub}' criada em {p_escolhida}!")
                st.rerun()

    with tab3:
        col1, col2 = st.columns(2)
        with col1: p_sel = st.selectbox("Pasta:", list(st.session_state.db.keys()), key="g_p")
        with col2: s_sel = st.selectbox("Subpasta:", list(st.session_state.db.get(p_sel, {}).keys()), key="g_s")
        
        texto_pdf = st.text_area("Cole o texto do material aqui:", height=400)
        if st.button("Salvar Conteúdo"):
            st.session_state.db[p_sel][s_sel] = texto_pdf
            salvar_dados(st.session_state.db)
            st.success("✅ Texto salvo! Pronto para leitura.")

# --- PÁGINA: PDF (LEITURA) ---
elif menu == "PDF (Leitura)":
    st.title("📖 Área de Leitura")

    # 1. Nível de Pastas (Matérias)
    if st.session_state.f_sel is None:
        st.subheader("Selecione a Matéria")
        for pasta in st.session_state.db.keys():
            if st.button(f"📁 {pasta}", use_container_width=True):
                st.session_state.f_sel = pasta
                st.rerun()

    # 2. Nível de Subpastas (Assuntos)
    elif st.session_state.s_sel is None:
        if st.button("⬅️ Voltar para Pastas"):
            st.session_state.f_sel = None
            st.rerun()
            
        st.subheader(f"📂 {st.session_state.f_sel}")
        subpastas = st.session_state.db[st.session_state.f_sel]
        
        for sub in subpastas.keys():
            if st.button(f"📄 {sub}", use_container_width=True):
                st.session_state.s_sel = sub
                st.rerun()

    # 3. Nível de Leitura (Texto)
    else:
        col_v, col_t = st.columns([1, 5])
        with col_v:
            if st.button("⬅️ Voltar"):
                st.session_state.s_sel = None
                st.rerun()
        with col_t:
            st.subheader(f"📖 Lendo: {st.session_state.s_sel}")

        st.divider()
        
        # Exibição do texto formatada para leitura repetitiva
        texto_final = st.session_state.db[st.session_state.f_sel][st.session_state.s_sel]
        
        if texto_final:
            st.markdown(f"""
            <div style="background-color: #f9f9f9; padding: 30px; border-radius: 10px; border-left: 5px solid #ff4b4b; line-height: 1.8; font-size: 20px; color: #31333F; text-align: justify;">
                {texto_final.replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            if st.button("🏁 Marcar como lido (Finalizar)", use_container_width=True):
                st.balloons()
                st.success("Parabéns! Mais uma repetição concluída.")
        else:
            st.warning("Ainda não há texto cadastrado para este assunto.")
