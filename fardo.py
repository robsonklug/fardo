import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Spinning AI - Bale Management", layout="wide")

st.title("🧶 Sistema Especialista de Mistura Téxtil")
st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("1. Entrada de Dados")
uploaded_file = st.sidebar.file_uploader("Suba sua planilha de fardos (Excel ou CSV)", type=["xlsx", "csv"])

st.sidebar.header("2. Parâmetros do Mix")
quantidade_desejada = st.sidebar.number_input("Qtd de Fardos no Laydown", min_value=1, max_value=200, value=40)
target_mic = st.sidebar.slider("Target Micronaire", 3.0, 5.0, 4.0, step=0.01)

# --- FUNÇÕES ---
def calcular_sci(row):
    # Fórmula corrigida: len convertido para polegadas (div por 25.4)
    # E garantindo que valores não sejam negativos através de pesos técnicos
    sci = (-414.67 + (2.9 * row['str']) + (45.7 * (row['len']/25.4)) + 
            (1.6 * row.get('unif', 80)) - (15.5 * row['mic']))
    return max(0, sci + 300) # Ajuste de base para escala industrial positiva

def selecionar_mix(df, qtd, target):
    df['diff_target'] = df['mic'] - target
    df_sorted = df.sort_values(by='diff_target')
    
    selecionados = []
    metade = qtd // 2
    selecionados.extend(df_sorted.head(metade).to_dict('records'))
    selecionados.extend(df_sorted.tail(qtd - metade).to_dict('records'))
    
    return pd.DataFrame(selecionados)

# --- PROCESSAMENTO ---
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_estoque = pd.read_csv(uploaded_file)
        else:
            df_estoque = pd.read_excel(uploaded_file)

        df_estoque.columns = [c.lower().strip() for c in df_estoque.columns]
        
        colunas_obrigatorias = ['id_fardo', 'mic', 'len', 'str']
        if not all(col in df_estoque.columns for col in colunas_obrigatorias):
            st.error(f"A planilha precisa de: {colunas_obrigatorias}")
        else:
            if st.button("Gerar Laydown Otimizado"):
                mix_final = selecionar_mix(df_estoque, quantidade_desejada, target_mic)
                mix_final['sci'] = mix_final.apply(calcular_sci, axis=1)

                # DASHBOARD
                m1, m2, m3, m4 = st.columns(4)
                avg_mic = mix_final['mic'].mean()
                std_mic = mix_final['mic'].std()
                cv_mic = (std_mic / avg_mic) * 100
                
                m1.metric("Média Micronaire", f"{avg_mic:.3f}", f"{avg_mic - target_mic:.4f}")
                m2.metric("Desvio Padrão (CV%)", f"{cv_mic:.2f}%")
                m3.metric("Resistência Médio", f"{mix_final['str'].mean():.1f} g/tex")
                m4.metric("Índice SCI Médio", f"{mix_final['sci'].mean():.0f}")

                st.subheader("📋 Ordem de Disposição no Pátio (Laydown)")
                
                # CORREÇÃO DO ERRO: substituindo applymap por map
                def color_mic(val):
                    if val < (target_mic - 0.2) or val > (target_mic + 0.2):
                        return 'color: red; font-weight: bold'
                    return 'color: black'

                # Aplicando a formatação corrigida
                st.dataframe(
                    mix_final.style.map(color_mic, subset=['mic']), 
                    use_container_width=True
                )

                csv = mix_final.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar Lista (.CSV)", csv, "laydown.csv", "text/csv")

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
