import streamlit as st

st.set_page_config(page_title="Mesa de Estudos", page_icon="📚")

# --- NAVEGAÇÃO LATERAL ---
pagina = st.sidebar.radio("Menu", ["Início", "Flashcards", "Cronograma", "Checklist"])

# --- PÁGINA: FLASHCARDS (ESTRUTURA DE PASTAS) ---
if pagina == "Flashcards":
    st.title("🗂️ Meus Flashcards")
    
    # Exemplo: Capa PMPE (Use o expander para ser a 'pasta')
    with st.expander("📁 CONCURSO PMPE", expanded=True):
        
        # Subtópico com a seta (Expander dentro de Expander)
        with st.expander("➡️ Raciocínio Lógico"):
            st.write("**P:** Qual a negação de 'Todo'?")
            st.info("**R:** Pelo menos um + negação.")
            
        with st.expander("➡️ Direito Constitucional"):
            st.write("**P:** O que é remédio constitucional?")
            st.info("**R:** Garantias para proteger direitos fundamentais.")

# --- PÁGINA: CRONOGRAMA ---
elif pagina == "Cronograma":
    st.title("📅 Cronograma")
    st.table({"Hora": ["08:00", "14:00"], "Matéria": ["PMPE - RLM", "PMPE - Direito"]})

# --- PÁGINA: CHECKLIST ---
elif pagina == "Checklist":
    st.title("✅ Checklist")
    for m in ["RLM", "Direito", "Português"]:
        st.checkbox(m)

else:
    st.title("📚 Mesa de Estudos")
    st.write("Selecione uma opção no menu lateral para começar.")
