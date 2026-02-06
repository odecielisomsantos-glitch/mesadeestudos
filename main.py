import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO E TRATAMENTO DE ERROS GLOBAL ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide")

# Função para exibir alertas bonitos em português
def mostrar_alerta(mensagem, tipo="erro"):
    if tipo == "erro":
        st.error(f"⚠️ **Ops! Algo deu errado:** {mensagem}")
    elif tipo == "aviso":
        st.warning(f"💡 **Atenção:** {mensagem}")
    else:
        st.success(f"✅ {mensagem}")

# --- 2. GESTÃO DE DADOS COM VALIDAÇÃO ---
DB_FILE = "dados_estudos.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                # Garantir que as estruturas base existam
                if "pastas" not in data: data["pastas"] = {}
                if "indices" not in data: data["indices"] = {"acertos": 0, "erros": 0}
                return data
        except Exception as e:
            mostrar_alerta(f"Não consegui ler seus dados salvos. {str(e)}")
            return {"pastas": {}, "indices": {"acertos": 0, "erros": 0}}
    return {"pastas": {}, "indices": {"acertos": 0, "erros": 0}}

def salvar_dados(dados):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(dados, f, indent=4)
    except Exception as e:
        mostrar_alerta(f"Falha ao salvar as informações. {str(e)}")

if "db" not in st.session_state:
    st.session_state.db = carregar_dados()

# --- 3. BARRA LATERAL ---
st.sidebar.title("🎮 Painel de Controle")
menu = st.sidebar.radio("Navegação:", ["📖 Leitura", "🧠 Revisão & Simulado", "📈 Índices", "⚙️ Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO (CORRIGIDA) ---
if menu == "⚙️ Gerenciamento":
    st.title("⚙️ Gerenciador de Conteúdo")
    t1, t2 = st.tabs(["📂 Estrutura", "🤖 Gerar Cards/Simulados"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            nova_p = st.text_input("Nome da Disciplina (Pasta):")
            if st.button("Criar Disciplina"):
                if nova_p:
                    st.session_state.db["pastas"][nova_p] = {}
                    salvar_dados(st.session_state.db)
                    st.toast(f"Disciplina {nova_p} criada!")
                    st.rerun()
        with c2:
            p_sel = st.selectbox("Selecione a Pasta Pai:", [""] + list(st.session_state.db["pastas"].keys()))
            nova_s = st.text_input("Nome do Assunto (Subpasta):")
            if st.button("Criar Assunto"):
                if p_sel and nova_s:
                    # Inicializa a subpasta com as listas necessárias para evitar o KeyError
                    st.session_state.db["pastas"][p_sel][nova_s] = {"cards": [], "simulados": []}
                    salvar_dados(st.session_state.db)
                    st.toast(f"Assunto {nova_s} vinculado!")
                    st.rerun()

    with t2:
        st.subheader("🤖 Gerador por Texto ou PDF")
        p_at = st.selectbox("Selecione a Pasta:", [""] + list(st.session_state.db["pastas"].keys()), key="gen_p")
        
        # Só tenta carregar subpastas se uma pasta estiver selecionada
        sub_options = list(st.session_state.db["pastas"][p_at].keys()) if p_at else []
        s_at = st.selectbox("Selecione a Subpasta:", sub_options, key="gen_s")
        
        if not s_at:
            mostrar_alerta("Por favor, selecione ou crie uma subpasta antes de gerar simulados.", "aviso")
        else:
            input_texto = st.text_area("Cole o texto da matéria ou lei aqui:", height=200)
            banca = st.selectbox("Banca Base:", ["AOCP", "CEBRASPE", "FGV", "VUNESP"])
            
            if st.button("✨ Gerar Simulado"):
                if input_texto:
                    try:
                        # BLINDAGEM: Verifica se a chave 'simulados' existe na subpasta selecionada
                        if "simulados" not in st.session_state.db["pastas"][p_at][s_at]:
                            st.session_state.db["pastas"][p_at][s_at]["simulados"] = []
                        
                        num_atual = len(st.session_state.db["pastas"][p_at][s_at]["simulados"]) + 1
                        
                        novo_sim = {
                            "id": f"Simulado {num_atual:02d}",
                            "banca": banca,
                            "data_criacao": datetime.now().strftime("%d/%m/%Y"),
                            "questoes": [
                                {"p": f"(Banca {banca}) Baseado no texto, o item X está correto?", "o": ["Certo", "Errado"], "c": "Certo"}
                            ],
                            "historico": []
                        }
                        
                        st.session_state.db["pastas"][p_at][s_at]["simulados"].append(novo_sim)
                        salvar_dados(st.session_state.db)
                        mostrar_alerta(f"Simulado gerado e salvo em {s_at}!", "sucesso")
                    except Exception as e:
                        mostrar_alerta(f"Erro ao processar simulado: {str(e)}")
                else:
                    mostrar_alerta("O campo de texto não pode estar vazio.", "aviso")

# --- 5. PÁGINA: REVISÃO & SIMULADO (HISTÓRICO) ---
elif menu == "🧠 Revisão & Simulado":
    st.title("🧠 Área de Estudo")
    db_p = st.session_state.db["pastas"]
    
    if not db_p:
        mostrar_alerta("Nenhuma pasta encontrada. Comece pelo 'Gerenciamento'.", "aviso")
    else:
        # Coluna de Módulos (Estilo Moodle/Cursos)
        col_nav, col_exec = st.columns([1, 2.5])
        
        with col_nav:
            for p, subs in db_p.items():
                with st.expander(f"📁 {p}"):
                    for s in subs.keys():
                        if st.button(f"📄 {s}", key=f"nav_{p}_{s}"):
                            st.session_state.active_study = (p, s)

        with col_exec:
            if "active_study" in st.session_state:
                p, s = st.session_state.active_study
                
                # Garantir integridade dos dados ao acessar
                sub_dados = db_p[p][s]
                if "simulados" not in sub_dados: sub_dados["simulados"] = []
                
                st.subheader(f"Módulo: {s}")
                
                if not sub_dados["simulados"]:
                    st.info("Ainda não há simulados para este assunto.")
                else:
                    for idx, sim in enumerate(sub_dados["simulados"]):
                        with st.container(border=True):
                            st.write(f"📝 **{sim['id']}** | Banca: {sim['banca']}")
                            
                            # Exibição do Histórico de Desempenho
                            if sim.get("historico"):
                                st.write("**Histórico de Evolução:**")
                                for h in sim["historico"]:
                                    st.caption(f"📅 {h['data']} - Aproveitamento: **{h['nota']}%**")
                            
                            if st.button(f"Refazer {sim['id']}", key=f"btn_{p}_{s}_{idx}"):
                                # Aqui entraria a lógica de resposta (mock por enquanto)
                                nota_fake = 80 # Exemplo
                                nova_tentativa = {
                                    "data": datetime.now().strftime("%d/%m/%Y"),
                                    "nota": nota_fake
                                }
                                sim["historico"].append(nova_tentativa)
                                salvar_dados(st.session_state.db)
                                st.success(f"Tentativa salva! Você acertou {nota_fake}%")
                                st.rerun()

# --- Outras páginas seguem a mesma lógica de tratamento ---
elif menu == "📈 Índices":
    st.title("📈 Meus Índices")
    # Gráficos e métricas (já protegidos pela função carregar_dados)
    st.write("Seu progresso será listado aqui automaticamente.")
