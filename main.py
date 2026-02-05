import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Minha Mesa de Estudos", layout="wide", page_icon="📚")

# 2. Menu Lateral de Navegação
st.sidebar.title("📌 Navegação")
pagina = st.sidebar.radio("Ir para:", ["Início", "Flashcards", "Cronograma", "Checklist"])

# --- PÁGINA: INÍCIO ---
if pagina == "Início":
    st.title("📚 Bem-vindo à sua Mesa de Estudos")
    st.markdown("""
    Este é o seu portal de produtividade. Selecione uma ferramenta no menu ao lado para começar!
    
    * **Flashcards:** Teste seus conhecimentos.
    * **Cronograma:** Organize seu dia.
    * **Checklist:** Monitore seu progresso nas matérias.
    """)
    st.image("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60")

# --- PÁGINA: FLASHCARDS ---
elif pagina == "Flashcards":
    st.title("🗂️ Meus Flashcards")
    
    # Banco de dados de exemplo
    flashcards = [
        {"pergunta": "O que é o Teorema de Pitágoras?", "resposta": "A² = B² + C² (Em um triângulo retângulo)"},
        {"pergunta": "Qual a capital do Brasil?", "resposta": "Brasília"},
        {"pergunta": "Como se define uma variável em Python?", "resposta": "Nomeando-a e atribuindo valor com '=', ex: x = 10"}
    ]

    if "card_idx" not in st.session_state:
        st.session_state.card_idx = 0
        st.session_state.ver_resposta = False

    card = flashcards[st.session_state.card_idx]

    with st.container(border=True):
        st.subheader("Pergunta:")
        st.write(card["pergunta"])
        
        if st.button("Mostrar Resposta"):
            st.session_state.ver_resposta = True
            
        if st.session_state.ver_resposta:
            st.success(f"**Resposta:** {card['resposta']}")
            if st.button("Próximo Card"):
                st.session_state.card_idx = (st.session_state.card_idx + 1) % len(flashcards)
                st.session_state.ver_resposta = False
                st.rerun()

# --- PÁGINA: CRONOGRAMA ---
elif pagina == "Cronograma":
    st.title("📅 Cronograma Semanal")
    
    dados_cronograma = {
        "Horário": ["08:00 - 10:00", "10:00 - 12:00", "14:00 - 16:00", "16:00 - 18:00"],
        "Segunda": ["Matemática", "Português", "Física", "Revisão"],
        "Terça": ["História", "Geografia", "Biologia", "Exercícios"],
        "Quarta": ["Química", "Inglês", "Literatura", "Simulado"]
    }
    
    df = pd.DataFrame(dados_cronograma)
    st.table(df)

# --- PÁGINA: CHECKLIST ---
elif pagina == "Checklist":
    st.title("✅ Checklist de Matérias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Exatas")
        st.checkbox("Álgebra Linear")
        st.checkbox("Cinemática")
        st.checkbox("Tabela Periódica")
        
    with col2:
        st.header("Humanas")
        st.checkbox("Revolução Industrial")
        st.checkbox("Era Vargas")
        st.checkbox("Gramática Aplicada")
