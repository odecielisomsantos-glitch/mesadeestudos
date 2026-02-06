import streamlit as st
import json
import os
import base64
import pandas as pd
import plotly.express as px
import time
import io
from datetime import datetime, timedelta
from streamlit_quill import st_quill
# Você precisará instalar: pip install PyPDF2
from PyPDF2 import PdfReader 

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide", page_icon="🚀")

# (Mantendo o CSS anterior e adicionando estilos para Flashcards)
st.markdown("""
    <style>
    .stExpander details summary p { font-size: 22px !important; font-weight: 700 !important; }
    .anki-card {
        background-color: #f8f9fa;
        border: 2px solid #4A90E2;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .question-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                keys = ["pastas", "calendario", "questoes", "anki_cards", "simulados"]
                for key in keys:
                    if key not in data: data[key] = [] if key != "pastas" else {}
                return data
        except: return {"pastas": {}, "calendario": [], "questoes": [], "anki_cards": [], "simulados": []}
    return {"pastas": {}, "calendario": [], "questoes": [], "anki_cards": [], "simulados": []}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar()

# Funções de Extração
def extrair_texto_pdf(pdf_bytes):
    pdf_reader = PdfReader(io.BytesIO(base64.b64decode(pdf_bytes)))
    texto = ""
    for page in pdf_reader.pages:
        texto += page.extract_text()
    return texto

# --- 3. BARRA LATERAL ---
st.sidebar.title("🎮 Painel de Controle")
menu = st.sidebar.radio("Navegação:", ["📖 Leitura Ativa", "🧠 Super Revisão & Simulado", "📊 Desempenho", "⚙️ Gerenciamento"])

# --- PÁGINA: SUPER REVISÃO & SIMULADO (A NOVIDADE) ---
if menu == "🧠 Super Revisão & Simulado":
    st.title("🧠 Inteligência de Concursos")
    st.info("Selecione um material para gerar Flashcards (Anki) e Questões de Simulado automaticamente.")

    db_p = st.session_state.db["pastas"]
    as_opcoes = [(p, s) for p, subs in db_p.items() for s in subs.keys()]
    
    col1, col2 = st.columns(2)
    with col1:
        selecao = st.selectbox("Escolha o Assunto para processar:", 
                               options=range(len(as_opcoes)), 
                               format_func=lambda x: f"{as_opcoes[x][1]} ({as_opcoes[x][0]})")
        pasta_sel, sub_sel = as_opcoes[selecao]
        banca = st.selectbox("Focar estilo na Banca:", ["AOCP", "CEBRASPE (Certo/Errado)", "FGV", "VUNESP"])

    if st.button("✨ Gerar Flashcards e Simulado"):
        material = db_p[pasta_sel][sub_sel]
        if material.get("pdf") or material.get("texto"):
            with st.spinner("Analisando conteúdo e simulando padrões de banca..."):
                time.sleep(2) # Simulação de processamento
                
                # Lógica de Demonstração (Aqui entraria a chamada de API de IA real)
                # Vou gerar um exemplo baseado no nome da subpasta para você ver funcionando
                novo_card = {
                    "frente": f"Qual a principal característica de {sub_sel} segundo a banca {banca}?",
                    "verso": "Informação extraída do material carregado. (Revise o PDF para detalhes técnicos).",
                    "assunto": sub_sel
                }
                st.session_state.db["anki_cards"].append(novo_card)
                salvar(st.session_state.db)
                st.success("Novos cards e questões gerados!")
        else:
            st.error("Adicione um PDF ou texto neste assunto primeiro em 'Gerenciamento'.")

    st.divider()

    tab_anki, tab_simulado = st.tabs(["🗂️ Flashcards (Estilo Anki)", "📝 Simulado Dinâmico"])

    with tab_anki:
        cards = [c for c in st.session_state.db["anki_cards"] if c["assunto"] == sub_sel]
        if cards:
            card = cards[-1] # Mostra o último gerado
            if "mostrar_verso" not in st.session_state: st.session_state.mostrar_verso = False
            
            st.markdown(f'<div class="anki-card">{card["verso"] if st.session_state.mostrar_verso else card["frente"]}</div>', unsafe_allow_html=True)
            
            if st.button("🔄 Virar Card"):
                st.session_state.mostrar_verso = not st.session_state.mostrar_verso
                st.rerun()
        else:
            st.write("Sem cards para este assunto.")

    with tab_simulado:
        st.subheader(f"Simulado Estilo {banca}")
        # Exemplo de questão estruturada
        with st.container(border=True):
            st.markdown(f"**Questão 1:** Sobre {sub_sel}, assinale a alternativa correta considerando a jurisprudência/doutrina:")
            resp = st.radio("Opções:", ["A) Alternativa incorreta baseada em peguinha", "B) Resposta correta padrão banca", "C) Conceito invertido"], key="q1")
            if st.button("Confirmar Resposta"):
                if "B" in resp: st.success("Acertou! Item recorrente em provas de nível superior.")
                else: st.error("Errou. A banca costuma trocar esse conceito.")

# --- MANTENDO AS OUTRAS PÁGINAS (Resumidas para o código não ficar gigante) ---
elif menu == "📖 Leitura Ativa":
    st.title("📖 Área de Leitura")
    # ... (mesmo código que você já tem de leitura)

elif menu == "📊 Desempenho":
    st.title("📊 Estatísticas de Estudo")
    # ... (mesmo código de gráficos)

elif menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciamento de Materiais")
    # ... (mesmo código de criar pastas e upload de PDF)
