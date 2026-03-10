import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Monitor de Estudos Pro", layout="wide", page_icon="📚")

# --- FUNÇÕES DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('estudos_v4.db', check_same_thread=False)
    c = conn.cursor()
    # Tabela de registros de estudo
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
    # Tabela de matérias cadastradas
    c.execute('CREATE TABLE IF NOT EXISTS materias (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)')
    
    # Inserir matérias iniciais se estiver vazio
    c.execute('SELECT COUNT(*) FROM materias')
    if c.fetchone()[0] == 0:
        materias_padrao = [("Programação",), ("Matemática",), ("Português",), ("Inglês",)]
        c.executemany('INSERT INTO materias (nome) VALUES (?)', materias_padrao)
    
    conn.commit()
    return conn

conn = init_db()

def get_materias():
    df_m = pd.read_sql_query("SELECT nome FROM materias ORDER BY nome", conn)
    return df_m['nome'].tolist()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("🎯 Navegação")
pagina = st.sidebar.radio("Ir para:", ["📝 Registrar Estudo", "📊 Dashboard", "📅 Histórico & Calendário", "⚙️ Configurar Matérias"])

# --- PÁGINA 1: REGISTRAR ESTUDO ---
if pagina == "📝 Registrar Estudo":
    st.title("📝 Novo Registro de Estudo")
    lista_materias = get_materias()
    
    if not lista_materias:
        st.warning("⚠️ Nenhuma matéria cadastrada. Vá em 'Configurar Matérias' primeiro.")
    else:
        with st.form("form_estudos", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                materia = st.selectbox("Selecione a Matéria", lista_materias)
                data_estudo = st.date_input("Data do Estudo", date.today())
                tipo_material = st.radio("Tipo de Estudo", ["Vídeo Aula", "PDF / Leitura", "Apenas Questões"])
                
            with col2:
                assunto = st.text_input("Assunto / Tópico detalhado")
                tempo = st.number_input("Tempo investido (minutos)", min_value=0, step=5)
            
            st.divider()
            st.subheader("✍️ Desempenho em Questões")
            c1, c2 = st.columns(2)
            q_feitas = c1.number_input("Questões Feitas", min_value=0, step=1)
            q_acertos = c2.number_input("Acertos", min_value=0, step=1)
            
            btn_salvar = st.form_submit_button("Salvar Progresso")
            
            if btn_salvar:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO registros (materia, tipo_material, assunto, tempo_minutos, questoes_feitas, questoes_acertos, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (materia, tipo_material, assunto, tempo, q_feitas, q_acertos, data_estudo))
                conn.commit()
                st.success(f"Registro de {materia} salvo com sucesso!")

# --- PÁGINA 2: DASHBOARD ---
elif pagina == "📊 Dashboard":
    st.title("📊 Análise de Desempenho")
    df = pd.read_sql_query("SELECT * FROM registros", conn)
    df['data'] = pd.to_datetime(df['data'])

    if not df.empty:
        # Filtro lateral de período
        st.sidebar.divider()
        st.sidebar.subheader("Filtros")
        data_ini = st.sidebar.date_input("Início", df['data'].min())
        data_fim = st.sidebar.date_input("Fim", df['data'].max())
        
        mask = (df['data'].dt.date >= data_ini) & (df['data'].dt.date <= data_fim)
        df_f = df.loc[mask]

        # Métricas de topo
        m1, m2, m3, m4 = st.columns(4)
        total_min = df_f['tempo_minutos'].sum()
        total_q = df_f['questoes_feitas'].sum()
        total_a = df_f['questoes_acertos'].sum()
        perc = (total_a / total_q * 100) if total_q > 0 else 0
        
        m1.metric("Tempo Total", f"{total_min/60:.1f}h")
        m2.metric("Questões", total_q)
        m3.metric("Acertos", total_a)
        m4.metric("Aproveitamento", f"{perc:.1f}%")

        # Gráficos
        col_esq, col_dir = st.columns(2)
        
        with col_esq:
            fig_tempo = px.pie(df_f, values='tempo_minutos', names='materia', title="Tempo por Matéria", hole=0.3)
            st.plotly_chart(fig_tempo, use_container_width=True)
            
        with col_dir:
            fig_tipo = px.bar(df_f, x='tipo_material', y='tempo_minutos', color='materia', title="Distribuição por Tipo de Material")
            st.plotly_chart(fig_tipo, use_container_width=True)

        st.subheader("📈 Evolução de Acertos (%)")
        df_evolucao = df_f.groupby('data').apply(lambda x: (x['questoes_acertos'].sum() / x['questoes_feitas'].sum() * 100) if x['questoes_feitas'].sum() > 0 else 0).reset_index()
        df_evolucao.columns = ['Data', 'Percentual']
        fig_line = px.line(df_evolucao, x='Data', y='Percentual', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Ainda não há dados para exibir. Comece a registrar seus estudos!")

# --- PÁGINA 3: HISTÓRICO & CALENDÁRIO ---
elif pagina == "📅 Histórico & Calendário":
    st.title("📅 Histórico de Estudos")
    df = pd.read_sql_query("SELECT * FROM registros ORDER BY data DESC", conn)
    
    if not df.empty:
        col_cal, col_list = st.columns([1, 2])
        
        with col_cal:
            data_sel = st.date_input("Filtrar por data específica:")
            
        dia_f = df[df['data'] == str(data_sel)]
        if not dia_f.empty:
            st.subheader(f"Resumo do dia {data_sel}")
            st.table(dia_f[['materia', 'tipo_material', 'assunto', 'tempo_minutos', 'questoes_feitas', 'questoes_acertos']])
        else:
            st.info(f"Sem registros para o dia {data_sel}")

        st.divider()
        st.subheader("Todos os registros")
        st.dataframe(df.drop(columns=['id']), use_container_width=True)
    else:
        st.info("Nenhum histórico disponível.")

# --- PÁGINA 4: CONFIGURAR MATÉRIAS ---
elif pagina == "⚙️ Configurar Matérias":
    st.title("⚙️ Gerenciar Matérias")
    
    with st.expander("➕ Adicionar Nova Matéria"):
        nova_mat = st.text_input("Nome da disciplina")
        if st.button("Cadastrar"):
            if nova_mat:
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO materias (nome) VALUES (?)", (nova_mat,))
                    conn.commit()
                    st.success(f"'{nova_mat}' adicionada com sucesso!")
                    st.rerun()
                except:
                    st.error("Erro: Esta matéria já existe.")
    
    st.subheader("Matérias Cadastradas")
    materias_list = get_materias()
    for m in materias_list:
        c1, c2 = st.columns([3, 1])
        c1.write(f"📚 {m}")
        if c2.button("Excluir", key=f"del_{m}"):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM materias WHERE nome = ?", (m,))
            conn.commit()
            st.rerun()
