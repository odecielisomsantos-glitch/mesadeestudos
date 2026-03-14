import streamlit as st
import pandas as pd

# 1. Configuração da Página e Estética Dark
st.set_page_config(
    page_title="Foco na Missão",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para forçar o tema escuro e customizar os cards
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #111111;
    }
    .main {
        background-color: #0E1117;
    }
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
    }
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🎯 FOCO NA MISSÃO")
    st.write("---")
    
    # Menu de Navegação
    menu = st.radio(
        "Navegação",
        ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Ranking", "Perfil"],
        index=0
    )
    
    st.write("---")
    st.caption("Você tem acesso completo!")

# --- CONTEÚDO PRINCIPAL: DASHBOARD ---
if menu == "Dashboard":
    st.write(f"### Olá, Guerreiro! 👋")
    st.caption("sábado, 7 de fevereiro")

    # Colunas para os Cards de Métricas (Igual à imagem)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="metric-card">
                <p style='color: gray; margin-bottom: 0;'>HORAS NA SEMANA</p>
                <h2 style='margin-top: 0;'>7h 5min</h2>
                <p style='color: #4CAF50; font-size: 0.8rem;'>Meta: 30h</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="metric-card">
                <p style='color: gray; margin-bottom: 0;'>QUESTÕES NA SEMANA</p>
                <h2 style='margin-top: 0;'>162</h2>
                <p style='color: #4CAF50; font-size: 0.8rem;'>75% de acerto</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="metric-card">
                <p style='color: gray; margin-bottom: 0;'>ACERTO GERAL</p>
                <h2 style='margin-top: 0;'>80%</h2>
                <p style='color: #4CAF50; font-size: 0.8rem;'>1866 questões</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # Barra de Progresso
    st.write("### Horas de Estudo (Meta semanal)")
    progresso = 0.24 # 24% conforme imagem
    st.progress(progresso)
    st.write(f"**{progresso*100:.0f}% concluído** | Faltam 22h 55min")
    
    st.warning("⚠️ Você está abaixo do ritmo. Intensifique!")

    # Gráfico de exemplo (Horas por dia)
    st.write("### Horas por Dia")
    dados_grafico = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'],
        'Horas': [1, 2.5, 4, 1.5, 0, 0, 0]
    })
    st.bar_chart(data=dados_grafico, x='Dia', y='Horas', color="#4CAF50")

# --- OUTRAS PÁGINAS (Simulação) ---
elif menu == "Registrar Estudo":
    st.header("📝 Registrar Nova Missão")
    materia = st.selectbox("Matéria", ["Matemática", "Português", "Direito", "Informática"])
    tempo = st.number_input("Tempo de estudo (minutos)", min_value=0)
    questoes = st.number_input("Questões resolvidas", min_value=0)
    acertos = st.number_input("Acertos", min_value=0)
    
    if st.button("Salvar na Missão"):
        st.success(f"Registro de {materia} salvo com sucesso!")

else:
    st.write(f"Você selecionou: **{menu}**. Esta página está em desenvolvimento.")
