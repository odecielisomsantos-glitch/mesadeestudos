import streamlit as st
import json
import os
import base64
import pandas as pd
import plotly.express as px
import time
import io
from datetime import datetime
from streamlit_quill import st_quill

# Tentativa de importação segura
try:
    from PyPDF2 import PdfReader
except ImportError:
    pass

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide", page_icon="📚")

# --- ESTILIZAÇÃO CSS (Inspirado na imagem de módulos) ---
st.markdown("""
    <style>
    /* Estilo do Menu de Módulos (Sidebar-like dentro da página) */
    .module-item {
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 5px;
        background-color: #f0f2f6;
        cursor: pointer;
        display: flex;
        align-items: center;
        transition: 0.3s;
    }
    .module-item:hover { background-color: #e0e4ea; }
    .module-active { background-color: #633bbc !important; color: white !important; }
    .lock-icon { margin-left: auto; font-size: 14px; opacity: 0.6; }
    
    /* Cards de Estudo */
    .anki-card {
        background-color: white;
        border: 2px solid #633bbc;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        min-height: 250px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Meta Progress Bar */
    .stProgress > div > div > div > div { background-color: #633bbc; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if "indices" not in data: 
                    data["indices"] = {"acertos": 0, "erros": 0, "revisoes": 0, "cards_feitos": 0, "meta_percent": 80}
                return data
        except: return {"pastas": {}, "indices": {}}
    return {"pastas": {}, "indices": {"acertos": 0, "erros": 0, "revisoes": 0, "cards_feitos": 0, "meta_percent": 80}}

def salvar_dados(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar_dados()

# --- BARRA LATERAL ---
st.sidebar.title("🎮 Painel de Controle")
menu = st.sidebar.radio("Navegação:", ["📖 Leitura Ativa", "🧠 Revisão & Simulado", "📈 Índices", "⚙️ Gerenciamento"])

# --- PÁGINA: REVISÃO & SIMULADO (ESTRUTURA DE MÓDULOS) ---
if menu == "🧠 Revisão & Simulado":
    st.title("🧠 Meus Módulos de Estudo")
    db_p = st.session_state.db["pastas"]
    
    if not db_p:
        st.info("Crie pastas e subpastas no Gerenciamento para começar.")
    else:
        col_menu, col_conteudo = st.columns([1, 2.5])
        
        with col_menu:
            st.subheader("📁 Disciplinas")
            for pasta in db_p.keys():
                with st.expander(f"▼ {pasta.upper()}", expanded=True):
                    for sub in db_p[pasta].keys():
                        # Botão que simula o item da imagem enviada
                        if st.button(f"📄 {sub}", key=f"nav_{pasta}_{sub}", use_container_width=True):
                            st.session_state.current_sub = (pasta, sub)
                            st.session_state.modo_estudo = None

        with col_conteudo:
            if "current_sub" in st.session_state:
                p, s = st.session_state.current_sub
                st.subheader(f"Módulo: {s}")
                
                c1, c2 = st.columns(2)
                if c1.button("📝 Iniciar Simulado", use_container_width=True): st.session_state.modo_estudo = "Simulado"
                if c2.button("🗂️ Revisar Cards", use_container_width=True): st.session_state.modo_estudo = "Cards"
                
                st.divider()
                
                modo = st.session_state.get("modo_estudo")
                material = db_p[p][s]
                
                if modo == "Cards":
                    if not material["cards"]: st.warning("Sem cards gerados. Vá em Gerenciamento.")
                    else:
                        card = material["cards"][0] # Exemplo simplificado
                        st.markdown(f'<div class="anki-card">{card["frente"]}</div>', unsafe_allow_html=True)
                        if st.button("Revelar Resposta"):
                            st.info(card["verso"])
                            st.session_state.db["indices"]["cards_feitos"] += 1
                            salvar_dados(st.session_state.db)

                elif modo == "Simulado":
                    if not material["simulado"]: st.warning("Sem simulado gerado.")
                    else:
                        for idx, q in enumerate(material["simulado"]):
                            st.markdown(f"**Questão {idx+1}:** {q['pergunta']}")
                            resp = st.radio("Sua resposta:", q['opcoes'], key=f"q_{idx}")
                            if st.button("Confirmar", key=f"btn_{idx}"):
                                if resp == q['correta']:
                                    st.success("Acertou!")
                                    st.session_state.db["indices"]["acertos"] += 1
                                else:
                                    st.error("Errou!")
                                    st.session_state.db["indices"]["erros"] += 1
                                salvar_dados(st.session_state.db)
            else:
                st.info("Selecione um assunto no menu ao lado para estudar.")

# --- PÁGINA: ÍNDICES (DASHBOARD) ---
elif menu == "📈 Índices":
    st.title("📈 Meus Índices de Performance")
    ind = st.session_state.db["indices"]
    
    # Metas
    col_meta1, col_meta2 = st.columns([2, 1])
    with col_meta1:
        st.subheader("🎯 Gerenciamento de Meta")
        meta = st.slider("Defina sua meta de acerto (%)", 0, 100, ind["meta_percent"])
        ind["meta_percent"] = meta
        
        total_q = ind["acertos"] + ind["erros"]
        perc_atual = (ind["acertos"] / total_q * 100) if total_q > 0 else 0
        
        st.write(f"Desempenho Atual: **{perc_atual:.1f}%**")
        st.progress(perc_atual / 100)
    
    with col_meta2:
        if perc_atual >= meta: st.success("Meta Atingida! 🔥")
        else: st.warning(f"Faltam {(meta - perc_atual):.1f}% para a meta.")

    st.divider()
    
    # Cards de Métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Questões Feitas", total_q)
    c2.metric("Acertos", ind["acertos"], delta=f"{perc_atual:.1f}%")
    c3.metric("Erros", ind["erros"], delta=f"-{100-perc_atual:.1f}%", delta_color="inverse")
    c4.metric("Cards Revisados", ind["cards_feitos"])
    
    # Gráfico de Evolução (Exemplo)
    st.subheader("📊 Histórico de Acertos")
    dados_grafico = pd.DataFrame({
        "Categoria": ["Acertos", "Erros"],
        "Quantidade": [ind["acertos"], ind["erros"]]
    })
    fig = px.pie(dados_grafico, values='Quantidade', names='Categoria', color_discrete_map={'Acertos':'#28a745', 'Erros':'#dc3545'})
    st.plotly_chart(fig)

# --- PÁGINA: GERENCIAMENTO ---
elif menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciador de Conteúdo")
    
    t1, t2 = st.tabs(["📂 Estrutura de Pastas", "🤖 Upload & Geração IA"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            nova_p = st.text_input("Nome da Disciplina (Pasta)")
            if st.button("Criar Disciplina"):
                if nova_p: 
                    st.session_state.db["pastas"][nova_p] = {}
                    salvar_dados(st.session_state.db); st.rerun()
        with c2:
            p_sel = st.selectbox("Selecione a Disciplina:", [""] + list(st.session_state.db["pastas"].keys()))
            nova_s = st.text_input("Nome do Assunto (Subpasta)")
            if st.button("Criar Assunto"):
                if p_sel and nova_s:
                    st.session_state.db["pastas"][p_sel][nova_s] = {"cards": [], "simulado": [], "pdf": ""}
                    salvar_dados(st.session_state.db); st.rerun()

    with t2:
        st.write("Selecione onde o PDF será processado:")
        p_up = st.selectbox("Pasta:", [""] + list(st.session_state.db["pastas"].keys()), key="p_up")
        s_up = st.selectbox("Subpasta:", list(st.session_state.db["pastas"][p_up].keys()) if p_up else [], key="s_up")
        
        pdf = st.file_uploader("Arraste o PDF da matéria aqui", type="pdf")
        if st.button("✨ Gerar Cards e Simulado") and s_up and pdf:
            with st.spinner("IA processando PDF para cards e questões..."):
                # SIMULAÇÃO DE GERAÇÃO (Aqui você integraria a lógica de leitura real)
                time.sleep(2)
                
                # Mock de Questões (Simulando banca CEBRASPE/AOCP)
                q_gerada = {
                    "pergunta": f"De acordo com o PDF de {s_up}, o item X é indispensável?",
                    "opcoes": ["Certo", "Errado"],
                    "correta": "Certo"
                }
                card_gerado = {
                    "frente": f"O que o material diz sobre {s_up}?",
                    "verso": "Diz que o conceito Y deve ser aplicado sempre."
                }
                
                st.session_state.db["pastas"][p_up][s_up]["simulado"].append(q_gerada)
                st.session_state.db["pastas"][p_up][s_up]["cards"].append(card_gerado)
                salvar_dados(st.session_state.db)
                st.success("Conteúdo integrado com sucesso!")

elif menu == "📖 Leitura Ativa":
    st.title("📖 Área de Leitura")
    st.info("Aqui você acessa os textos e grifos originais.")
