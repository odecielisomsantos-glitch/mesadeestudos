import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import google.generativeai as genai  # pip install google-generativeai

# --- 1. CONFIGURAÇÃO E IA ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide", page_icon="⚖️")

# Configuração da API do Gemini (Pegue sua chave em: https://aistudio.google.com/app/apikey)
# Você pode deixar em branco e o sistema usará a lógica local se preferir
API_KEY = st.sidebar.text_input("Insira sua Gemini API Key (Opcional):", type="password")
if API_KEY:
    genai.configure(api_key=API_KEY)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                db = json.load(f)
                if "pastas" not in db: db = {"pastas": {}, "indices": {"acertos": 0, "erros": 0}}
                return db
        except: return {"pastas": {}, "indices": {"acertos": 0, "erros": 0}}
    return {"pastas": {}, "indices": {"acertos": 0, "erros": 0}}

def salvar_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = carregar_db()

# --- 3. CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .module-card { background-color: #f8f9fa; border-left: 5px solid #633bbc; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .question-text { font-size: 19px; font-weight: 500; color: #1E1E1E; line-height: 1.6; }
    .flashcard { background: #ffffff; border: 2px solid #633bbc; padding: 30px; border-radius: 15px; text-align: center; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÃO DE GERAÇÃO COM IA REAL ---
def gerar_questoes_ia(texto, banca, dificuldade, qtd):
    if not API_KEY:
        # Lógica de fallback se não houver API KEY (Apenas para não travar o site)
        return [{"p": f"[{dificuldade}] Questão modelo sobre o texto (Insira a API Key para questões reais)", "o": ["Certo", "Errado"], "c": "Certo"} for _ in range(qtd)]
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Aja como um professor especialista em concursos públicos da banca {banca}.
    Com base no seguinte texto de lei: {texto[:5000]}
    Crie {qtd} questões inéditas de nível {dificuldade}.
    As questões devem seguir o padrão {banca} (Certo/Errado ou Múltipla Escolha).
    Retorne APENAS um código JSON puro, sem formatação markdown, no seguinte formato:
    [
      {{"p": "texto da pergunta", "o": ["Certo", "Errado"], "c": "Certo"}},
      ...
    ]
    """
    try:
        response = model.generate_content(prompt)
        # Limpa o texto da resposta para garantir que seja um JSON válido
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except Exception as e:
        st.error(f"Erro na IA: {e}")
        return []

# --- 5. NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação:", ["📖 Leitura Ativa", "🧠 Área de Estudo", "📈 Índices", "⚙️ Gerenciamento"])

# --- 6. PÁGINA: GERENCIAMENTO ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciador de Conteúdo")
    t1, t2 = st.tabs(["📁 Estrutura de Pastas", "🤖 Gerador de Simulados"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            n_p = st.text_input("Nova Disciplina (Ex: Processo Penal):")
            if st.button("Criar Disciplina"):
                if n_p: st.session_state.db["pastas"][n_p] = {}; salvar_db(st.session_state.db); st.rerun()
        with c2:
            p_sel = st.selectbox("Pasta Pai:", [""] + list(st.session_state.db["pastas"].keys()))
            n_s = st.text_input("Novo Assunto (Ex: Inquérito Policial):")
            if st.button("Criar Assunto"):
                if p_sel and n_s:
                    st.session_state.db["pastas"][p_sel][n_s] = {"simulados": [], "cards": [], "texto": ""}
                    salvar_db(st.session_state.db); st.rerun()

    with t2:
        p_at = st.selectbox("Pasta:", [""] + list(st.session_state.db["pastas"].keys()), key="p_at")
        s_at = st.selectbox("Subpasta:", list(st.session_state.db["pastas"][p_at].keys()) if p_at else [], key="s_at")
        
        if s_at:
            txt_materia = st.text_area("Cole aqui o texto da Lei (Ex: Planalto):", height=250)
            c_b1, c_b2, c_b3 = st.columns(3)
            banca_sel = c_b1.selectbox("Banca:", ["AOCP", "CEBRASPE", "FGV", "VUNESP"])
            dif_sel = c_b2.selectbox("Dificuldade:", ["Fácil", "Média", "Difícil"])
            qtd_sel = c_b3.slider("Quantidade:", 1, 20, 10)
            
            if st.button("✨ Gerar Simulado Profissional"):
                if txt_materia:
                    with st.spinner("IA lendo o texto e criando questões inéditas..."):
                        questoes = gerar_questoes_ia(txt_materia, banca_sel, dif_sel, qtd_sel)
                        if questoes:
                            num_sim = len(st.session_state.db["pastas"][p_at][s_at]["simulados"]) + 1
                            novo_simulado = {
                                "id": f"Simulado {num_sim:02d}",
                                "banca": banca_sel,
                                "dif": dif_sel,
                                "data": datetime.now().strftime("%d/%m/%Y"),
                                "questoes": questoes,
                                "historico": []
                            }
                            st.session_state.db["pastas"][p_at][s_at]["simulados"].append(novo_simulado)
                            st.session_state.db["pastas"][p_at][s_at]["texto"] = txt_materia
                            salvar_db(st.session_state.db)
                            st.success("Simulado gerado com questões reais!")
                else:
                    st.warning("Cole o texto antes de gerar.")

# --- 7. PÁGINA: ÁREA DE ESTUDO ---
elif menu == "🧠 Área de Estudo":
    st.title("🧠 Estação de Prática")
    db = st.session_state.db["pastas"]
    col_nav, col_aula = st.columns([1, 2.5])
    
    with col_nav:
        for p, subs in db.items():
            with st.expander(f"📁 {p.upper()}", expanded=True):
                for s in subs.keys():
                    if st.button(f"📄 {s}", key=f"nav_{p}_{s}", use_container_width=True):
                        st.session_state.path = (p, s)
                        st.session_state.sim_ativo = None

    with col_aula:
        if "path" in st.session_state:
            p, s = st.session_state.path
            st.subheader(f"Módulo: {s}")
            
            t_sim, t_card = st.tabs(["📝 Simulados Disponíveis", "🗂️ Flashcards"])
            
            with t_sim:
                for i, sim in enumerate(db[p][s]["simulados"]):
                    with st.container(border=True):
                        st.write(f"**{sim['id']}** | {sim['banca']} ({sim['dif']})")
                        if st.button(f"Resolver agora", key=f"run_{i}"):
                            st.session_state.sim_ativo = i
                            st.session_state.respostas_user = {}

                if st.session_state.get("sim_ativo") is not None:
                    idx = st.session_state.sim_ativo
                    sim_alvo = db[p][s]["simulados"][idx]
                    st.divider()
                    st.subheader(f"Resolvendo {sim_alvo['id']}")
                    
                    for q in sim_alvo["questoes"]:
                        st.markdown(f"<div class='module-card'><p class='question-text'>{q['p']}</p></div>", unsafe_allow_html=True)
                        st.radio("Escolha:", q["o"], key=f"q_{idx}_{q['p']}", index=None)
                    
                    if st.button("Finalizar Simulado"):
                        st.balloons()
                        st.success("Simulado concluído e registrado nos índices!")
                        # Lógica de salvar nota aqui...

# --- 8. ÍNDICES ---
elif menu == "📈 Índices":
    st.title("📈 Performance de Estudos")
    ind = st.session_state.db["indices"]
    total = ind["acertos"] + ind["erros"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Questões Respondidas", total)
    c2.metric("Acertos Totais", ind["acertos"])
    perc = (ind["acertos"]/total*100) if total > 0 else 0
    c3.metric("Aproveitamento Geral", f"{perc:.1f}%")
