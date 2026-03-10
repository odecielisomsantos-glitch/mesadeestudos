import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('estudos_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia TEXT,
            tipo_material TEXT,
            assunto TEXT,
            tempo_minutos INTEGER,
            questoes_feitas INTEGER,
            questoes_acertos INTEGER,
            data DATE
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("🎯 Menu de Navegação")
pagina = st.sidebar.radio("Ir para:", ["📝 Registrar Estudo", "📊 Dashboard & Análise", "📅 Calendário"])

# --- PÁGINA 1: REGISTRO ---
if pagina == "📝 Registrar Estudo":
    st.title("📝 Novo Registro de Estudo")
    
    with st.form("form_estudos", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            materia = st.selectbox("Matéria", ["Programação", "Matemática", "Direito", "Português", "Outros"])
            data_estudo = st.date_input("Data do Estudo", date.today())
            tipo_material = st.radio("Tipo de Material", ["Vídeo Aula", "PDF / Leitura"])
            
        with col2:
            assunto = st.text_input("Assunto detalhado")
            tempo = st.number_input("Tempo investido (minutos)", min_value=0, step=5)
            
        st.divider()
        st.subheader("✍️ Desempenho em Questões")
        c1, c2 = st.columns(2)
        q_feitas = c1.number_input("Questões Feitas", min_value=0, step=1)
        q_acertos = c2.number_input("Questões Certas", min_value=0, step=1)
        
        if st.form_submit_button("Salvar Registro"):
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO registros (materia, tipo_material, assunto, tempo_minutos, questoes_feitas, questoes_acertos, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (materia, tipo_material, assunto, tempo, q_feitas, q_acertos, data_estudo))
            conn.commit()
            st.success("Dados salvos com sucesso!")

# --- PÁGINA 2: DASHBOARD ---
elif pagina == "📊 Dashboard & Análise":
    st.title("📊 Análise de Desempenho")
    
    df = pd.read_sql_query("SELECT * FROM registros", conn)
    df['data'] = pd.to_datetime(df['data'])

    if not df.empty:
        # Filtro de Período
        st.sidebar.divider()
        data_inicio = st.sidebar.date_input("Início", df['data'].min())
        data_fim = st.sidebar.date_input("Fim", df['data'].max())
        
        mask = (df['data'].dt.date >= data_inicio) & (df['data'].dt.date <= data_fim)
        df_filtrado = df.loc[mask]

        # Métricas Principais
        m1, m2, m3 = st.columns(3)
        total_horas = df_filtrado['tempo_minutos'].sum() / 60
        total_q = df_filtrado['questoes_feitas'].sum()
        acertos = df_filtrado['questoes_acertos'].sum()
        perc = (acertos / total_q * 100) if total_q > 0 else 0
        
        m1.metric("Tempo Total", f"{total_horas:.1f}h")
        m2.metric("Questões", total_q)
        m3.metric("Aproveitamento", f"{perc:.1f}%")

        # Gráficos
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            fig_tempo = px.pie(df_filtrado, values='tempo_minutos', names='materia', title="Tempo por Matéria")
            st.plotly_chart(fig_tempo, use_container_width=True)
            
        with col_graf2:
            fig_tipo = px.bar(df_filtrado, x='tipo_material', y='tempo_minutos', color='materia', title="Aula vs PDF (minutos)")
            st.plotly_chart(fig_tipo, use_container_width=True)

        st.subheader("📈 Evolução de Acertos")
        fig_evolucao = px.line(df_filtrado.sort_values('data'), x='data', y='questoes_acertos', title="Acertos ao longo do tempo")
        st.plotly_chart(fig_evolucao, use_container_width=True)
    else:
        st.warning("Ainda não há dados para gerar o dashboard.")

# --- PÁGINA 3: CALENDÁRIO ---
elif pagina == "📅 Calendário":
    st.title("📅 Histórico Diário")
    df = pd.read_sql_query("SELECT * FROM registros ORDER BY data DESC", conn)
    
    if not df.empty:
        # Visualização em estilo lista/calendário simples
        selected_date = st.date_input("Selecione uma data para ver o que estudou:")
        dia_especifico = df[df['data'] == str(selected_date)]
        
        if not dia_especifico.empty:
            st.write(f"Estudos de {selected_date}:")
            st.table(dia_especifico[['materia', 'tipo_material', 'assunto', 'tempo_minutos']])
        else:
            st.info("Nenhum registro para este dia.")
            
        st.divider()
        st.subheader("Todos os registros")
        st.dataframe(df, use_container_width=True)
