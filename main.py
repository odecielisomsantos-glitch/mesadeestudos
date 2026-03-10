import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Meu Dashboard de Estudos", layout="wide", page_icon="📚")

# --- FUNÇÕES DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('estudos_v5.db', check_same_thread=False)
    c = conn.cursor()
    # Tabela de registros de estudo
    c.execute('''CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT, materia TEXT, tipo_material TEXT, 
        assunto TEXT, tempo_minutos INTEGER, questoes_feitas INTEGER, 
        questoes_acertos INTEGER, data DATE)''')
    # Tabela de matérias
    c.execute('CREATE TABLE IF NOT EXISTS materias (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)')
    # Tabela de pastas (Keep)
    c.execute('CREATE TABLE IF NOT EXISTS pastas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, pai_id INTEGER DEFAULT NULL)')
    # Tabela de cards (Keep)
    c.execute('CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, conteudo TEXT, pasta_id INTEGER, cor TEXT, data_criacao DATETIME)')
    
    # Inserir matérias padrão se vazio
    c.execute('SELECT COUNT(*) FROM materias')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO materias (nome) VALUES (?)', [("Programação",), ("Matemática",), ("Português",)])
    conn.commit()
    return conn

conn = init_db()

def get_materias():
    return pd.read_sql_query("SELECT nome FROM materias ORDER BY nome", conn)['nome'].tolist()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("🎯 Navegação")
pagina = st.sidebar.radio("Ir para:", ["📝 Registrar Estudo", "📊 Dashboard", "📅 Histórico", "💡 Keep (Cards)", "⚙️ Configurações"])

