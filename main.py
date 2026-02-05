import streamlit as st
import json
import os

# --- CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Mesa de Estudos", layout="wide", page_icon="📖")
DB_FILE = "dados_leitura.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def salvar_dados(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar_dados()
if "leitura_ativa" not in st.session_state: st.session_state.leitura_ativa = None

# --- BARRA LATERAL ---
st.sidebar.title("🎮 Painel de Controle")
opcao = st.sidebar.radio("Ir para:", ["PDF (Leitura)", "Gerenciamento"])

# --- PÁGINA: GERENCIAMENTO ---
if opcao == "Gerenciamento":
    st.title("⚙️ Gerenciamento de Conteúdo")
    
    aba_mat, aba_ass, aba_texto = st.tabs(["📂 Criar Matéria", "📂 Criar Assunto", "📝 Adicionar Texto"])
    
    with aba_mat:
        nova_materia = st.text_input("Nome da Matéria (Ex: Direito Constitucional)")
        if st.button("Salvar Matéria"):
            if nova_materia and nova_materia not in st.session_state.db:
                st.session_state.db[nova_materia] = {}
                salvar_dados(st.session_state.db)
                st.success(f"Matéria '{nova_materia}' criada!")
                st.rerun()

    with aba_ass:
        mat_escolhida = st.selectbox("Selecione a Matéria:", list(st.session_state.db.keys()))
        novo_assunto = st.text_input("Nome do Assunto (Ex: Direitos Fundamentais)")
        if st.button("Vincular Assunto"):
            if novo_assunto:
                st.session_state.db[mat_escolhida][novo_assunto] = {"texto": "", "leituras": 0}
                salvar_dados(st.session_state.db)
                st.success(f"Assunto '{novo_assunto}' vinculado a {mat_escolhida}!")
                st.rerun()

    with aba_texto:
        col_m, col_a = st.columns(2)
        with col_m: m_sel = st.selectbox("Matéria:", list(st.session_state.db.keys()), key="m_text")
        with col_a: a_sel = st.selectbox("Assunto:", list(st.session_state.db.get(m_sel, {}).keys()))
        
        texto_input = st.text_area("Cole aqui o conteúdo do seu PDF para leitura:", height=300)
        if st.button("Salvar/Atualizar Conteúdo"):
            st.session_state.db[m_sel][a_sel]["texto"] = texto_input
            salvar_dados(st.session_state.db)
            st.success("Conteúdo salvo com sucesso! Pronto para leitura.")

# --- PÁGINA: PDF (LEITURA) ---
elif opcao == "PDF (Leitura)":
    st.title("📖 Área de Leitura e Repetição")
    
    if not st.session_state.db:
        st.warning("Nenhuma matéria encontrada. Vá em Gerenciamento para começar.")
    else:
        # Se nenhuma subpasta (assunto) estiver aberta, mostra as Matérias
        if st.session_state.leitura_ativa is None:
            cols = st.columns(3)
            for i, materia in enumerate(st.session_state.db.keys()):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.subheader(f"📂 {materia}")
                        # Mostra os assuntos dentro da pasta
                        for assunto in st.session_state.db[materia].keys():
                            if st.button(f"➡️ {assunto}", key=f"read_{materia}_{assunto}"):
                                st.session_state.leitura_ativa = (materia, assunto)
                                st.rerun()
        else:
            # Interface de Leitura Ativa
            m, a = st.session_state.leitura_ativa
            
            col_voltar, col_info = st.columns([1, 4])
            with col_voltar:
                if st.button("⬅️ Voltar"):
                    st.session_state.leitura_ativa = None
                    st.rerun()
            
            with col_info:
                contagem = st.session_state.db[m][a].get("leituras", 0)
                st.write(f"**Lido {contagem} vezes**")

            st.divider()
            st.header(f"{m} > {a}")
            
            # Área do Texto com Estética Limpa
            with st.container(border=True):
                st.markdown(f'<div style="text-align: justify; line-height: 1.6; font-size: 18px;">{st.session_state.db[m][a]["texto"]}</div>', unsafe_allow_html=True)
            
            st.divider()
            if st.button("✅ CONCLUÍ MAIS UMA LEITURA!", use_container_width=True):
                st.session_state.db[m][a]["leituras"] += 1
                salvar_dados(st.session_state.db)
                st.balloons() # Efeito visual de comemoração
                st.rerun()
