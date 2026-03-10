import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('estudos_v3.db', check_same_thread=False)
    c = conn.cursor()
    # Tabela de Registros
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
    # Tabela de Matérias (Nova!)
    c.execute('CREATE TABLE IF NOT EXISTS materias (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)')
    
    # Inserir matérias padrão se a tabela estiver vazia
    c.execute('SELECT COUNT(*) FROM materias')
    if c.fetchone()[0] == 0:
        materias_iniciais = [("Programação",), ("Matemática",), ("Português",)]
        c.executemany('INSERT INTO materias (nome) VALUES (?)', materias_iniciais)
    
    conn.commit()
    return conn

conn = init_db()

# Função auxiliar para buscar matérias
def get_materias():
    df_m = pd.read_sql_query("SELECT nome FROM materias ORDER BY nome", conn)
    return df_m['nome'].tolist()

# --- BARRA LATERAL ---
st.sidebar.title("🎯 Menu de Navegação")
pagina = st.sidebar.radio("Ir para:", ["📝 Registrar Estudo", "📊 Dashboard", "📅 Calendário", "⚙️ Gerenciar Matérias"])

# --- PÁGINA: GERENCIAR MATÉRIAS ---
if pagina == "⚙️ Gerenciar Matérias":
    st.title("⚙️ Configurações de Matérias")
    
    # Adicionar Nova Matéria
    with st.expander("➕ Adicionar Nova Matéria"):
        nova_materia = st.text_input("Nome da Matéria")
        if st.button("Salvar Matéria"):
            if nova_materia:
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO materias (nome) VALUES (?)", (nova_materia,))
                    conn.commit()
                    st.success(f"'{nova_materia}' adicionada!")
                    st.rerun()
                except:
                    st.error("Esta matéria já existe.")
    
    # Listar e Excluir Matérias
    st.subheader("Lista de Matérias Atuais")
    lista_m = get_materias()
    for m in lista_m:
        col_m, col_btn = st.columns([3, 1])
        col_m.write(f"📖 {m}")
        if col_btn.button("Excluir", key=m):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM materias WHERE nome = ?", (m,))
            conn.commit()
            st.rerun()

# --- PÁGINA: REGISTRAR ESTUDO (Atualizada) ---
elif pagina == "📝 Registrar Estudo":
    st.title("📝 Novo Registro")
    lista_materias = get_materias()
    
    with st.form("form_estudos", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            materia = st.selectbox("Selecione a Matéria", lista_materias)
            data_estudo = st.date_input("Data", date.today())
            tipo_material = st.radio("Material", ["Vídeo Aula", "PDF / Leitura"])
        with col2:
            assunto = st.text_input("Assunto")
            tempo = st.number_input("Tempo (min)", min_value=0, step=5)
            
        st.divider()
        st.subheader("✍️ Questões")
        c1, c2 = st.columns(2)
        q_feitas = c1.number_input("Feitas", min_value=0)
        q_acertos = c2.number_input("Acertos", min_value=0)
        
        if st.form_submit_button("Salvar Registro"):
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO registros (materia, tipo_material, assunto, tempo_minutos, questoes_feitas, questoes_acertos, data)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                           (materia, tipo_material, assunto, tempo, q_feitas, q_acertos, data_estudo))
            conn.commit()
            st.success("Salvo!")

# --- PÁGINA: DASHBOARD (Resumida para o exemplo) ---
elif pagina == "📊 Dashboard":
    st.title("📊 Dashboard")
    df = pd.read_sql_query("SELECT * FROM registros", conn)
    if not df.empty:
        # Gráfico de tempo por matéria
        fig = px.bar(df, x='materia', y='tempo_minutos', color='tipo_material', title="Tempo de Estudo")
        st.plotly_chart(fig)
        
        # Tabela de acertos
        df['perc'] = (df['questoes_acertos'] / df['questoes_feitas'] * 100).fillna(0)
        st.write("Desempenho por Matéria:")
        st.dataframe(df.groupby('materia')[['questoes_feitas', 'questoes_acertos', 'perc']].mean())
    else:
        st.info("Sem dados.")

# --- PÁGINA: CALENDÁRIO ---
elif pagina == "📅 Calendário":
    st.title("📅 Calendário")
    df = pd.read_sql_query("SELECT * FROM registros ORDER BY data DESC", conn)
    st.dataframe(df)