# --- PÁGINA 1: REGISTRAR ESTUDO ---
if pagina == "📝 Registrar Estudo":
    st.title("📝 Novo Registro de Estudo")
    lista_materias = get_materias()
    
    with st.form("form_estudos", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            materia = st.selectbox("Matéria", lista_materias)
            data_estudo = st.date_input("Data", date.today())
            tipo_material = st.radio("Tipo de Material", ["Vídeo Aula", "PDF / Leitura", "Apenas Questões"])
        with col2:
            assunto = st.text_input("Assunto detalhado")
            tempo = st.number_input("Tempo (minutos)", min_value=0, step=5)
        
        st.divider()
        st.subheader("✍️ Questões")
        c1, c2 = st.columns(2)
        q_feitas = c1.number_input("Feitas", min_value=0)
        q_acertos = c2.number_input("Acertos", min_value=0)
        
        if st.form_submit_button("Salvar Progresso"):
            cursor = conn.cursor()
            cursor.execute('INSERT INTO registros (materia, tipo_material, assunto, tempo_minutos, questoes_feitas, questoes_acertos, data) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (materia, tipo_material, assunto, tempo, q_feitas, q_acertos, data_estudo))
            conn.commit()
            st.success("Salvo com sucesso!")

# --- PÁGINA 2: DASHBOARD ---
elif pagina == "📊 Dashboard":
    st.title("📊 Análise de Desempenho")
    df = pd.read_sql_query("SELECT * FROM registros", conn)
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'])
        # Filtro de Período
        st.sidebar.subheader("Filtro de Data")
        data_ini = st.sidebar.date_input("Início", df['data'].min())
        data_fim = st.sidebar.date_input("Fim", df['data'].max())
        df_f = df[(df['data'].dt.date >= data_ini) & (df['data'].dt.date <= data_fim)]

        # Métricas
        m1, m2, m3 = st.columns(3)
        total_q = df_f['questoes_feitas'].sum()
        total_a = df_f['questoes_acertos'].sum()
        m1.metric("Tempo Total", f"{df_f['tempo_minutos'].sum()/60:.1f}h")
        m2.metric("Total Questões", total_q)
        m3.metric("Aproveitamento", f"{(total_a/total_q*100 if total_q > 0 else 0):.1f}%")

        # Gráficos
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.plotly_chart(px.pie(df_f, values='tempo_minutos', names='materia', title="Tempo por Matéria", hole=0.4))
        with col_g2:
            st.plotly_chart(px.bar(df_f, x='tipo_material', y='tempo_minutos', color='materia', title="Distribuição por Material"))
    else:
        st.info("Sem dados registrados.")

# --- PÁGINA 3: HISTÓRICO ---
elif pagina == "📅 Histórico":
    st.title("📅 Histórico Diário")
    df = pd.read_sql_query("SELECT * FROM registros ORDER BY data DESC", conn)
    st.dataframe(df, use_container_width=True)

# --- PÁGINA 4: KEEP (CARDS E PASTAS) ---
elif pagina == "💡 Keep (Cards)":
    st.title("💡 Keep: Notas e Resumos")
    
    # Gerenciar Pastas na Sidebar
    st.sidebar.divider()
    with st.sidebar.expander("📂 Gerenciar Pastas"):
        nova_p = st.text_input("Nome da Pasta")
        df_p_check = pd.read_sql_query("SELECT * FROM pastas", conn)
        pai_p = st.selectbox("Pasta Pai (Subpasta)", ["Nenhuma"] + df_p_check['nome'].tolist())
        if st.button("Criar Pasta"):
            pai_id = df_p_check[df_p_check['nome'] == pai_p]['id'].values[0] if pai_p != "Nenhuma" else None
            conn.cursor().execute("INSERT INTO pastas (nome, pai_id) VALUES (?, ?)", (nova_p, pai_id))
            conn.commit()
            st.rerun()

    # Seleção de Pasta para exibição
    df_pastas = pd.read_sql_query("SELECT * FROM pastas", conn)
    pasta_selecionada = st.selectbox("📂 Selecione a Pasta/Subpasta", ["Todas"] + df_pastas['nome'].tolist())
    p_id_filtro = df_pastas[df_pastas['nome'] == pasta_selecionada]['id'].values[0] if pasta_selecionada != "Todas" else None

    # Criar Card
    with st.expander("➕ Adicionar Novo Card"):
        c_tit = st.text_input("Título")
        c_cor = st.color_picker("Cor", "#1e1e1e")
        c_cont = st.text_area("Conteúdo (Markdown)")
        c_pasta = st.selectbox("Salvar na pasta:", df_pastas['nome'].tolist())
        if st.button("Fixar Nota"):
            p_id_salvar = df_pastas[df_pastas['nome'] == c_pasta]['id'].values[0]
            conn.cursor().execute("INSERT INTO cards (titulo, conteudo, pasta_id, cor, data_criacao) VALUES (?, ?, ?, ?, ?)",
                                  (c_tit, c_cont, p_id_salvar, c_cor, datetime.now()))
            conn.commit()
            st.rerun()

    # Mostrar Cards
    query = "SELECT * FROM cards" + (f" WHERE pasta_id = {p_id_filtro}" if p_id_filtro else "")
    df_cards = pd.read_sql_query(query, conn)
    
    cols = st.columns(3)
    for i, (_, card) in enumerate(df_cards.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""<div style="background-color:{card['cor']}; padding:15px; border-radius:10px; border:1px solid #444; margin-bottom:10px">
                <h4 style='margin:0'>{card['titulo']}</h4><p style='font-size:13px'>{card['conteudo']}</p></div>""", unsafe_allow_html=True)
            if st.button("Apagar", key=f"del_{card['id']}"):
                conn.cursor().execute("DELETE FROM cards WHERE id = ?", (card['id'],))
                conn.commit()
                st.rerun()

# --- PÁGINA 5: CONFIGURAÇÕES ---
elif pagina == "⚙️ Configurações":
    st.title("⚙️ Gerenciar Matérias")
    with st.form("add_mat"):
        nova_m = st.text_input("Nova Matéria")
        if st.form_submit_button("Adicionar"):
            try:
                conn.cursor().execute("INSERT INTO materias (nome) VALUES (?)", (nova_m,))
                conn.commit()
                st.rerun()
            except: st.error("Matéria já existe.")
    
    mats = get_materias()
    for m in mats:
        col_a, col_b = st.columns([4,1])
        col_a.write(m)
        if col_b.button("Remover", key=f"rm_{m}"):
            conn.cursor().execute("DELETE FROM materias WHERE nome = ?", (m,))
            conn.commit()
            st.rerun()
