import streamlit as st
import json
import os

# --- 1. CONFIGURAÇÃO E ESTILO (CSS) ---
st.set_page_config(page_title="Plataforma de Leitura", layout="wide")

st.markdown("""
    <style>
    /* Estilo das Pastas (Expanders) */
    .stExpander details summary p {
        font-size: 26px !important;
        font-weight: 800 !important;
        text-align: left !important;
        color: #1E1E1E !important;
    }
    /* Estilo do Bloco de Leitura */
    .caixa-leitura {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        font-size: 22px;
        line-height: 1.8;
        text-align: justify;
        color: #262730;
        margin-top: 20px;
    }
    /* Estilo das Subpastas (Botões) */
    div.stButton > button {
        text-align: left !important;
        font-weight: bold !important;
        font-size: 18px !important;
        height: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar()
if "leitura_atual" not in st.session_state: st.session_state.leitura_atual = None

# --- 3. MENU LATERAL ---
st.sidebar.title("🎮 Painel")
menu = st.sidebar.radio("Ir para:", ["PDF (Leitura)", "Gerenciamento"])

# --- 4. PÁGINA: GERENCIAMENTO ---
if menu == "Gerenciamento":
    st.title("⚙️ Gerenciamento")
    t1, t2, t3 = st.tabs(["📁 Criar Pasta", "📂 Criar Subpasta", "📝 Texto"])
    
    with t1:
        n_p = st.text_input("Nome da Pasta")
        if st.button("Criar"):
            if n_p:
                st.session_state.db[n_p] = {}
                salvar(st.session_state.db); st.success("Feito!"); st.rerun()

    with t2:
        p_s = st.selectbox("Na Pasta:", list(st.session_state.db.keys()))
        n_s = st.text_input("Nome da Subpasta")
        if st.button("Vincular"):
            if n_s:
                # Criamos com campos padrão para evitar erros
                st.session_state.db[p_s][n_s] = {"texto": "", "contagem": 0}
                salvar(st.session_state.db); st.success("Vinculado!"); st.rerun()

    with t3:
        p_c = st.selectbox("Pasta:", list(st.session_state.db.keys()), key="c1")
        s_c = st.selectbox("Subpasta:", list(st.session_state.db.get(p_c, {}).keys()), key="c2")
        txt = st.text_area("Conteúdo:", height=250)
        if st.button("Salvar Texto"):
            st.session_state.db[p_c][s_c]["texto"] = txt
            salvar(st.session_state.db); st.success("Texto Salvo!"); st.rerun()

# --- 5. PÁGINA: PDF (LEITURA) ---
else:
    st.title("📖 Área de Leitura")
    
    # Exibição das Pastas e Subpastas
    for pasta, subpastas in st.session_state.db.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            if not subpastas:
                st.write("Vazio. Adicione subpastas no Gerenciamento.")
            
            for sub, dados in subpastas.items():
                col_btn, col_info = st.columns([4, 1])
                
                # Tratamento de erro: se 'contagem' não existir na pasta antiga, ele usa 0
                qtd = dados.get("contagem", 0)
                
                with col_btn:
                    if st.button(f"📄 {sub}", key=f"btn_{pasta}_{sub}", use_container_width=True):
                        st.session_state.leitura_atual = (pasta, sub)
                        st.rerun()
                with col_info:
                    st.markdown(f"**Lido: {qtd}x**")

    # Área de Leitura (Sempre abre abaixo quando uma subpasta é clicada)
    if st.session_state.leitura_atual:
        p_ativa, s_ativa = st.session_state.leitura_atual
        conteudo_puro = st.session_state.db[p_ativa][s_ativa].get("texto", "")
        
        st.divider()
        st.subheader(f"📍 Lendo: {s_ativa}")
        
        # Mostra o texto ou um aviso se estiver vazio
        if conteudo_puro:
            st.markdown(f'<div class="caixa-leitura">{conteudo_puro.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        else:
            st.warning("Esta subpasta ainda não possui texto. Adicione no Gerenciamento.")

        # Botão de Conclusão
        if st.button("✅ LEITURA CONCLUÍDA!", use_container_width=True):
            # Incrementa a contagem de forma segura
            st.session_state.db[p_ativa][s_ativa]["contagem"] = st.session_state.db[p_ativa][s_ativa].get("contagem", 0) + 1
            salvar(st.session_state.db)
            st.balloons()
            st.rerun()
