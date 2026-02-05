import streamlit as st
import json
import os

# --- CONFIGURAÇÃO E CSS PARA ESTILIZAÇÃO ---
st.set_page_config(page_title="Plataforma de Leitura", layout="wide")

# CSS para tornar as barras profissionais, texto à esquerda, negrito e maior
st.markdown("""
    <style>
    .stExpander {
        border: 1px solid #d3d3d3 !important;
        border-radius: 5px !important;
        margin-bottom: 10px !important;
    }
    .stExpander p {
        font-size: 22px !important;
        font-weight: bold !important;
        color: #31333F !important;
        text-align: left !important;
    }
    .subpasta-bar {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 5px;
        cursor: pointer;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
    }
    .texto-leitura {
        background-color: white;
        padding: 40px;
        border-radius: 10px;
        line-height: 1.8;
        font-size: 20px;
        text-align: justify;
        border: 1px solid #e6e9ef;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "dados_leitura_v3.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def salvar_dados(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar_dados()

# --- BARRA LATERAL ---
st.sidebar.title("🎮 Painel")
menu = st.sidebar.radio("Ir para:", ["PDF (Leitura)", "Gerenciamento"])

# --- PÁGINA: GERENCIAMENTO ---
if menu == "Gerenciamento":
    st.title("⚙️ Gerenciamento de Conteúdo")
    tab1, tab2, tab3 = st.tabs(["📁 Criar Pasta", "📂 Criar Subpasta", "📝 Adicionar Texto"])
    
    with tab1:
        n_pasta = st.text_input("Nome da Matéria (Pasta Principal)")
        if st.button("Salvar Pasta"):
            if n_pasta:
                st.session_state.db[n_pasta] = {}
                salvar_dados(st.session_state.db)
                st.success(f"✅ Pasta '{n_pasta}' criada!")
                st.rerun()

    with tab2:
        p_sel = st.selectbox("Na Pasta:", list(st.session_state.db.keys()))
        n_sub = st.text_input("Nome do Assunto (Subpasta)")
        if st.button("Salvar Subpasta"):
            if n_sub:
                st.session_state.db[p_sel][n_sub] = {"texto": "", "contagem": 0}
                salvar_dados(st.session_state.db)
                st.success("✅ Subpasta vinculada!")
                st.rerun()

    with tab3:
        p_sel2 = st.selectbox("Pasta:", list(st.session_state.db.keys()), key="tx_p")
        s_sel2 = st.selectbox("Subpasta:", list(st.session_state.db.get(p_sel2, {}).keys()), key="tx_s")
        txt = st.text_area("Texto para Leitura:", height=300)
        if st.button("Atualizar Texto"):
            st.session_state.db[p_sel2][s_sel2]["texto"] = txt
            salvar_dados(st.session_state.db)
            st.success("✅ Material pronto para estudo!")

# --- PÁGINA: PDF (LEITURA) ---
elif menu == "PDF (Leitura)":
    st.title("📖 Área de Leitura")
    
    if not st.session_state.db:
        st.info("Acesse o Gerenciamento para criar suas primeiras pastas.")
    
    for pasta, subpastas in st.session_state.db.items():
        # A "Pasta" agora é um expander estilizado (Texto à esquerda e Negrito via CSS)
        with st.expander(f"📁 {pasta.upper()}"):
            if not subpastas:
                st.write("Nenhum assunto cadastrado.")
            
            for sub, dados in subpastas.items():
                col_sub, col_count = st.columns([4, 1])
                
                with col_sub:
                    # Botão que simula a abertura da subpasta
                    if st.button(f"📄 {sub}", key=f"btn_{pasta}_{sub}", use_container_width=True):
                        st.session_state.visualizando = (pasta, sub)
                
                with col_count:
                    st.markdown(f"**Lido: {dados['contagem']}x**")

    # Área de Exibição do Texto (Abre abaixo de tudo ao selecionar)
    if "visualizando" in st.session_state:
        p, s = st.session_state.visualizando
        st.divider()
        st.subheader(f"📍 Lendo agora: {s}")
        
        texto_exibir = st.session_state.db[p][s]["texto"]
        if texto_exibir:
            st.markdown(f'<div class="texto-leitura">{texto_exibir.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
            
            st.write("")
            if st.button("✅ LEITURA CONCLUÍDA!", use_container_width=True):
                st.session_state.db[p][s]["contagem"] += 1
                salvar_dados(st.session_state.db)
                st.balloons()
                st.success(f"Parabéns! Você completou {st.session_state.db[p][s]['contagem']} leituras deste tópico.")
                st.rerun()
        else:
            st.warning("Texto não encontrado. Adicione o conteúdo no Gerenciamento.")
