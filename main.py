import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerenciador de Estudos", layout="wide", page_icon="📄")

# --- BARRA LATERAL (APENAS PDF) ---
st.sidebar.title("📚 Navegação")
menu = st.sidebar.radio("Selecione:", ["PDF"])

# --- ÁREA PRINCIPAL: PDF ---
if menu == "PDF":
    st.title("📂 Meus Materiais em PDF")
    
    # Espaço para o painel de gerenciamento
    with st.expander("➕ Adicionar Novo PDF", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            nome_pdf = st.text_input("Nome do Material (Ex: Direito Administrativo)")
            arquivo = st.file_uploader("Escolha o arquivo PDF", type=["pdf"])
        
        with col2:
            categoria = st.selectbox("Pasta/Concurso", ["PMPE", "PCPE", "Geral"])
        
        if st.button("Salvar PDF"):
            if nome_pdf and arquivo:
                # Aqui futuramente salvaremos o arquivo
                st.success(f"✅ O arquivo '{nome_pdf}' foi adicionado à pasta {categoria}!")
            else:
                st.error("⚠️ Por favor, preencha o nome e selecione um arquivo.")

    st.divider()

    # --- LISTAGEM DE MATERIAIS (EXEMPLO VISUAL) ---
    st.subheader("📌 Arquivos Disponíveis")
    
    # Mockup de como aparecerá na tela
    col_pdf1, col_pdf2 = st.columns(2)
    
    with col_pdf1:
        with st.container(border=True):
            st.write("📄 **Apostila_RLM_V1.pdf**")
            st.caption("Pasta: PMPE")
            st.button("Visualizar PDF", key="v1")

    with col_pdf2:
        with st.container(border=True):
            st.write("📄 **Direito_Constitucional_Resumo.pdf**")
            st.caption("Pasta: PCPE")
            st.button("Visualizar PDF", key="v2")
