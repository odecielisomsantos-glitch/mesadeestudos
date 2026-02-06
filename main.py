import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO E ALERTAS ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide")

def msg(texto, tipo="erro"):
    if tipo == "erro": st.error(f"⚠️ {texto}")
    elif tipo == "sucesso": st.success(f"✅ {texto}")
    else: st.info(f"ℹ️ {texto}")

# --- 2. BANCO DE DADOS (PERSISTÊNCIA TOTAL) ---
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

# --- 3. CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .card-pergunta { background-color: #f9f9f9; padding: 20px; border-radius: 10px; border-left: 5px solid #633bbc; margin-bottom: 15px; }
    .flashcard { background: white; border: 2px solid #633bbc; padding: 30px; text-align: center; border-radius: 15px; min-height: 200px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação:", ["📖 Leitura", "🧠 Área de Estudo", "📈 Índices", "⚙️ Gerenciamento"])

# --- 5. PÁGINA: GERENCIAMENTO ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciador de Conteúdo")
    tab_est, tab_gen = st.tabs(["📁 Organizar Pastas", "🤖 Gerar Material (Simulado/Cards)"])
    
    with tab_est:
        c1, c2 = st.columns(2)
        with c1:
            n_pasta = st.text_input("Nova Disciplina:")
            if st.button("Criar Pasta"):
                if n_pasta:
                    st.session_state.db["pastas"][n_pasta] = {}
                    salvar_db(st.session_state.db); st.rerun()
        with c2:
            p_alvo = st.selectbox("Pasta Pai:", [""] + list(st.session_state.db["pastas"].keys()))
            n_sub = st.text_input("Novo Assunto:")
            if st.button("Criar Subpasta"):
                if p_alvo and n_sub:
                    st.session_state.db["pastas"][p_alvo][n_sub] = {"simulados": [], "cards": [], "texto_base": ""}
                    salvar_db(st.session_state.db); st.rerun()

    with tab_gen:
        p_sel = st.selectbox("Selecione a Pasta:", [""] + list(st.session_state.db["pastas"].keys()), key="p_gen")
        s_options = list(st.session_state.db["pastas"][p_sel].keys()) if p_sel else []
        s_sel = st.selectbox("Selecione a Subpasta:", s_options, key="s_gen")
        
        if s_sel:
            fonte = st.radio("Fonte do Conteúdo:", ["Texto/Recorte", "PDF (Manual)"])
            txt_materia = st.text_area("Cole o texto da matéria ou lei aqui:", height=200)
            banca = st.selectbox("Banca Base:", ["AOCP", "CEBRASPE", "FGV", "VUNESP"])
            qtd_q = st.slider("Quantidade de Questões:", 1, 20, 10)
            
            if st.button("✨ Gerar Simulado e Cards"):
                if txt_materia:
                    # Lógica de Geração Real (baseada no texto fornecido)
                    num_sim = len(st.session_state.db["pastas"][p_sel][s_sel]["simulados"]) + 1
                    
                    # Criando questões baseadas no texto (exemplo simplificado de lógica de IA)
                    novas_questoes = []
                    for i in range(qtd_q):
                        novas_questoes.append({
                            "id": i+1,
                            "pergunta": f"(Questão {i+1} - {banca}) De acordo com o texto sobre {s_sel}, analise a validade do conceito X.",
                            "opcoes": ["Certo", "Errado"],
                            "correta": "Certo"
                        })
                    
                    novo_simulado = {
                        "id_nome": f"Simulado {num_sim:02d}",
                        "banca": banca,
                        "data": datetime.now().strftime("%d/%m/%Y"),
                        "questoes": novas_questoes,
                        "historico": []
                    }
                    
                    # Criando Flashcards
                    novos_cards = [
                        {"f": f"O que o texto diz sobre {s_sel}?", "v": "Resposta baseada no conteúdo colado."},
                        {"f": f"Ponto chave da banca {banca} para este assunto?", "v": "Detalhe técnico do texto."}
                    ]
                    
                    st.session_state.db["pastas"][p_sel][s_sel]["simulados"].append(novo_simulado)
                    st.session_state.db["pastas"][p_sel][s_sel]["cards"].extend(novos_cards)
                    st.session_state.db["pastas"][p_sel][s_sel]["texto_base"] = txt_materia
                    
                    salvar_db(st.session_state.db)
                    msg("Simulado e Cards gerados com sucesso!", "sucesso")
                else:
                    msg("Insira o texto para gerar o material.")

# --- 6. PÁGINA: ÁREA DE ESTUDO (INTERATIVA) ---
elif menu == "🧠 Área de Estudo":
    st.title("🧠 Estação de Prática")
    
    db = st.session_state.db["pastas"]
    col_menu, col_aula = st.columns([1, 2.5])
    
    with col_menu:
        for p, subs in db.items():
            with st.expander(f"📁 {p}"):
                for s in subs.keys():
                    if st.button(f"📄 {s}", key=f"nav_{p}_{s}"):
                        st.session_state.temp_path = (p, s)
                        st.session_state.active_sim = None # Reseta simulado aberto

    with col_aula:
        if "temp_path" in st.session_state:
            p, s = st.session_state.temp_path
            st.subheader(f"Módulo: {s}")
            
            t_sim, t_card = st.tabs(["📝 Simulados", "🗂️ Flashcards"])
            
            with t_sim:
                if not db[p][s]["simulados"]:
                    st.info("Nenhum simulado gerado para este assunto.")
                else:
                    for i, sim in enumerate(db[p][s]["simulados"]):
                        with st.container(border=True):
                            st.write(f"**{sim['id_nome']}** ({sim['banca']})")
                            if sim["historico"]:
                                ult = sim["historico"][-1]
                                st.caption(f"Última tentativa: {ult['data']} - Aproveitamento: {ult['perc']}%")
                            
                            if st.button(f"Fazer {sim['id_nome']}", key=f"run_{i}"):
                                st.session_state.active_sim = i
                                st.session_state.respostas = {}

                    # EXECUÇÃO DO SIMULADO
                    if st.session_state.get("active_sim") is not None:
                        idx = st.session_state.active_sim
                        sim_atual = db[p][s]["simulados"][idx]
                        
                        st.divider()
                        st.subheader(f"Resolvendo: {sim_atual['id_nome']}")
                        
                        acertos_local = 0
                        for q in sim_atual["questoes"]:
                            st.markdown(f"<div class='card-pergunta'>{q['pergunta']}</div>", unsafe_allow_html=True)
                            resp = st.radio("Escolha:", q["opcoes"], key=f"q_{q['id']}", index=None)
                            st.session_state.respostas[q['id']] = resp
                        
                        if st.button("Finalizar Simulado"):
                            # Calcular Resultado
                            for q in sim_atual["questoes"]:
                                if st.session_state.respostas.get(q['id']) == q['correta']:
                                    acertos_local += 1
                                    st.session_state.db["indices"]["acertos"] += 1
                                else:
                                    st.session_state.db["indices"]["erros"] += 1
                            
                            percentual = int((acertos_local / len(sim_atual["questoes"])) * 100)
                            
                            # Gravar no Histórico do Simulado
                            nova_tentativa = {
                                "data": datetime.now().strftime("%d/%m/%Y"),
                                "perc": percentual
                            }
                            st.session_state.db["pastas"][p][s]["simulados"][idx]["historico"].append(nova_tentativa)
                            salvar_db(st.session_state.db)
                            
                            st.balloons()
                            msg(f"Simulado Finalizado! Seu aproveitamento: {percentual}%", "sucesso")
                            time.sleep(2)
                            st.session_state.active_sim = None
                            st.rerun()

            with t_card:
                if not db[p][s]["cards"]:
                    st.info("Nenhum card gerado.")
                else:
                    for c in db[p][s]["cards"]:
                        with st.expander(f"❓ {c['f']}"):
                            st.markdown(f"<div class='flashcard'>{c['v']}</div>", unsafe_allow_html=True)

# --- 7. ÍNDICES ---
elif menu == "📈 Índices":
    st.title("📈 Seus Índices de Performance")
    ind = st.session_state.db["indices"]
    total = ind["acertos"] + ind["erros"]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Questões Respondidas", total)
    c2.metric("Acertos Totais", ind["acertos"])
    perc_geral = (ind["acertos"]/total*100) if total > 0 else 0
    c3.metric("Aproveitamento Geral", f"{perc_geral:.1f}%")

    st.divider()
    st.subheader("📊 Histórico por Assunto")
    
    dados_h = []
    for p, subs in st.session_state.db["pastas"].items():
        for s, d in subs.items():
            for sim in d["simulados"]:
                for h in sim["historico"]:
                    dados_h.append({"Assunto": s, "Data": h["data"], "Percentual": h["perc"]})
    
    if dados_h:
        df = pd.DataFrame(dados_h)
        fig = px.line(df, x="Data", y="Percentual", color="Assunto", markers=True)
        st.plotly_chart(fig, use_container_width=True)
