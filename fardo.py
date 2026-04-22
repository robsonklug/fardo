import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="TOTVS | Planej.Contr.Produção", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def carregar_estoque_fixo():
    np.random.seed(42)
    n_fardos = 500
    data = {
        "id_fardo": [f"BALE-{i:03d}" for i in range(1, n_fardos + 1)],
        "mic": np.round(np.random.normal(4.1, 0.35, n_fardos), 2),
        "len": np.round(np.random.normal(28.5, 0.8, n_fardos), 2),
        "str": np.round(np.random.normal(30.0, 1.5, n_fardos), 1),
        "unif": np.round(np.random.normal(82.0, 1.2, n_fardos), 1)
    }
    df = pd.DataFrame(data)
    df['mic'] = df['mic'].clip(3.4, 4.9)
    return df

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Segoe UI', sans-serif; }
    header[data-testid="stHeader"] { background-color: #005495; color: white; height: 50px; }
    section[data-testid="stSidebar"] { background-color: #f0f4f7; border-right: 1px solid #d1dbe5; }
    .logo-text { color: #000000; font-size: 48px; font-weight: 800; margin-bottom: 20px; line-height: 1; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 5px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="logo-text">TOTVS</div>', unsafe_allow_html=True)
    st.button("Modo apresentação", use_container_width=True)
    st.text_input("Pesquisar", placeholder="Pesquisar funcionalidades...")

    with st.expander("MONITOR PCP", expanded=True):
        st.write("Visao Geral do Estoque")
        st.info("Estoque Fixo: 500 fardos carregados.")

    with st.expander("CONFIGURACAO DO MIX", expanded=True):
        target_mic = st.slider("Target Micronaire", 3.0, 5.0, 4.07, step=0.01)
        tolerancia = st.slider("Tolerancia (+/-)", 0.05, 0.50, 0.15)
        qtd_fardos = st.number_input("Qtd Fardos Laydown", min_value=1, value=40)

    st.markdown("---")
    st.caption("v. 02.9.0010 | PCP_SIMULADOR")
    st.caption("Data: 14/04/2026")

st.markdown("**TOTVS | Planej.Contr.Produção** > Gestao a vista > Planejamento de Mistura")

# Botão de popup (Expander para compatibilidade)
with st.expander("Entenda o Calculo de Selecao"):
    st.markdown("""
    O algoritmo opera em tres camadas:
    1. **Filtragem:** Seleciona fardos dentro da tolerancia definida.
    2. **Ordenacao:** Organiza pela diferenca em relacao ao target.
    3. **Equilibrio:** Compensa fardos baixos com fardos altos para cravar a media.
    """)

df_estoque = carregar_estoque_fixo()

if st.button("Executar Planejamento Otimizado", type="primary"):
    limite_inf = target_mic - tolerancia
    limite_sup = target_mic + tolerancia
    df_aptos = df_estoque[(df_estoque['mic'] >= limite_inf) & (df_estoque['mic'] <= limite_sup)].copy()

    if len(df_aptos) < qtd_fardos:
        st.error(f"Falha no Processamento: Apenas {len(df_aptos)} fardos disponiveis.")
    else:
        df_aptos['diff'] = df_aptos['mic'] - target_mic
        df_sorted = df_aptos.sort_values('diff')
        mix = pd.concat([df_sorted.head(qtd_fardos//2), df_sorted.tail(qtd_fardos//2 + qtd_fardos%2)])
        
        c1, c2, c3, c4 = st.columns(4)
        avg_mic = mix['mic'].mean()
        cv_mic = (mix['mic'].std() / avg_mic) * 100
        
        c1.metric("Media Micronaire", f"{avg_mic:.3f}", f"{avg_mic - target_mic:.4f}")
        c2.metric("Desvio Padrao (CV%)", f"{cv_mic:.2f}%")
        c3.metric("Resistencia Media", f"{mix['str'].mean():.1f} g/tex")
        c4.metric("Status Qualidade", "CONFORME" if cv_mic < 4.5 else "CRITICO")

        st.subheader("Sequenciamento para Disposicao no Patio")
        st.dataframe(mix[['id_fardo', 'mic', 'len', 'str', 'unif']], use_container_width=True)
        st.download_button("Gerar Relatorio de Carga", mix.to_csv(index=False), "ordem_carga_pcp.csv")
