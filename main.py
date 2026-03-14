import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(
    page_title="Foco na Missão",
    page_icon="🎯",
    layout="wide"
)

# 2. Injeção de CSS para o Tema Escuro Real e Fontes
st.markdown("""
    <style>
    /* Fundo total da página e da sidebar */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }

    /* Ajuste de fontes de títulos e textos */
    h1, h2, h3, p, span, label {
        color: #FFFFFF !important;
        font-family: 'sans serif';
    }

    /* Estilização dos Cards de Métricas */
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 10px;
    }
    
    .metric-title {
        color: #808080 !important;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .metric-value {
        color: #FFFFFF !important;
        font-size: 32px;
        font-weight: bold;
    }
    
    .metric-footer {
        color: #4CAF50 !important;
        font-size: 14px;
    }

    /* Barra lateral - itens do menu */
    [data-testid="stSidebarNav"] {
        background-color: #0E1117 !important;
    }
    
    /* Botões e Inputs */
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        width: 100%;
    }

    /* Estilo do Alerta (Warning) */
    .stAlert {
        background-color: #262730 !important;
        color: #FFA500 !important;
        border: 1px solid #FFA500;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: #4CAF50;'>🎯 FOCO NA MISSÃO</h2>", unsafe_allow_html=True)
    st.write("---")
    
    menu = st.radio(
        "Navegação",
        ["Dashboard", "Registrar Estudo", "Cronômetro", "Desempenho", "Relatórios", "Ranking", "Perfil"],
        index=0
    )
    
    st.write("---")
    st.caption("Você tem acesso completo!")

# --- CONTEÚDO PRINCIPAL ---
if menu == "Dashboard":
    st.markdown("### Olá, Guerreiro! 👋")
    st.markdown("<p style='color: #808080;'>sábado, 7 de fevereiro</p>", unsafe_allow_html=True)

    # Cards customizados via HTML para total controle de cor
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-title">HORAS NA SEMANA</div>
                <div class="metric-value">7h 5min</div>
                <div class="metric-footer">Meta: 30h</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-title">QUESTÕES NA SEMANA</div>
                <div class="metric-value">162</div>
                <div class="metric-footer">75% de acerto</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-title">ACERTO GERAL</div>
                <div class="metric-value">80%</div>
                <div class="metric-footer">1866 questões</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    st.markdown("### Horas de Estudo (Meta semanal)")
    progresso = 0.24 
    st.progress(progresso)
    st.markdown(f"**{progresso*100:.0f}% concluído** | <span style='color: #808080;'>Faltam 22h 55min</span>", unsafe_allow_html=True)
    
    st.warning("⚠️ Você está abaixo do ritmo. Intensifique!")

    # Gráfico
    st.markdown("### Horas por Dia")
    dados_grafico = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'],
        'Horas': [1, 2.5, 4, 1.5, 0, 0, 0]
    })
    # O gráfico do Streamlit segue o tema do sistema, mas as cores das barras podem ser fixadas
    st.bar_chart(data=dados_grafico, x='Dia', y='Horas', color="#4CAF50")

elif menu == "Registrar Estudo":
    st.header("📝 Registrar Nova Missão")
    # Conteúdo da página de registro...
