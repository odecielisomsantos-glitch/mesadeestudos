import streamlit as st
import json
import os

# --- CONFIGURAÇÃO E DADOS ---
st.set_page_config(page_title="Mesa de Estudos", layout="wide")
DB_FILE = "meus_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "dados" not in st.session_state: st.session_state.dados = carregar()
if "pasta_ativa" not in st.session_state: st.session_state.pasta_ativa = None

# --- BARRA LATERAL (LIMPA) ---
menu = st.sidebar.radio("Navegação", ["Flashcards", "Cronograma", "Checklist"])

# --- PÁGINA: FLASHCARDS ---
if menu == "Flashcards":
    st.title("🗂️ Central de Flashcards")
    
    # --- ÁREA DE GERENCIAMENTO (NA DIREITA) ---
    with st.expander("🛠️ PAINEL DE CRIAÇÃO (Clique para expandir)", expanded=False):
        aba1, aba2, aba3 = st.tabs(["📁 Nova Pasta", "📚 Nova Matéria", "🃏 Novo Card/Subtópico"])
        
        with aba1:
            n_pasta = st.text_input("Nome do Concurso")
            if st.button("Criar Pasta"):
                if n_pasta:
                    st.session_state.dados[n_pasta] = {}
                    salvar(st.session_state.dados)
                    st.success(f"✅ Pasta '{n_pasta}' criada com sucesso!")
                    st.rerun()

        with aba2:
            p_sel = st.selectbox("Escolha a Pasta:", list(st.session_state.dados.keys()), key="p_materia")
            n_materia = st.text_input("Nome da Matéria (ex: RLM)")
            if st.button("Adicionar Matéria"):
                if n_materia:
                    st.session_state.dados[p_sel][n_materia] = {}
                    salvar(st.session_state.dados)
                    st.success(f"✅ Matéria '{n_materia}' adicionada em {p_sel}!")
                    st.rerun()

        with aba3:
            p_sel2 = st.selectbox("Pasta:", list(st.session_state.dados.keys()), key="p_card")
            m_sel = st.selectbox("Matéria:", list(st.session_state.dados.get(p_sel2, {}).keys()))
            subtopico = st.text_input("Nome do Subtópico (Seta)")
            conteudo = st.text_area("Conteúdo do Flashcard")
            if st.button("Salvar Flashcard"):
                if subtopico:
                    if subtopico not in st.session_state.dados[p_sel2][m_sel]:
                        st.session_state.dados[p_sel2][m_sel][subtopico] = conteudo
                        salvar(st.session_state.dados)
                        st.success(f"✅ Card '{subtopico}' criado!")
                        st.rerun()

    st.divider()

    # --- EXIBIÇÃO ---
    if st.session_state.pasta_ativa is None:
        st.subheader("📂 Suas Pastas")
        cols = st.columns(4)
        for i, pasta in enumerate(st.session_state.dados.keys()):
            with cols[i % 4]:
                with st.container(border=True):
                    # Placeholder para a capa do concurso
                    st.markdown(f"### 📑 {pasta}")
                    if st.button(f"Abrir {pasta}", key=f"btn_{pasta}"):
                        st.session_state.pasta_ativa = pasta
                        st.rerun()
    else:
        if st.button("⬅️ Voltar"):
            st.session_state.pasta_ativa = None
            st.rerun()
            
        st.header(f"📍 {st.session_state.pasta_ativa}")
        materias = st.session_state.dados[st.session_state.pasta_ativa]
        
        for materia, subtopicos in materias.items():
            # Pasta da Matéria
            with st.expander(f"📁 {materia.upper()}", expanded=True):
                for sub, resp in subtopicos.items():
                    # Subtópico com a seta
                    with st.expander(f"➡️ {sub}"):
                        st.write(resp)

# --- OUTRAS PÁGINAS ---
elif menu == "Cronograma":
    st.title("📅 Cronograma")
    st.info("Área em desenvolvimento")

elif menu == "Checklist":
    st.title("✅ Checklist")
    st.info("Área em desenvolvimento")
