import streamlit as st
import pandas as pd

st.set_page_config(page_title="Foco na Missão", layout="wide")

# CSS Simplificado (Tudo em um bloco só)
st.markdown("""<style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {background-color: #0E1117 !important;}
    h1, h2, h3, p, span, label {color: #FFF !important;}
    .card {background: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; margin-bottom: 10px;}
    .t {color: #808080; font-size: 12px; font-weight: bold;}
    .v {font-size: 28px; font-weight: bold; margin: 5px 0;}
    .f {color: #4CAF50; font-size: 13px;}
</style>""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: #4CAF50;'>🎯 FOCO NA MISSÃO</h2>", unsafe_allow_html=True)
    menu = st.radio("Navegação", ["Dashboard", "Registrar", "Cronômetro", "Desempenho", "Perfil"])

if menu == "Dashboard":
    st.markdown("### Olá, Guerreiro! 👋")
    
    # Gerando os 3 cards com apenas um loop
    cols = st.columns(3)
    metrics = [
        ("HORAS NA SEMANA", "7h 5min", "Meta: 30h"),
        ("QUESTÕES NA SEMANA", "162", "75% de acerto"),
        ("ACERTO GERAL", "80%", "1866 questões")
    ]
    
    for col, (tit, val, foot) in zip(cols, metrics):
        col.markdown(f'<div class="card"><div class="t">{tit}</div><div class="v">{val}</div><div class="f">{foot}</div></div>', unsafe_allow_html=True)

    st.write("---")
    st.markdown("### Progresso Semanal")
    st.progress(0.24)
    st.warning("⚠️ Você está abaixo do ritmo. Intensifique!")

    # Gráfico minimalista
    df = pd.DataFrame({'D': ['S','T','Q','Q','S','S','D'], 'H': [1, 2.5, 4, 1.5, 0, 0, 0]})
    st.bar_chart(df, x='D', y='H', color="#4CAF50")

elif menu == "Registrar":
    st.subheader("📝 Nova Missão")
    with st.form("estudo"):
        materia = st.selectbox("Matéria", ["Matemática", "Português", "Direito"])
        tempo = st.number_input("Minutos", 0)
        if st.form_submit_button("Salvar"):
            st.success("Salvo!")
