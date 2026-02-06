import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide", page_icon="📚")

# --- 2. GESTÃO DE DADOS (PERSISTÊNCIA) ---
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
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = carregar_db()

# --- 3. ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .stExpander details summary p { font-size: 18px !important; font-weight: bold; }
    .card-pergunta { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #633bbc; margin-bottom: 20px; font-size: 18px; }
    .flashcard { background: white; border: 2px solid #633bbc; padding: 30px; text-align: center; border-radius: 15px; min-height: 180px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVEGAÇÃO LATERAL ---
menu = st.sidebar.radio("Navegação:", ["📖 Leitura Ativa", "🧠 Área de Estudo", "📈 Índices", "⚙️ Gerenciamento"])

# --- 5. PÁGINA: GERENCIAMENTO (FÁBRICA DE CONTEÚDO) ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciador de Conteúdo")
    tab_pastas, tab_ia = st.tabs(["📁 Organizar Pastas", "🤖 Gerar Simulado e Cards"])
    
    with tab_pastas:
        c1, c2 = st.columns(2)
        with c1:
            n_pasta = st.text_input("Nova Disciplina (Ex: Processo Penal):")
            if st.button("Criar Disciplina"):
                if n_pasta:
                    st.session_state.db["pastas"][n_pasta] = {}
                    salvar_db(st.session_state.db); st.rerun()
        with c2:
            p_alvo = st.selectbox("Pasta Pai:", [""] + list(st.session_state.db["pastas"].keys()))
            n_sub = st.text_input("Novo Assunto (Ex: Inquérito Policial):")
            if st.button("Vincular Assunto"):
                if p_alvo and n_sub:
                    st.session_state.db["pastas"][p_alvo][n_sub] = {"simulados": [], "cards": [], "texto_base": ""}
                    salvar_db(st.session_state.db); st.rerun()

    with tab_ia:
        st.subheader("🤖 Gerador Inteligente")
        p_sel = st.selectbox("Selecione a Pasta:", [""] + list(st.session_state.db["pastas"].keys()), key="p_g")
        s_opt = list(st.session_state.db["pastas"][p_sel].keys()) if p_sel else []
        s_sel = st.selectbox("Selecione a Subpasta:", s_opt, key="s_g")
        
        if s_sel:
            txt_input = st.text_area("Cole o texto da matéria aqui para criar o material:", height=200)
            banca = st.selectbox("Banca Base:", ["AOCP", "CEBRASPE", "FGV", "VUNESP"])
            qtd_q = st.slider("Quantidade de Questões:", 1, 20, 10)
            
            if st.button("✨ Gerar Simulado e Cards"):
                if txt_input:
                    # BLINDAGEM CONTRA KEYERROR
                    sub_alvo = st.session_state.db["pastas"][p_sel][s_sel]
                    if "simulados" not in sub_alvo: sub_alvo["simulados"] = []
                    if "cards" not in sub_alvo: sub_alvo["cards"] = []
                    
                    num_sim = len(sub_alvo["simulados"]) + 1
                    
                    # Criação das questões (Simulando IA baseada no seu texto)
                    novas_q = []
                    for i in range(qtd_q):
                        novas_q.append({
                            "id": i+1,
                            "p": f"(Questão {i+1} - {banca}) De acordo com o texto sobre {s_sel}, o item X está correto?",
                            "o": ["Certo", "Errado"],
                            "c": "Certo"
                        })
                    
                    # Salva o novo simulado
                    sub_alvo["simulados"].append({
                        "id_nome": f"Simulado {num_sim:02d}",
                        "banca": banca,
                        "data": datetime.now().strftime("%d/%m/%Y"),
                        "questoes": novas_q,
                        "historico": []
                    })
                    
                    # Salva Cards baseados no assunto
                    sub_alvo["cards"].append({"f": f"Conceito fundamental de {s_sel}?", "v": "Informação extraída do seu texto."})
                    
                    salvar_db(st.session_state.db)
                    st.success(f"Simulado {num_sim:02d} e Cards criados!")
                    st.rerun()
                else:
                    st.error("Insira o texto para processar.")

# --- 6. PÁGINA: ÁREA DE ESTUDO (AONDE VOCÊ ESTUDA) ---
elif menu == "🧠 Área de Estudo":
    st.title("🧠 Estação de Prática")
    
    col_nav, col_conteudo = st.columns([1, 2.5])
    
    with col_nav:
        st.subheader("Módulos")
        for p, subs in st.session_state.db["pastas"].items():
            with st.expander(f"📁 {p}"):
                for s in subs.keys():
                    if st.button(f"📄 {s}", key=f"btn_{p}_{s}"):
                        st.session_state.caminho_estudo = (p, s)
                        st.session_state.sim_em_curso = None # Limpa simulado anterior

    with col_conteudo:
        if "caminho_estudo" in st.session_state:
            p, s = st.session_state.caminho_estudo
            dados_materia = st.session_state.db["pastas"][p][s]
            
            t_sim, t_card = st.tabs(["📝 Simulados", "🗂️ Flashcards"])
            
            with t_sim:
                if not dados_materia.get("simulados"):
                    st.info("Nenhum simulado disponível. Gere um no Gerenciamento.")
                else:
                    # Lista de Simulados
                    for i, sim in enumerate(dados_materia["simulados"]):
                        with st.container(border=True):
                            st.write(f"**{sim['id_nome']}** | Banca: {sim['banca']}")
                            if sim["historico"]:
                                for h in sim["historico"]:
                                    st.caption(f"📅 {h['data']} - Aproveitamento: {h['perc']}%")
                            
                            if st.button(f"Resolver {sim['id_nome']}", key=f"exec_{i}"):
                                st.session_state.sim_em_curso = i
                                st.session_state.respostas_temp = {}

                    # Execução do Simulado Interativo
                    if st.session_state.get("sim_em_curso") is not None:
                        st.divider()
                        idx = st.session_state.sim_em_curso
                        atual = dados_materia["simulados"][idx]
                        st.subheader(f"Resolvendo {atual['id_nome']}")
                        
                        # Loop de Questões Real
                        for q in atual["questoes"]:
                            st.markdown(f"<div class='card-pergunta'>{q['p']}</div>", unsafe_allow_html=True)
                            resp = st.radio("Escolha:", q["o"], key=f"pergunta_{q['id']}", index=None)
                            st.session_state.respostas_temp[q['id']] = resp
                        
                        if st.button("Finalizar e Gravar Resultado"):
                            # Lógica de correção
                            total_q = len(atual["questoes"])
                            acertos = 0
                            for q in atual["questoes"]:
                                if st.session_state.respostas_temp.get(q['id']) == q['c']:
                                    acertos += 1
                                    st.session_state.db["indices"]["acertos"] += 1
                                else:
                                    st.session_state.db["indices"]["erros"] += 1
                            
                            percentual = int((acertos / total_q) * 100)
                            
                            # Salva no histórico do simulado
                            st.session_state.db["pastas"][p][s]["simulados"][idx]["historico"].append({
                                "data": datetime.now().strftime("%d/%m/%Y"),
                                "perc": percentual
                            })
                            salvar_db(st.session_state.db)
                            st.success(f"Simulado Concluído! Aproveitamento: {percentual}%")
                            time.sleep(1.5)
                            st.session_state.sim_em_curso = None
                            st.rerun()

            with t_card:
                if not dados_materia.get("cards"):
                    st.info("Sem cards disponíveis.")
                else:
                    for card in dados_materia["cards"]:
                        with st.expander(f"❓ {card['f']}"):
                            st.markdown(f"<div class='flashcard'>{card['v']}</div>", unsafe_allow_html=True)

# --- 7. PÁGINA: ÍNDICES ---
elif menu == "📈 Índices":
    st.title("📈 Performance de Estudos")
    ind = st.session_state.db["indices"]
    total = ind["acertos"] + ind["erros"]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Questões Respondidas", total)
    c2.metric("Acertos Totais", ind["acertos"])
    perc = (ind["acertos"]/total*100) if total > 0 else 0
    c3.metric("Aproveitamento Geral", f"{perc:.1f}%")
    
    st.divider()
    st.subheader("📊 Gráfico de Evolução")
    
    lista_hist = []
    for p, subs in st.session_state.db["pastas"].items():
        for s, d in subs.items():
            if "simulados" in d:
                for sim in d["simulados"]:
                    for h in sim["historico"]:
                        lista_hist.append({"Data": h["data"], "Percentual": h["perc"], "Assunto": s})
    
    if lista_hist:
        df = pd.DataFrame(lista_hist)
        fig = px.line(df, x="Data", y="Percentual", color="Assunto", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ainda não há tentativas registradas para exibir no gráfico.")

elif menu == "📖 Leitura Ativa":
    st.title("📖 Leitura Ativa")
    st.write("Seção destinada aos seus grifos e textos originais.")
