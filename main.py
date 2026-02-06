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
try:
    from PyPDF2 import PdfReader
except ImportError:
    st.error("Erro: A biblioteca PyPDF2 não foi instalada. Crie um arquivo 'requirements.txt' no GitHub com 'PyPDF2' escrito dentro.")

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stExpander details summary p { font-size: 20px !important; font-weight: 700 !important; }
    .anki-card {
        background-color: #f8f9fa;
        border: 2px solid #4A90E2;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .folder-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        transition: 0.3s;
    }
    .folder-box:hover { border-color: #4A90E2; background-color: #f0f7ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                # Garante que as chaves novas existam para evitar erros de 'KeyError'
                if "pastas" not in data: data = {"pastas": data}
                for pasta in data["pastas"]:
                    for sub in data["pastas"][pasta]:
                        if "cards" not in data["pastas"][pasta][sub]: data["pastas"][pasta][sub]["cards"] = []
                        if "simulado" not in data["pastas"][pasta][sub]: data["pastas"][pasta][sub]["simulado"] = []
                return data
        except: return {"pastas": {}}
    return {"pastas": {}}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar()

# --- 3. BARRA LATERAL ---
st.sidebar.title("🎮 Painel de Controle")
menu = st.sidebar.radio("Navegação:", ["📖 Leitura Ativa", "🧠 Revisão & Simulado", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: REVISÃO & SIMULADO (A ESTANTE) ---
if menu == "🧠 Revisão & Simulado":
    st.title("🧠 Minha Estante de Estudos")
    db_p = st.session_state.db["pastas"]
    
    if not db_p:
        st.info("Sua estante está vazia. Vá em Gerenciamento para criar pastas e materiais.")
    
    # Lista de Pastas (Estilo plataforma)
    for pasta, subpastas in db_p.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=True):
            cols = st.columns(len(subpastas) if subpastas else 1)
            for i, (sub, dados) in enumerate(subpastas.items()):
                with cols[i % len(cols)]:
                    st.markdown(f"**{sub}**")
                    tipo = st.radio(f"Modo {sub}:", ["Cards", "Simulado"], key=f"mode_{sub}")
                    
                    if st.button(f"Iniciar {tipo}", key=f"btn_{sub}"):
                        st.session_state.estudando = {"pasta": pasta, "sub": sub, "tipo": tipo}

    # Área de Estudo Ativa
    if "estudando" in st.session_state:
        st.divider()
        estudo = st.session_state.estudando
        conteudo = db_p[estudo["pasta"]][estudo["sub"]]
        
        st.subheader(f"✍️ {estudo['tipo']}: {estudo['sub']}")
        
        if estudo["tipo"] == "Cards":
            if not conteudo["cards"]:
                st.warning("Nenhum card gerado para este assunto.")
            else:
                # Lógica simples de navegação de cards
                if "card_idx" not in st.session_state: st.session_state.card_idx = 0
                idx = st.session_state.card_idx % len(conteudo["cards"])
                card = conteudo["cards"][idx]
                
                if "mostrar_verso" not in st.session_state: st.session_state.mostrar_verso = False
                
                st.markdown(f'<div class="anki-card">{card["verso"] if st.session_state.mostrar_verso else card["frente"]}</div>', unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                if c1.button("🔄 Virar"): st.session_state.mostrar_verso = not st.session_state.mostrar_verso; st.rerun()
                if c2.button("➡️ Próximo"): 
                    st.session_state.card_idx += 1
                    st.session_state.mostrar_verso = False
                    st.rerun()
                if c3.button("❌ Sair"): del st.session_state.estudando; st.rerun()

        else: # Simulado
            if not conteudo["simulado"]:
                st.warning("Nenhum simulado disponível.")
            else:
                for item in conteudo["simulado"]:
                    st.info(item["pergunta"])
                    st.radio("Resposta:", item["opcoes"], key=f"sim_{item['pergunta']}")
                if st.button("Finalizar Simulado"):
                    st.balloons(); del st.session_state.estudando; st.rerun()

# --- 5. PÁGINA: GERENCIAMENTO (O CÉREBRO) ---
elif menu == "⚙️ Gerenciamento":
    st.title("⚙️ Centro de Produção")
    t1, t2, t3 = st.tabs(["📁 Estrutura", "📄 Material & IA", "🗑️ Excluir"])
    
    with t1:
        # Mesma lógica anterior de criar pastas e subpastas
        col1, col2 = st.columns(2)
        with col1:
            nova_p = st.text_input("Nova Pasta (Ex: Direito Penal)")
            if st.button("Criar"):
                if nova_p: st.session_state.db["pastas"][nova_p] = {}; salvar(st.session_state.db); st.rerun()
        with col2:
            p_sel = st.selectbox("Pasta Pai:", [""] + list(st.session_state.db["pastas"].keys()))
            nova_s = st.text_input("Nova Subpasta (Ex: Princípios)")
            if st.button("Vincular"):
                if p_sel and nova_s:
                    st.session_state.db["pastas"][p_sel][nova_s] = {"texto": "", "pdf": "", "contagem": 0, "cards": [], "simulado": []}
                    salvar(st.session_state.db); st.rerun()

    with t2:
        st.subheader("🤖 Gerador Inteligente")
        p_at = st.selectbox("Selecione a Pasta:", [""] + list(st.session_state.db["pastas"].keys()), key="gen_p")
        s_at = st.selectbox("Selecione a Subpasta:", list(st.session_state.db["pastas"][p_at].keys()) if p_at else [], key="gen_s")
        
        if s_at:
            pdf_file = st.file_uploader("Upload do PDF da Matéria", type="pdf")
            banca = st.selectbox("Estilo da Banca:", ["AOCP", "CEBRASPE", "FGV"])
            
            if st.button("🚀 Gerar Material de Estudo (IA)"):
                if pdf_file:
                    # Aqui simulamos a extração e criação
                    # Em um sistema real, aqui você processaria o PDF
                    fake_card = {"frente": f"Conceito chave de {s_at} para a {banca}", "verso": "Explicação extraída do material."}
                    fake_sim = {"pergunta": f"Sobre {s_at}, a {banca} afirma que:", "opcoes": ["Certo", "Errado"], "correta": "Certo"}
                    
                    st.session_state.db["pastas"][p_at][s_at]["cards"].append(fake_card)
                    st.session_state.db["pastas"][p_at][s_at]["simulado"].append(fake_sim)
                    
                    # Salva o PDF também
                    st.session_state.db["pastas"][p_at][s_at]["pdf"] = base64.b64encode(pdf_file.read()).decode('utf-8')
                    
                    salvar(st.session_state.db)
                    st.success("Cards e Simulados gerados com sucesso!")
                else:
                    st.error("Faça o upload do PDF primeiro.")

    with t3:
        # Lógica de exclusão para manter o banco limpo
        ex_p = st.selectbox("Excluir Pasta:", [""] + list(st.session_state.db["pastas"].keys()), key="del_p")
        if ex_p and st.button("Confirmar Exclusão Permanente"):
            del st.session_state.db["pastas"][ex_p]
            salvar(st.session_state.db); st.rerun()

# --- MANTENDO LEITURA ATIVA ---
elif menu == "📖 Leitura Ativa":
    st.title("📖 Área de Leitura")
    # ... (seu código original de leitura)
