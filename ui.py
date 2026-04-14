
import streamlit as st
import pandas as pd

def inject_css():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #07111f 0%, #0f1d35 45%, #132743 100%);
        color: #f5f7fb;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }
    .ld-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }
    .ld-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #d6def0;
        margin-bottom: 8px;
    }
    .ld-text {
        font-size: 0.98rem;
        color: #f7f9ff;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header_cards(result):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Regime", result["regime"])
    with c2:
        st.metric("Viés WIN", result["bias"]["win_label"])
    with c3:
        st.metric("Viés WDO", result["bias"]["wdo_label"])
    with c4:
        st.metric("Confiança", result["confidence"])

def render_summary_box(title, text):
    st.markdown(f"""
        <div class="ld-box">
            <div class="ld-title">{title}</div>
            <div class="ld-text">{text}</div>
        </div>
    """, unsafe_allow_html=True)

def render_section_table(title, rows):
    st.markdown(f"#### {title}")
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_probabilities(probabilities):
    df = pd.DataFrame(
        [{"Cenário": "Continuação de alta", "Probabilidade %": probabilities["continuação_alta"]},
         {"Cenário": "Continuação de baixa", "Probabilidade %": probabilities["continuação_baixa"]},
         {"Cenário": "Lateralização", "Probabilidade %": probabilities["lateralização"]}]
    )
    st.markdown("#### Probabilidades")
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_traps(traps):
    st.markdown("#### Armadilhas prováveis")
    for trap in traps:
        st.warning(trap)
