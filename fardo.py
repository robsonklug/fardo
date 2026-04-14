import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página para visual profissional
st.set_page_config(page_title="TOTVS | Planej.Contr.Produção - Fiação", layout="wide")

# --- CSS CUSTOMIZADO PARA ESTILO ERP ---
st.markdown("""
    <style>
    /* Topo Azul do ERP */
    header[data-testid="stHeader"] {
        background-color: #005495;
        color: white;
    }
    /* Ajuste do Menu Lateral */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6;
        width: 300px !important;
    }
    .main-title {
        color: #005495;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (MENU LATERAL SIMILAR AO PRINT) ---
with st.sidebar:
    st.image("https://logodownload.org/wp-content/uploads/2018/09/totvs-logo.png", width=150) # Logo ilustrativo
    st.markdown("### Planej.Contr.Produção")
    
    st.button("📺 Modo Apresentação", use_container_width=True)
    
    with st.expander("🔍 MONITOR PCP", expanded=True):
        st.write("Linha de Fiação A")
        
    with st.expander("📦 MP (Matéria Prima)"):
        uploaded_file = st.file_uploader(
            "Upload de Fardos (HVI)", 
            type=["xlsx", "csv"],
            help="Suba a planilha de estoque de fardos aqui."
        )
    
    with st.expander("⚙️ PROCESSO"):
        target_mic = st.slider("Target Micronaire", 3.0, 5.0, 4.0, step=0.01, help="Alvo de finura.")
        tolerancia = st.slider("Tolerância (+/-)", 0.05, 0.50, 0.20, help="Janela de aceitação.")
        qtd_desejada = st.number_input("Qtd fardos no Laydown", min_value=1, value=40)

    st.markdown("---")
    st.write("📅 Data: 14/04/2026")
    st.write("👤 Usuário: PCP_TEXTIL")

# --- CONTEÚDO PRINCIPAL (ÁREA DE TRABALHO) ---
st.markdown('<p class="main-title">🧶 Gestão de Mistura e Disposição de Fardos (Laydown)</p>', unsafe_allow_html=True)

if uploaded_file:
    try:
        # Carregamento
        df_estoque = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df_estoque.columns = [c.lower().strip() for c in df_estoque.columns]

        # Botão Estilizado
        if st.button("Gerar Laydown Otimizado", type="primary"):
            
            # Lógica de Seleção
            limite_inf = target_mic - tolerancia
            limite_sup = target_mic + tolerancia
            df_filtrado = df_estoque[(df_estoque['mic'] >= limite_inf) & (df_estoque['mic'] <= limite_sup)].copy()

            if len(df_filtrado) < qtd_desejada:
                st.error(f"🚨 Saldo insuficiente em MP. Apenas {len(df_filtrado)} fardos atendem à conformidade.")
            else:
                # Ordenação para equilíbrio
                df_filtrado['diff'] = df_filtrado['mic'] - target_mic
                df_sorted = df_filtrado.sort_values(by='diff')
                
                mix_final = pd.concat([df_sorted.head(qtd_desejada // 2), df_sorted.tail(qtd_desejada // 2 + qtd_desejada % 2)])
                
                # DASHBOARD DE RESULTADOS
                avg_mic = mix_final['mic'].mean()
                cv_mic = (mix_final['mic'].std() / avg_mic) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Média Mic", f"{avg_mic:.3f}", f"{avg_mic - target_mic:.4f}", help="Média do lote selecionado")
                col2.metric("Desvio (CV%)", f"{cv_mic:.2f}%", help="Coeficiente de variação")
                col3.metric("Fardos Aptos", len(df_filtrado), help="Total de fardos que atendem à tolerância")
                col4.metric("Conformidade", "OK" if cv_mic < 5 else "CRÍTICO")

                # TABELA DE DISPOSIÇÃO
                st.subheader("📋 Ordem de Carregamento")
                st.dataframe(
                    mix_final[['id_fardo', 'mic', 'len', 'str']].style.map(
                        lambda x: 'background-color: #ffcccc' if abs(x - target_mic) > (tolerancia * 0.8) else '', subset=['mic']
                    ),
                    use_container_width=True
                )
                
                # Exportar
                csv = mix_final.to_csv(index=False).encode('utf-8')
                st.download_button("📂 Exportar para Coletor (CSV)", csv, "laydown_totvs.csv", "text/csv")
    except Exception as e:
        st.error(f"Falha na leitura do arquivo: {e}")
else:
    # Tela de Boas-vindas (Vazia como no seu print)
    st.info("Aguardando importação de dados no menu lateral [MP] para iniciar o planejamento.")
    st.image("https://cdn-icons-png.flaticon.com/512/4090/4090458.png", width=100) # Ícone de espera
