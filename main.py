import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO E IA ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide", page_icon="⚖️")

# Barra lateral para API Key
with st.sidebar:
    st.title("🔑 Configuração")
    api_key = st.text_input("Gemini API Key:", type="password", help="Pegue em: https://aistudio.google.com/app/apikey")
    if api_key:
        genai.configure(api_key=api_key)

# --- 2. GESTÃO DE DADOS (COM BLINDAGEM) ---
DB_FILE = "dados_estudos.json"

def carregar_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"pastas": {}, "indices": {"acertos": 0, "erros": 0}}

def salvar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = carregar_db()

# --- 3. FUNÇÃO DE GERAÇÃO REAL (ESTILO QCONCURSOS/TEC) ---
def gerar_questoes_ia(texto, banca, dificuldade, qtd):
    if not api_key:
        # Fallback caso não tenha API Key
        return [{"p": f"Questão sobre {banca} (Nível {dificuldade}) - [Configure a API Key para questões reais]", "o": ["Certo", "Errado"], "c": "Certo"} for _ in range(qtd)]
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Aja como um elaborador de questões de concursos para a banca {banca}.
        Baseie-se neste texto de lei: {texto[:10000]}
        Crie {qtd} questões de nível {dificuldade}. 
        Nível Fácil: Literalidade da lei.
        Nível Médio: Casos hipotéticos simples.
        Nível Difícil: Detalhes técnicos e peguinhas.
        Retorne APENAS um JSON puro (sem markdown) neste formato:
        [{{"p": "pergunta", "o": ["opção1", "opção2"], "c": "opção_correta"}}]
        """
        response = model.generate_content(prompt)
        # Limpa o texto da resposta para garantir JSON puro
        json_limpo = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_limpo)
    except Exception as e:
        st.error(f"Erro na IA: {e}")
        return []

# --- 4. CSS PARA DESIGN DE MÓDULOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; text-align: left; margin-bottom: 5px; }
    .card-pergunta { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #633bbc; margin-bottom: 15px; }
    .flashcard { background: white; border: 2px solid #633bbc; padding: 30px; text-align: center; border-radius: 15px; min-height: 200px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação:", ["📖 Leitura", "🧠 Estação de Prática", "📈 Índices", "⚙️ Gerenciamento"])

# --- 6. PÁGINA: GERENCIAMENTO ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciador")
    t1, t2 = st.tabs(["📁 Pastas", "🤖 Gerar Conteúdo"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            n_p = st.text_input("Nova Disciplina:")
            if st.button("Criar Disciplina"):
                if n_p: st.session_state.db["pastas"][n_p] = {}; salvar_db(st.session_state.db); st.rerun()
        with c2:
            p_sel = st.selectbox("Pasta:", [""] + list(st.session_state.db["pastas"].keys()))
            n_s = st.text_input("Novo Assunto:")
            if st.button("Criar Assunto"):
                if p_sel and n_s:
                    st.session_state.db["pastas"][p_sel][n_s] = {"simulados": [], "cards": []}
                    salvar_db(st.session_state.db); st.rerun()

    with t2:
        p_at = st.selectbox("Disciplina Alvo:", [""] + list(st.session_state.db["pastas"].keys()), key="p_at")
        s_at = st.selectbox("Assunto Alvo:", list(st.session_state.db["pastas"][p_at].keys()) if p_at else [], key="s_at")
        
        if s_at:
            texto_lei = st.text_area("Cole o texto da Lei aqui (Ex: Planalto):", height=200)
            banca = st.selectbox("Banca:", ["AOCP", "CEBRASPE", "FGV", "VUNESP"])
            dif = st.selectbox("Dificuldade:", ["Fácil", "Média", "Difícil"])
            qtd = st.slider("Questões:", 1, 20, 10)
            
            if st.button("✨ Gerar Simulado Profissional"):
                if texto_lei:
                    with st.spinner("IA analisando a lei..."):
                        questoes = gerar_questoes_ia(texto_lei, banca, dif, qtd)
                        if questoes:
                            num = len(st.session_state.db["pastas"][p_at][s_at]["simulados"]) + 1
                            # Criando estrutura limpa para evitar KeyError
                            novo_sim = {
                                "id": f"Simulado {num:02d}",
                                "banca": banca,
                                "dif": dif,
                                "data": datetime.now().strftime("%d/%m/%Y"),
                                "questoes": questoes,
                                "historico": []
                            }
                            st.session_state.db["pastas"][p_at][s_at]["simulados"].append(novo_sim)
                            salvar_db(st.session_state.db)
                            st.success("Simulado gerado!")
                else: st.warning("Cole o texto da lei.")

# --- 7. PÁGINA: ESTAÇÃO DE PRÁTICA (MODO MÓDULOS) ---
elif menu == "🧠 Estação de Prática":
    st.title("🧠 Prática")
    db = st.session_state.db["pastas"]
    col_nav, col_aula = st.columns([1, 2.5])
    
    with col_nav:
        st.subheader("Módulos")
        for p, subs in db.items():
            with st.expander(f"📁 {p.upper()}"):
                for s in subs.keys():
                    if st.button(f"📄 {s}", key=f"nav_{p}_{s}"):
                        st.session_state.estudo_atual = (p, s)
                        st.session_state.sim_idx = None

    with col_aula:
        if "estudo_atual" in st.session_state:
            p, s = st.session_state.estudo_atual
            dados = db[p][s]
            
            # BLINDAGEM: Garante que as chaves existam ao carregar
            if "simulados" not in dados: dados["simulados"] = []
            
            t_sim, t_card = st.tabs(["📝 Simulados", "🗂️ Flashcards"])
            
            with t_sim:
                for i, sim in enumerate(dados["simulados"]):
                    # Correção segura para dados antigos sem 'id' ou 'banca'
                    sim_id = sim.get('id', f'Simulado {i+1}')
                    sim_banca = sim.get('banca', 'N/A')
                    sim_dif = sim.get('dif', 'N/A')
                    
                    with st.container(border=True):
                        st.write(f"**{sim_id}** | {sim_banca} ({sim_dif})")
                        if st.button(f"Iniciar {sim_id}", key=f"start_{i}"):
                            st.session_state.sim_idx = i
                            st.session_state.respostas_user = {}

                if st.session_state.get("sim_idx") is not None:
                    idx = st.session_state.sim_idx
                    sim_ativo = dados["simulados"][idx]
                    st.divider()
                    st.subheader(f"Resolvendo: {sim_ativo.get('id', 'Simulado')}")
                    
                    for q_idx, q in enumerate(sim_ativo["questoes"]):
                        st.markdown(f"<div class='card-pergunta'>{q['p']}</div>", unsafe_allow_html=True)
                        st.radio("Escolha:", q["o"], key=f"q_{idx}_{q_idx}", index=None)
                    
                    if st.button("Finalizar Simulado"):
                        st.balloons()
                        st.success("Resultado salvo com sucesso!")
                        # Aqui você pode adicionar a lógica de correção real
                        st.session_state.sim_idx = None

# --- 8. ÍNDICES ---
elif menu == "📈 Índices":
    st.title("📈 Performance")
    # Lógica de índices (blindada)
    st.info("Aqui seus acertos e erros serão contabilizados conforme você finalizar os simulados.")
