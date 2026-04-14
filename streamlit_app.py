
import streamlit as st
import pandas as pd
from datetime import datetime

from parser import parse_market_text
from core.engine import analyze_market
from core.database import init_db, save_analysis, load_recent
from core.ui import inject_css, render_header_cards, render_section_table, render_summary_box, render_traps, render_probabilities

st.set_page_config(
    page_title="LD Trading PRO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_db()

st.title("LD Trading PRO")
st.caption("Leitura macro, viés operacional, probabilidades, armadilhas e mudança de regime para WIN e WDO.")

with st.sidebar:
    st.markdown("### Modo de uso")
    st.write("1. Cole o texto bruto do painel.")
    st.write("2. Clique em **Analisar mercado**.")
    st.write("3. Leia o regime, o viés, as probabilidades e o plano operacional.")
    st.write("4. Faça uma nova leitura nos horários-chave do dia para detectar viradas.")
    st.markdown("---")
    st.markdown("### Horários úteis")
    st.write("08:50–09:10 · Pré-mercado")
    st.write("09:30–09:45 · Abertura")
    st.write("10:00–10:30 · Confirmação")
    st.write("14:30–15:00 · Releitura EUA")

default_text = ""
raw_text = st.text_area("Cole aqui os dados do mercado", value=default_text, height=360, placeholder="Cole o texto bruto do painel aqui...")

analyze = st.button("Analisar mercado", use_container_width=True, type="primary")

if analyze and raw_text.strip():
    parsed = parse_market_text(raw_text)
    result = analyze_market(parsed)

    save_analysis(
        timestamp=result["meta"]["timestamp"],
        regime=result["regime"],
        bias_win=result["bias"]["win_label"],
        bias_wdo=result["bias"]["wdo_label"],
        confidence=result["confidence"],
        raw_text=raw_text,
        summary=result["executive_summary"],
    )

    render_header_cards(result)

    col_a, col_b = st.columns([1.35, 1], gap="large")
    with col_a:
        render_summary_box("Leitura macro", result["macro_summary"])
        render_summary_box("Plano operacional", result["operational_plan"])
        render_traps(result["traps"])
    with col_b:
        render_probabilities(result["probabilities"])
        render_summary_box("Invalidação do cenário", result["invalidation"])
        render_summary_box("Resumo executivo", result["executive_summary"])

    st.markdown("### Mapa dos dados lidos")
    sec1, sec2 = st.columns(2, gap="large")
    with sec1:
        render_section_table("Estados Unidos e risco", parsed["tables"]["macro_us"])
        render_section_table("Brasil e correlação", parsed["tables"]["brazil"])
    with sec2:
        render_section_table("Europa e Ásia", parsed["tables"]["world"])
        render_section_table("Commodities e moedas", parsed["tables"]["commod_fx"])

    st.markdown("### Diagnóstico interno")
    diag = pd.DataFrame(
        [
            {"Métrica": "Score WIN", "Valor": result["scores"]["win_score"]},
            {"Métrica": "Score WDO", "Valor": result["scores"]["wdo_score"]},
            {"Métrica": "Score Macro", "Valor": result["scores"]["macro_score"]},
            {"Métrica": "Força da virada", "Valor": result["scores"]["turn_strength"]},
            {"Métrica": "Regime", "Valor": result["regime"]},
            {"Métrica": "Confiança", "Valor": result["confidence"]},
        ]
    )
    st.dataframe(diag, use_container_width=True, hide_index=True)

st.markdown("### Histórico recente")
recent = load_recent(limit=8)
if recent:
    hist = pd.DataFrame(recent, columns=["Horário", "Regime", "Viés WIN", "Viés WDO", "Confiança", "Resumo"])
    st.dataframe(hist, use_container_width=True, hide_index=True)
else:
    st.info("Ainda não há leituras salvas nesta instalação.")
