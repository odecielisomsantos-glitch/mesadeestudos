import streamlit as st
import json
import os
import base64
import pandas as pd
import plotly.express as px
import time
from datetime import datetime, timedelta
from streamlit_quill import st_quill

# --- 1. CONFIGURAÇÃO E ESTILO (CSS) ---
st.set_page_config(page_title="Mesa de Estudos VIP", layout="wide")

st.markdown("""
    <style>
    /* Estilo das Pastas Principais */
    .stExpander details summary p { font-size: 26px !important; font-weight: 800 !important; text-align: left !important; color: #1E1E1E !important; }
    
    /* Estilo do Editor de Leitura */
    .stQuill { background-color: white; border-radius: 15px; border: 1px solid #E0E0E0; }
    .ql-editor { font-size: 20px !important; line-height: 1.8 !important; min-height: 400px; text-align: justify; }

    /* Cronômetro na Sidebar */
    .timer-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #dcdfe3; margin-bottom: 20px; }
    .timer-text { font-family: 'Courier New', monospace; font-size: 28px; font-weight: bold; color: #ff4b4b; }

    /* Cards do Calendário */
    .card-revisao-pendente { background-color: #FFF9C4; border-left: 5px solid #FBC02D; padding: 8px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; font-weight: bold; color: #827717; }
    .card-revisao-concluida { background-color: #C8E6C9; border-left: 5px solid #4CAF50; padding: 8px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; font-weight: bold; color: #1B5E20; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS ---
DB_FILE = "dados_estudos.json"

def carregar():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                if "pastas" not in data: data = {"pastas": data, "calendario": []}
                return data
        except: return {"pastas": {}, "calendario": []}
    return {"pastas": {}, "calendario": []}

def salvar(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

if "db" not in st.session_state: st.session_state.db = carregar()

# --- 3. LÓGICA DO CRONÔMETRO ---
if "segundos" not in st.session_state: st.session_state.segundos = 0
if "timer_rodando" not in st.session_state: st.session_state.timer_rodando = False

def formatar_tempo(s):
    horas, rem = divmod(s, 3600)
    mins, segs = divmod(rem, 60)
    return f"{horas:02d}:{mins:02d}:{segs:02d}"

# --- 4. BARRA LATERAL ---
st.sidebar.title("🎮 Painel de Controle")

# Widget do Cronômetro
st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Tempo de Estudo")
tempo_placeholder = st.sidebar.empty()
col_t1, col_t2 = st.sidebar.columns(2)

if col_t1.button("Play/Pause"):
    st.session_state.timer_rodando = not st.session_state.timer_rodando
if col_t2.button("Zerar"):
    st.session_state.segundos = 0
    st.session_state.timer_rodando = False
    st.rerun()

if st.session_state.timer_rodando:
    tempo_placeholder.markdown(f'<div class="timer-box"><span class="timer-text">{formatar_tempo(st.session_state.segundos)}</span></div>', unsafe_allow_html=True)
    time.sleep(1)
    st.session_state.segundos += 1
    st.rerun()
else:
    tempo_placeholder.markdown(f'<div class="timer-box"><span class="timer-text">{formatar_tempo(st.session_state.segundos)}</span></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação:", ["📖 Leitura Ativa", "📊 Revisão e Quadro", "❓ Questões", "⚙️ Gerenciamento"])

# --- 5. PÁGINA: LEITURA ATIVA ---
if menu == "📖 Leitura Ativa":
    st.title("📖 Área de Leitura e Grifos")
    db_p = st.session_state.db["pastas"]
    
    for pasta, subpastas in db_p.items():
        with st.expander(f"📁 {pasta.upper()}", expanded=False):
            for sub, dados in subpastas.items():
                with st.expander(f"📄 {sub}"):
                    st.write(f"📊 **Leituras:** {dados.get('contagem', 0)}x")
                    
                    # EDITOR COM MEMÓRIA DE GRIFOS
                    conteudo_html = dados.get("texto", "")
                    st.caption("🖍️ Selecione o texto e use o balde de tinta na barra para grifar.")
                    
                    novo_texto = st_quill(
                        value=conteudo_html,
                        toolbar=[[{'background': ['#FFF176', '#A5D6A7', '#F48FB1', 'white']}], ['clean']],
                        key=f"q_{pasta}_{sub}",
                        html=True
                    )
                    
                    if st.button("💾 Salvar Grifos Permanentemente", key=f"s_{sub}"):
                        db_p[pasta][sub]["texto"] = novo_texto
                        salvar(st.session_state.db)
                        st.success("Grifos salvos!")
                        st.rerun()

                    if dados.get("pdf"):
                        st.divider()
                        st.download_button("📥 Baixar PDF Original", base64.b64decode(dados["pdf"]), f"{sub}.pdf", key=f"d_{sub}")
                        st.markdown(f'<iframe src="data:application/pdf;base64,{dados["pdf"]}" width="100%" height="800"></iframe>', unsafe_allow_html=True)

                    if st.button("✅ CONCLUIR LEITURA", key=f"f_{sub}", use_container_width=True):
                        db_p[pasta][sub]["contagem"] = dados.get("contagem", 0) + 1
                        salvar(st.session_state.db); st.balloons(); st.rerun()

# --- 6. PÁGINA: REVISÃO E QUADRO ---
elif menu == "📊 Revisão e Quadro":
    st.title("📊 Centro de Inteligência")
    db_p = st.session_state.db["pastas"]
    
    # Gráfico de Pizza
    rev, pend, s_mat = 0, 0, 0
    for p, subs in db_p.items():
        for s, d in subs.items():
            if not d.get("texto") and not d.get("pdf"): s_mat += 1
            elif d.get("contagem", 0) > 0: rev += 1
            else: pend += 1
    
    fig = px.pie(values=[rev, pend, s_mat], names=['Revisadas', 'Pendentes', 'Sem Material'],
                 color=['Revisadas', 'Pendentes', 'Sem Material'],
                 color_discrete_map={'Revisadas':'#28a745', 'Pendentes':'#ffc107', 'Sem Material':'#dc3545'}, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📅 Quadro Semanal")
    
    # Agendamento
    as_opcoes = [f"{s} | {p}" for p, subs in db_p.items() for s in subs.keys()]
    c_a, c_d = st.columns(2)
    with c_a: ass_sel = st.selectbox("Assunto:", [""] + as_opcoes)
    with c_d: dat_sel = st.date_input("Dia:", datetime.now())
    
    if st.button("📌 Agendar"):
        if ass_sel:
            st.session_state.db["calendario"].append({"assunto": ass_sel, "data": str(dat_sel), "concluido": False})
            salvar(st.session_state.db); st.rerun()

    cols = st.columns(7)
    for i, col in enumerate(cols):
        dia = datetime.now().date() + timedelta(days=i)
        with col:
            st.markdown(f"**{dia.strftime('%d/%m')}**")
            with st.container(border=True):
                tarefas = [t for t in st.session_state.db["calendario"] if t["data"] == str(dia)]
                for idx, t in enumerate(tarefas):
                    cor = "card-revisao-concluida" if t.get("concluido") else "card-revisao-pendente"
                    st.markdown(f'<div class="{cor}">{t["assunto"]}</div>', unsafe_allow_html=True)
                    if not t.get("concluido"):
                        if st.button("✅", key=f"v_{dia}_{idx}"):
                            t["concluido"] = True; salvar(st.session_state.db); st.rerun()

# --- 7. PÁGINA: QUESTÕES ---
elif menu == "❓ Questões":
    st.title("❓ Banco de Questões")
    st.warning("🚀 Seção em construção! Em breve você poderá linkar seus simulados aqui.")

# --- 8. PÁGINA: GERENCIAMENTO ---
else:
    st.title("⚙️ Gerenciamento")
    t1, t2, t3, t4 = st.tabs(["📁 Pastas", "📂 Subpastas", "📝 Material", "✏️ Editar/Excluir"])
    db_p = st.session_state.db["pastas"]
    
    with t1:
        n_p = st.text_input("Nova Pasta")
        if st.button("Criar"):
            if n_p: db_p[n_p] = {}; salvar(st.session_state.db); st.rerun()
    with t2:
        p_s = st.selectbox("Pasta Pai:", [""] + list(db_p.keys()))
        n_s = st.text_input("Subpasta")
        if st.button("Vincular"):
            if p_s and n_s:
                db_p[p_s][n_s] = {"texto": "", "pdf": "", "contagem": 0}
                salvar(st.session_state.db); st.rerun()
    with t3:
        p_c = st.selectbox("Pasta:", [""] + list(db_p.keys()), key="p1")
        s_c = st.selectbox("Subpasta:", list(db_p[p_c].keys()) if p_c else [], key="p2")
        if s_c:
            txt = st.text_area("Texto:", height=200, value=db_p[p_c][s_c].get("texto", ""))
            pdf = st.file_uploader("PDF", type="pdf")
            if st.button("Salvar"):
                db_p[p_c][s_c]["texto"] = txt
                if pdf: db_p[p_c][s_c]["pdf"] = base64.b64encode(pdf.read()).decode('utf-8')
                salvar(st.session_state.db); st.success("Salvo!"); st.rerun()
    with t4:
        ed_p = st.selectbox("Excluir Pasta:", [""] + list(db_p.keys()))
        if ed_p and st.button("🗑️ Deletar"):
            del db_p[ed_p]; salvar(st.session_state.db); st.rerun()
