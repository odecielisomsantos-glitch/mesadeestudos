import streamlit as st
import json
import os

# Configuração e Banco de Dados (JSON)
st.set_page_config(page_title="Mesa de Estudos", layout="wide")
DB_FILE = "dados_estudos.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def salvar_dados(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "dados" not in st.session_state: st.session_state.dados = carregar_dados()
if "pasta_ativa" not in st.session_state: st.session_state.pasta_ativa = None

# --- SIDEBAR: CRIAÇÃO ---
st.sidebar.title("🛠️ Gerenciar Estudos")
with st.sidebar.expander("➕ Criar Nova Pasta (Capa)"):
    nova_pasta = st.text_input("Nome do Concurso/Pasta")
    if st.button("Criar Pasta"):
        if nova_pasta and nova_pasta not in st.session_state.dados:
            st.session_state.dados[nova_pasta] = {}
            salvar_dados(st.session_state.dados)
            st.rerun()

with st.sidebar.expander("📚 Adicionar Matéria"):
    pasta_sel = st.selectbox("Na pasta:", list(st.session_state.dados.keys()))
    nova_materia = st.text_input("Nome da Matéria")
    if st.button("Adicionar Matéria"):
        st.session_state.dados[pasta_sel][nova_materia] = []
        salvar_dados(st.session_state.dados)
        st.rerun()

with st.sidebar.expander("🃏 Adicionar Flashcard"):
    p_sel = st.selectbox("Pasta:", list(st.session_state.dados.keys()), key="p1")
    m_sel = st.selectbox("Matéria:", list(st.session_state.dados.get(p_sel, {}).keys()))
    pergunta = st.text_input("Subtópico/Pergunta")
    resposta = st.text_area("Conteúdo/Resposta")
    if st.button("Salvar Card"):
        st.session_state.dados[p_sel][m_sel].append({"q": pergunta, "r": resposta})
        salvar_dados(st.session_state.dados)
        st.rerun()

# --- ÁREA PRINCIPAL ---
if st.button("🏠 Voltar ao Início"): st.session_state.pasta_ativa = None

if st.session_state.pasta_ativa is None:
    st.title("📂 Minhas Pastas de Estudo")
    cols = st.columns(3)
    for i, pasta in enumerate(st.session_state.dados.keys()):
        with cols[i % 3]:
            # Visual de "Capa" similar à sua imagem
            with st.container(border=True):
                st.image("https://via.placeholder.com/300x150/262730/ffffff?text=ESTUDOS", use_container_width=True)
                if st.button(f"📂 {pasta}", use_container_width=True):
                    st.session_state.pasta_ativa = pasta
                    st.rerun()
else:
    st.title(f"📍 {st.session_state.pasta_ativa}")
    materias = st.session_state.dados[st.session_state.pasta_ativa]
    
    for materia, cards in materias.items():
        with st.expander(f"📁 {materia.upper()}", expanded=False):
            for card in cards:
                # O subtópico com a seta (expander aninhado)
                with st.expander(f"➡️ {card['q']}"):
                    st.info(card['r'])
