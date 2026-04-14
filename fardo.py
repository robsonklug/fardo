import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página para simular o ambiente ERP
st.set_page_config(page_title="TOTVS | Planej.Contr.Produção", layout="wide", initial_sidebar_state="expanded")

# --- CSS PARA REPLICAR O ESTILO DO PRINT (TOTVS STYLE) ---
st.markdown("""
    <style>
    /* Importação de fonte similar ao padrão Windows/TOTVS */
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Topo Azul do ERP - Cor Exata TOTVS */
    header[data-testid="stHeader"] {
        background-color: #005495;
        color: white;
        height: 50px;
    }

    /* Ajuste da Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #f0f4f7; /* Cinza azulado claro */
        border-right: 1px solid #d1dbe5;
    }

    /* Estilização dos Botões da Barra Lateral */
    .stButton > button {
        width: 100%;
        border-radius: 2px;
        text-align: left;
        background-color: transparent;
        color: #005495;
        border: 1px solid transparent;
        font-weight: 500;
    }

    /* Títulos dos Expanders */
    .p-sidebar {
        font-size: 13px;
        color: #005495;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Estilo das Métricas */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #333;
    }
    
    /* Logo no topo da sidebar */
    .logo-text {
        color: #005495;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        border-bottom: 2px solid #005495;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (BARRA LATERAL ESTILO TOTVS) ---
with st.sidebar:
    # Substituindo logo quebrado por texto estilizado (ou caminho local)
    st.markdown('<div class="logo-text">TOTVS</div>', unsafe_allow_html=True)
    
    st.button("📽️ Modo apresentação", use_container_width=True)
    
    # Campo de pesquisa simulado
    st.text_input("🔍 Pesquisar", placeholder="Pesquisar funcionalidades...")

    with st.expander("🖥️ MONITOR PCP", expanded=False):
        st.write("📊 Visão Geral")
        st.write("📈 Linha A")

    with st.expander("📦 MP (Matéria Prima)", expanded=True):
        uploaded_file = st.file_uploader(
            "Importar HVI (.csv, .xlsx)", 
            type=["xlsx", "csv"],
            help="Carregue a planilha de fardos para iniciar o planejamento de mistura."
        )
    
    with st.expander("⚙️ PROCESSO"):
        target_mic = st.slider("Target Micronaire", 3.0, 5.0, 4.07, step=0.01)
        tolerancia = st.slider("Tolerância (+/-)", 0.05, 0.50, 0.15)
        qtd_fardos = st.number_input("Qtd Fardos Laydown", min_value=1, value=40)

    with st.expander("⚖️ GESTÃO DA QUALIDADE"):
        st.write("Verificar Conformidade")
        
    st.markdown("---")
    st.caption("v. 02.9.0010")
    st.caption("👤 Usuário: pcp | 📅 14/04/2026")

# --- ÁREA PRINCIPAL ---
# Simulação da barra de navegação superior do ERP
st.markdown(f"**TOTVS | Planej.Contr.Produção** > Gestão à vista - Fiação")

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        df.columns = [c.lower().strip() for c in df.columns]

        if st.button("Gerar Laydown Otimizado", type="primary"):
            # Lógica de seleção
            limite_inf = target_mic - tolerancia
            limite_sup = target_mic + tolerancia
            df_aptos = df[(df['mic'] >= limite_inf) & (df['mic'] <= limite_sup)].copy()

            if len(df_aptos) < qtd_fardos:
                st.warning(f"Atenção: Apenas {len(df_aptos)} fardos atendem à tolerância definida.")
            else:
                # Ordenação para balanço
                df_aptos['diff'] = df_aptos['mic'] - target_mic
                df_sorted = df_aptos.sort_values('diff')
                mix = pd.concat([df_sorted.head(qtd_fardos//2), df_sorted.tail(qtd_fardos//2 + qtd_fardos%2)])
                
                # Métricas em colunas
                c1, c2, c3, c4 = st.columns(4)
                avg_mic = mix['mic'].mean()
                cv_mic = (mix['mic'].std() / avg_mic) * 100
                
                c1.metric("Média Micronaire", f"{avg_mic:.3f}", f"{avg_mic - target_mic:.4f}", help="Média do mix atual.")
                c2.metric("Desvio Padrão (CV%)", f"{cv_mic:.2f}%", help="Quanto menor, mais homogêneo o fio.")
                c3.metric("Resistência (STR)", f"{mix['str'].mean():.1f}", help="Resistência média em g/tex.")
                c4.metric("Status", "EM CONFORMIDADE" if cv_mic < 5 else "FORA DE PADRÃO")

                st.subheader("📋 Sequenciamento de Carga (Laydown)")
                
                # Tabela estilizada
                st.dataframe(
                    mix[['id_fardo', 'mic', 'len', 'str']].style.map(
                        lambda x: 'background-color: #e6f2ff; font-weight: bold' if abs(x - target_mic) > (tolerancia * 0.7) else '', 
                        subset=['mic']
                    ),
                    use_container_width=True
                )
                
                # Exportação
                st.download_button("📥 Exportar Relatório PCP", mix.to_csv(index=False), "laydown_totvs.csv")

    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
else:
    # Tela de espera similar ao print (vazia)
    st.empty()
    st.markdown("<br><br><br><center><h3>Aguardando entrada de dados para processamento...</h3></center>", unsafe_allow_html=True)
