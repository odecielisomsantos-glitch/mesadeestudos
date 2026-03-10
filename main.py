import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('estudos.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia TEXT,
            assunto TEXT,
            tempo_minutos INTEGER,
            data TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# --- INTERFACE ---
st.set_page_config(page_title="Monitor de Estudos", layout="centered")
st.title("📚 Meu Dashboard de Estudos")

# Formulário de Entrada
with st.form("registro_estudo"):
    st.subheader("Novo Registro")
    materia = st.selectbox("Matéria", ["Programação", "Matemática", "Inglês", "Design", "Outros"])
    assunto = st.text_input("Assunto detalhado")
    tempo = st.number_input("Tempo investido (minutos)", min_value=5, step=5)
    
    submitted = st.form_submit_button("Salvar Progresso")
    
    if submitted:
        data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor.execute(
            'INSERT INTO registros (materia, assunto, tempo_minutos, data) VALUES (?, ?, ?, ?)',
            (materia, assunto, tempo, data_hoje)
        )
        conn.commit()
        st.success("Estudo registrado com sucesso!")

# --- VISUALIZAÇÃO DOS DADOS ---
st.divider()
st.subheader("📈 Histórico de Atividades")

# Carregar dados do banco para o Pandas
df = pd.read_sql_query("SELECT * FROM registros ORDER BY id DESC", conn)

if not df.empty:
    # Métricas rápidas
    total_minutos = df['tempo_minutos'].sum()
    st.metric("Total de Horas", f"{total_minutos / 60:.1f}h")
    
    # Tabela de dados
    st.dataframe(df.drop(columns=['id']), use_container_width=True)
    
    # Gráfico simples
    st.bar_chart(df.groupby('materia')['tempo_minutos'].sum())
else:
    st.info("Nenhum registro encontrado. Comece a estudar agora!")
