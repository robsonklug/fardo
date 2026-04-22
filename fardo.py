import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página - Identidade Corporativa
st.set_page_config(page_title="TOTVS | Planej.Contr.Produção", layout="wide", initial_sidebar_state="expanded")

# --- GERADOR DE DADOS FIXOS (Simulação de Estoque Real) ---
@st.cache_data
def carregar_estoque_fixo():
    np.random.seed(42)
    n_fardos = 500
    data = {
        "id_fardo": [f"BALE-{i:03d}" for i in range(1, n_fardos + 1)],
        "mic": np.round(np.random.normal(4.1, 0.35, n_fardos), 2), # Micronaire
        "len": np.round(np.random.normal(28.5, 0.8, n_fardos), 2), # Comprimento mm
        "str": np.round(np.random.normal(30.0, 1.5, n_fardos), 1), # Resistência
        "unif": np.round(np.random.normal(82.0, 1.2, n_fardos), 1) # Uniformidade
    }
    df = pd.DataFrame(data)
    # Limites técnicos para evitar valores irreais
    df['mic'] = df['mic'].clip(3.4, 4.9)
    return df

# --- CSS PARA ESTILO ERP TOTVS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap');
    html, body, [class*="css"]  { font-family: 'Segoe UI', sans-serif; }
    header[data-testid="stHeader"] { background-color: #005495; color: white; height: 50px; }
    section[data-testid="stSidebar"] { background-color: #f0f4f7; border-right: 1px solid #d1dbe5; }
    .logo-text { color: #005495; font-size: 24px; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #005495; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 5px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (MENU FIXO) ---
with st.sidebar:
    st.markdown('<div class="logo-text">TOTVS</div>', unsafe_allow_html=True)
    
    st.button("📽️ Modo apresentação", use_container_width=True)
    st.text_input("🔍 Pesquisar", placeholder="Pesquisar funcionalidades...")

    with st.expander("🖥️ MONITOR PCP", expanded=True):
        st.write("📊 Visão Geral do Estoque")
        st.info(f"Estoque Fixo: 500 fardos carregados.")

    with st.expander("⚙️ CONFIGURAÇÃO DO MIX", expanded=True):
        target_mic = st.slider("Target Micronaire", 3.0, 5.0, 4.07, step=0.01, help="Alvo de finura para o lote.")
        tolerancia = st.slider("Tolerância (+/-)", 0.05, 0.50, 0.15, help="Janela de aceitação para controle de CV%.")
        qtd_fardos = st.number_input("Qtd Fardos Laydown", min_value=1, value=40)

    with st.expander("⚖️ GESTÃO DA QUALIDADE"):
        st.caption("Normas Internas NBR")
        
    st.markdown("---")
    st.caption("v. 02.9.0010 | PCP_SIMULADOR")
    st.caption("📅 Data: 14/04/2026")

# --- CONTEÚDO PRINCIPAL ---
st.markdown(f"**TOTVS | Planej.Contr.Produção** > Gestão à vista > Planejamento de Mistura")

# Carrega os dados fixos do fonte
df_estoque = carregar_estoque_fixo()

# Área de comando
if st.button("Executar Planejamento Otimizado", type="primary"):
    
    # Lógica de Filtro e Seleção
    limite_inf = target_mic - tolerancia
    limite_sup = target_mic + tolerancia
    df_aptos = df_estoque[(df_estoque['mic'] >= limite_inf) & (df_estoque['mic'] <= limite_sup)].copy()

    if len(df_aptos) < qtd_fardos:
        st.error(f"❌ Falha no Processamento: Apenas {len(df_aptos)} fardos disponíveis dentro da tolerância de +/- {tolerancia}.")
    else:
        # Algoritmo de equilíbrio de massa (Extremos controlados)
        df_aptos['diff'] = df_aptos['mic'] - target_mic
        df_sorted = df_aptos.sort_values('diff')
        
        # Seleciona os pares para zerar a diferença em relação ao target
        mix = pd.concat([df_sorted.head(qtd_fardos//2), df_sorted.tail(qtd_fardos//2 + qtd_fardos%2)])
        
        # Dashboard de Resultados (Métricas TOTVS)
        st.markdown("### 📈 Indicadores do Lote Gerado")
        c1, c2, c3, c4 = st.columns(4)
        
        avg_mic = mix['mic'].mean()
        cv_mic = (mix['mic'].std() / avg_mic) * 100
        
        c1.metric("Média Micronaire", f"{avg_mic:.3f}", f"{avg_mic - target_mic:.4f}", help="Média calculada do mix.")
        c2.metric("Desvio Padrão (CV%)", f"{cv_mic:.2f}%", help="Uniformidade da mistura.")
        c3.metric("Resistência Média", f"{mix['str'].mean():.1f} g/tex", help="Força mecânica da fibra.")
        c4.metric("Status Qualidade", "CONFORME" if cv_mic < 4.5 else "CRÍTICO")

        # Tabela de Sequenciamento
        st.subheader("📋 Sequenciamento para Disposição no Pátio")
        st.markdown("*Os fardos destacados representam os limites da sua tolerância.*")
        
        st.dataframe(
            mix[['id_fardo', 'mic', 'len', 'str', 'unif']].style.map(
                lambda x: 'background-color: #e6f2ff; color: #005495; font-weight: bold' if abs(x - target_mic) > (tolerancia * 0.7) else '', 
                subset=['mic']
            ),
            use_container_width=True
        )
        
        # Botão de Exportação Final
        st.download_button("📥 Gerar Relatório de Carga", mix.to_csv(index=False), "ordem_carga_pcp.csv")
else:
    # Estado inicial do sistema
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1,2,1])
    with col_b:
        st.info("Sistema pronto para processamento. Utilize o menu lateral para configurar os parâmetros e clique em 'Executar Planejamento'.")
        st.write("---")
        st.markdown("**Resumo do Estoque Atual:**")
        st.write(f"- Total de fardos em pátio: {len(df_estoque)}")
        st.write(f"- Range de Micronaire: {df_estoque['mic'].min()} a {df_estoque['mic'].max()}")
