import streamlit as st
import json
import os
import base64
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO E DADOS ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide")

DB_FILE = "dados_estudos.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if "pastas" not in data: data = {"pastas": {}, "indices": {}}
                return data
        except: return {"pastas": {}, "indices": {}}
    return {"pastas": {}, "indices": {}}

def salvar_dados(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar_dados()

# --- 2. ESTILIZAÇÃO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; }
    .status-card { background-color: #f8f9fa; border-left: 5px solid #633bbc; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    .metric-box { text-align: center; padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL ---
menu = st.sidebar.radio("Navegação:", ["📖 Leitura", "🧠 Revisão & Simulado", "📈 Índices", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO (CÉREBRO) ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciador de Conteúdo")
    t1, t2 = st.tabs(["📂 Estrutura", "🤖 Gerar Cards/Simulados"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            nova_p = st.text_input("Disciplina:")
            if st.button("Criar Disciplina"):
                if nova_p: st.session_state.db["pastas"][nova_p] = {}; salvar_dados(st.session_state.db); st.rerun()
        with c2:
            p_sel = st.selectbox("Pasta Pai:", [""] + list(st.session_state.db["pastas"].keys()))
            nova_s = st.text_input("Assunto:")
            if st.button("Criar Assunto"):
                if p_sel and nova_s:
                    st.session_state.db["pastas"][p_sel][nova_s] = {"cards": [], "simulados": []}
                    salvar_dados(st.session_state.db); st.rerun()

    with t2:
        st.subheader("🤖 Gerador por Texto ou PDF")
        p_at = st.selectbox("Pasta:", [""] + list(st.session_state.db["pastas"].keys()), key="g1")
        s_at = st.selectbox("Subpasta:", list(st.session_state.db["pastas"][p_at].keys()) if p_at else [], key="g2")
        
        fonte = st.radio("Fonte do Conteúdo:", ["Texto/Recorte", "PDF (Se disponível)"])
        input_texto = ""
        if fonte == "Texto/Recorte":
            input_texto = st.text_area("Cole o texto da matéria aqui (ou trechos da lei):", height=200)
        else:
            pdf = st.file_uploader("Upload PDF", type="pdf")
        
        banca = st.selectbox("Banca Base:", ["AOCP", "CEBRASPE", "FGV", "VUNESP"])
        num_q = st.slider("Quantidade de Questões:", 5, 20, 10)
        
        if st.button("✨ Gerar Simulado 01"):
            if s_at and (input_texto or fonte == "PDF (Se disponível)"):
                with st.spinner("IA modelando simulado com base na banca..."):
                    time.sleep(2)
                    novo_simulado = {
                        "id": f"Simulado {len(st.session_state.db['pastas'][p_at][s_at]['simulados']) + 1}",
                        "banca": banca,
                        "data_criacao": str(datetime.now().date()),
                        "questoes": [ # Mock de questões simuladas
                            {"p": f"Considerando a doutrina sobre {s_at}, o item X está correto?", "o": ["Certo", "Errado"], "c": "Certo"}
                        ],
                        "historico": [] # Onde salvaremos as notas
                    }
                    st.session_state.db["pastas"][p_at][s_at]["simulados"].append(novo_simulado)
                    salvar_dados(st.session_state.db)
                    st.success(f"Simulado salvo em {s_at}!")

# --- 5. PÁGINA: REVISÃO & SIMULADO (ESTUDO) ---
elif menu == "🧠 Revisão & Simulado":
    st.title("🧠 Área de Prática")
    db_p = st.session_state.db["pastas"]
    
    col_nav, col_exec = st.columns([1, 2])
    
    with col_nav:
        st.subheader("Módulos")
        for p, subs in db_p.items():
            with st.expander(f"📁 {p}"):
                for s in subs.keys():
                    if st.button(f"📄 {s}", key=f"btn_{p}_{s}"):
                        st.session_state.active_sub = (p, s)

    with col_exec:
        if "active_sub" in st.session_state:
            p, s = st.session_state.active_sub
            content = db_p[p][s]
            st.subheader(f"Assunto: {s}")
            
            for i, sim in enumerate(content["simulados"]):
                with st.container(border=True):
                    st.write(f"📝 **{sim['id']}** ({sim['banca']})")
                    st.caption(f"Criado em: {sim['data_criacao']}")
                    
                    # Mostrar histórico de notas
                    if sim["historico"]:
                        notas = ", ".join([f"{h['nota']}% ({h['data']})" for h in sim["historico"]])
                        st.markdown(f"📊 **Histórico:** {notas}")
                    
                    if st.button(f"Responder {sim['id']}", key=f"run_{p}_{s}_{i}"):
                        st.session_state.current_sim = (p, s, i)
            
            # Execução do Simulado
            if "current_sim" in st.session_state:
                st.divider()
                ps, ss, idx = st.session_state.current_sim
                sim_atual = db_p[ps][ss]["simulados"][idx]
                
                # Interface de questões simplificada para o exemplo
                st.write("---")
                st.write(f"Questão: {sim_atual['questoes'][0]['p']}")
                res = st.radio("Opção:", sim_atual['questoes'][0]['o'], key="input_q")
                
                if st.button("Finalizar e Salvar Tentativa"):
                    # Lógica de cálculo (exemplo 100% ou 0% baseado no mock)
                    nota = 100 if res == sim_atual['questoes'][0]['c'] else 0
                    nova_tentativa = {"data": datetime.now().strftime("%d/%m/%Y"), "nota": nota}
                    
                    # Salva no histórico do simulado específico
                    st.session_state.db["pastas"][ps][ss]["simulados"][idx]["historico"].append(nova_tentativa)
                    
                    # Atualiza índices gerais
                    if nota == 100: st.session_state.db["indices"]["acertos"] += 1
                    else: st.session_state.db["indices"]["erros"] += 1
                    
                    salvar_dados(st.session_state.db)
                    st.success(f"Tentativa registrada: {nota}%!")
                    time.sleep(1)
                    del st.session_state.current_sim
                    st.rerun()

# --- 6. PÁGINA: ÍNDICES ---
elif menu == "📈 Índices":
    st.title("📈 Relatório de Progresso")
    ind = st.session_state.db.get("indices", {"acertos": 0, "erros": 0})
    
    c1, c2, c3 = st.columns(3)
    total = ind["acertos"] + ind["erros"]
    perc = (ind["acertos"]/total*100) if total > 0 else 0
    
    c1.metric("Total de Questões", total)
    c2.metric("Acertos Gerais", ind["acertos"])
    c3.metric("Aproveitamento", f"{perc:.1f}%")
    
    st.divider()
    st.subheader("📉 Evolução por Simulado")
    
    # Busca todos os históricos para montar um gráfico
    todos_dados = []
    for p, subs in st.session_state.db["pastas"].items():
        for s, dados in subs.items():
            for sim in dados["simulados"]:
                for h in sim["historico"]:
                    todos_dados.append({"Assunto": s, "Data": h["data"], "Nota": h["nota"]})
    
    if todos_dados:
        df = pd.DataFrame(todos_dados)
        fig = px.line(df, x="Data", y="Nota", color="Assunto", markers=True, title="Desempenho ao Longo do Tempo")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ainda não há histórico de tentativas para exibir gráficos.")
