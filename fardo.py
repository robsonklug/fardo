import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página para simular o ambiente ERP
st.set_page_config(page_title="TOTVS | Planej.Contr.Produção", layout="wide", initial_sidebar_state="expanded")

# --- GERADOR DE ESTOQUE FIXO (500 FARDOS) ---
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

# --- CSS PERSONALIZADO (PADRÃO CORPORATIVO) ---
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

# --- SIDEBAR (CONFIGURAÇÕES PCP) ---
with st.sidebar:
    st.markdown('<div class="logo-text">TOTVS</div>', unsafe_allow_html=True)
    st.button("Modo apresentacao", use_container_width=True)
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

# --- CONTEÚDO PRINCIPAL ---
st.markdown("**TOTVS | Planej.Contr.Produção** > Gestao a vista > Planejamento de Mistura")

# Detalhamento Técnico (Expander)
with st.expander("MEMORIAL DESCRITIVO: LOGICA DE SELECAO TECNICA"):
    st.markdown("""
    O sistema utiliza um algoritmo de **Compensacao de Massa e Filtragem por Variancia**. O processo segue as etapas:

    1. **Pre-Selecao por Grade de Conformidade:** Filtramos apenas fardos cujo Micronaire ($Mic_i$) satisfaz:  
       $$Target - Tol \leq Mic_i \leq Target + Tol$$  
       *Objetivo:* Controlar o Desvio Padrao (CV%) e evitar fibras imaturas ou excessivamente grossas no mesmo lote.

    2. **Calculo do Vetor de Diferenca ($\Delta$):**
       Para cada fardo apto, calculamos a distancia do alvo:  
       $$\Delta_i = Mic_i - Target$$

    3. **Algoritmo de Pareamento Extremo (Sanduiche):**
       Os fardos sao ordenados pelo valor de $\Delta$. Selecionamos $n/2$ fardos com os menores $\Delta$ (valores negativos, abaixo do alvo) e $n/2$ com os maiores $\Delta$ (valores positivos, acima do alvo).  
       *Vantagem:* A media aritmetica final do mix converge para o $Target$ de forma precisa, enquanto a variancia e mantida dentro da zona de seguranca definida pela tolerancia.
    """)

df_estoque = carregar_estoque_fixo()

if st.button("Executar Planejamento Otimizado", type="primary"):
    # Execução da Lógica
    limite_inf = target_mic - tolerancia
    limite_sup = target_mic + tolerancia
    df_aptos = df_estoque[(df_estoque['mic'] >= limite_inf) & (df_estoque['mic'] <= limite_sup)].copy()

    if len(df_aptos) < qtd_fardos:
        st.error(f"Falha no Processamento: Apenas {len(df_aptos)} fardos disponiveis dentro da faixa.")
    else:
        df_aptos['diff'] = df_aptos['mic'] - target_mic
        df_sorted = df_aptos.sort_values('diff')
        mix = pd.concat([df_sorted.head(qtd_fardos//2), df_sorted.tail(qtd_fardos//2 + qtd_fardos%2)])
        
        # Dashboard de Indicadores com Help (Tooltip)
        st.markdown("### Indicadores do Lote Gerado")
        c1, c2, c3, c4 = st.columns(4)
        
        avg_mic = mix['mic'].mean()
        cv_mic = (mix['mic'].std() / avg_mic) * 100
        
        c1.metric(
            "Media Micronaire", 
            f"{avg_mic:.3f}", f"{avg_mic - target_mic:.4f}",
            help="A media final do lote. Deve estar o mais proximo possivel de zero (seta verde) para garantir que o fio nao apresente variacao de tonalidade no tingimento."
        )
        c2.metric(
            "Desvio Padrao (CV%)", 
            f"{cv_mic:.2f}%",
            help="Coeficiente de Variacao. Mede a homogeneidade da mistura. Para fiacao de alta qualidade (Anel), este valor deve estar abaixo de 4%. Valores altos indicam risco de irregularidade de massa."
        )
        c3.metric(
            "Resistencia Media", 
            f"{mix['str'].mean():.1f} g/tex",
            help="Forca de ruptura da fibra. Valores acima de 28 g/tex sao considerados excelentes para evitar quebras nos filatorios e aumentar a eficiencia produtiva."
        )
        c4.metric(
            "Status Qualidade", 
            "CONFORME" if cv_mic < 4.5 else "CRITICO",
            help="Diagnostico automatico do lote. Lotes CRITICOS possuem fardos muito diferentes entre si, mesmo que a media esteja correta."
        )

        st.subheader("Sequenciamento para Disposicao no Patio (Laydown)")
        st.dataframe(
            mix[['id_fardo', 'mic', 'len', 'str', 'unif']].style.map(
                lambda x: 'background-color: #e6f2ff; font-weight: bold' if abs(x - target_mic) > (tolerancia * 0.7) else '', 
                subset=['mic']
            ),
            use_container_width=True
        )
        
        st.download_button("Gerar Relatorio de Carga", mix.to_csv(index=False), "ordem_carga_pcp.csv")
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("Sistema pronto para processamento. Utilize o menu lateral para configurar os parametros e clique em Executar.")
