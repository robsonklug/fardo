import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(page_title="Spinning AI - Bale Management", layout="wide")

st.title("🧶 Sistema Especialista de Mistura Téxtil")
st.markdown("---")

# --- SIDEBAR: CONFIGURAÇÕES E UPLOAD ---
st.sidebar.header("1. Entrada de Dados")
uploaded_file = st.sidebar.file_uploader("Suba sua planilha de fardos (Excel ou CSV)", type=["xlsx", "csv"])

st.sidebar.header("2. Parâmetros do Mix")
quantidade_desejada = st.sidebar.number_input("Qtd de Fardos no Laydown", min_value=1, max_value=200, value=40)
target_mic = st.sidebar.slider("Target Micronaire", 3.0, 5.0, 4.0, step=0.01)

# --- FUNÇÕES DE APOIO ---
def calcular_sci(row):
    """Cálculo simplificado do Spinning Consistency Index"""
    return (-414.67 + (2.9 * row['str']) + (45.7 * (row['len']/25.4)) + 
            (1.6 * row.get('unif', 80)) - (15.5 * row['mic']))

def selecionar_mix(df, qtd, target):
    # Lógica de seleção por pareamento (Equilíbrio de massa)
    df['diff_target'] = df['mic'] - target
    df_sorted = df.sort_values(by='diff_target')
    
    selecionados = []
    metade = qtd // 2
    # Puxa os extremos para equilibrar a média no centro
    selecionados.extend(df_sorted.head(metade).to_dict('records'))
    selecionados.extend(df_sorted.tail(qtd - metade).to_dict('records'))
    
    return pd.DataFrame(selecionados)

# --- PROCESSAMENTO PRINCIPAL ---
if uploaded_file is not None:
    try:
        # Carregamento flexível
        if uploaded_file.name.endswith('.csv'):
            df_estoque = pd.read_csv(uploaded_file)
        else:
            df_estoque = pd.read_excel(uploaded_file)

        # Padronização de nomes de colunas para evitar erros
        df_estoque.columns = [c.lower().strip() for c in df_estoque.columns]
        
        # Verificação de colunas obrigatórias
        colunas_obrigatorias = ['id_fardo', 'mic', 'len', 'str']
        if not all(col in df_estoque.columns for col in colunas_obrigatorias):
            st.error(f"Erro: A planilha deve conter as colunas: {colunas_obrigatorias}")
        else:
            st.success(f"Estoque carregado: {len(df_estoque)} fardos encontrados.")

            if st.button("Gerar Laydown Otimizado"):
                mix_final = selecionar_mix(df_estoque, quantidade_desejada, target_mic)
                
                # Adiciona cálculo de SCI para análise de qualidade
                mix_final['sci'] = mix_final.apply(calcular_sci, axis=1)

                # --- DASHBOARD DE MÉTRICAS ---
                m1, m2, m3, m4 = st.columns(4)
                avg_mic = mix_final['mic'].mean()
                std_mic = mix_final['mic'].std()
                
                m1.metric("Média Micronaire", f"{avg_mic:.3f}", f"{avg_mic - target_mic:.4f}")
                m2.metric("Desvio Padrão (CV%)", f"{(std_mic/avg_mic)*100:.2f}%")
                m3.metric("Resistência Média", f"{mix_final['str'].mean():.1f} g/tex")
                m4.metric("Índice SCI Médio", f"{mix_final['sci'].mean():.0f}")

                # --- EXIBIÇÃO E DOWNLOAD ---
                st.subheader("📋 Ordem de Disposição no Pátio (Laydown)")
                
                # Colorir células para facilitar visualização de fardos críticos
                def color_mic(val):
                    color = 'red' if val < (target_mic - 0.2) or val > (target_mic + 0.2) else 'black'
                    return f'color: {color}'

                st.dataframe(mix_final.style.applymap(color_mic, subset=['mic']), use_container_width=True)

                # Exportar Resultado
                csv = mix_final.to_csv(index=False).encode('utf-8')
                st.download_button("Baixar Lista de Carregamento (.CSV)", csv, "laydown_gerado.csv", "text/csv")

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
else:
    st.info("👆 Por favor, faça o upload da sua planilha de estoque na barra lateral para começar.")
    st.markdown("""
    ### Formato esperado da planilha:
    | id_fardo | mic | len | str |
    | :--- | :--- | :--- | :--- |
    | F-001 | 3.8 | 28.5 | 30.2 |
    """)