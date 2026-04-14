import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Spinning AI - Pro Mix", layout="wide")

st.title("🧶 Sistema Especialista de Mistura Téxtil")
st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("1. Entrada de Dados")
uploaded_file = st.sidebar.file_uploader(
    "Suba sua planilha de fardos", 
    type=["xlsx", "csv"],
    help="Selecione o arquivo HVI contendo os dados de laboratório. Colunas obrigatórias: id_fardo, mic, len, str."
)

st.sidebar.header("2. Parâmetros de Qualidade")
target_mic = st.sidebar.slider(
    "Target Micronaire", 3.0, 5.0, 4.0, step=0.01,
    help="O valor médio de Micronaire (finura/maturidade) desejado para o fio final. Crucial para garantir a uniformidade do tingimento."
)

tolerancia = st.sidebar.slider(
    "Tolerância Mic (+/-)", 0.05, 0.50, 0.20,
    help="Define a 'janela' de aceitação. Fardos fora desta faixa em relação ao Target serão descartados para manter o CV% baixo."
)

qtd_desejada = st.sidebar.number_input(
    "Qtd fardos no Laydown", min_value=1, value=40,
    help="Quantidade de fardos que serão dispostos lado a lado para o pegador automático na abertura."
)

# --- LÓGICA DE SELEÇÃO ---
def selecionar_mix_inteligente(df, qtd, target, tol):
    limite_inf = target - tol
    limite_sup = target + tol
    df_filtrado = df[(df['mic'] >= limite_inf) & (df['mic'] <= limite_sup)].copy()
    
    if len(df_filtrado) < qtd:
        return None, len(df_filtrado)

    df_filtrado['diff'] = df_filtrado['mic'] - target
    df_sorted = df_filtrado.sort_values(by='diff')
    
    selecionados = []
    metade = qtd // 2
    selecionados.extend(df_sorted.head(metade).to_dict('records'))
    selecionados.extend(df_sorted.tail(qtd - metade).to_dict('records'))
    
    return pd.DataFrame(selecionados), len(df_filtrado)

# --- PROCESSAMENTO ---
if uploaded_file:
    try:
        df_estoque = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df_estoque.columns = [c.lower().strip() for c in df_estoque.columns]

        if st.button("Gerar Laydown de Alta Estabilidade"):
            mix_final, disponiveis = selecionar_mix_inteligente(df_estoque, qtd_desejada, target_mic, tolerancia)

            if mix_final is None:
                st.error(f"Estoque insuficiente! Apenas {disponiveis} fardos atendem à tolerância.")
            else:
                # DASHBOARD COM HELP TEXTS
                m1, m2, m3, m4 = st.columns(4)
                avg_mic = mix_final['mic'].mean()
                cv_mic = (mix_final['mic'].std() / avg_mic) * 100
                
                m1.metric(
                    "Média Micronaire", f"{avg_mic:.3f}", f"{avg_mic - target_mic:.4f}",
                    help="Média real calculada dos fardos selecionados. Deve estar o mais próximo possível do Target para evitar manchas de tingimento."
                )
                m2.metric(
                    "Desvio Padrão (CV%)", f"{cv_mic:.2f}%",
                    help="Coeficiente de Variação do Micronaire. Valores abaixo de 4% indicam uma mistura homogênea. Acima de 10% indica alto risco de irregularidade no fio."
                )
                m3.metric(
                    "Fardos Aptos", disponiveis,
                    help="Total de fardos no seu estoque que estão dentro da faixa de tolerância definida na barra lateral."
                )
                m4.metric(
                    "Status de Estabilidade", "ESTÁVEL" if cv_mic < 5 else "ALTO RISCO",
                    help="Classificação automática baseada no CV%. Lotes estáveis garantem maior eficiência nas máquinas de fiação (anéis e rotores)."
                )

                st.subheader("📋 Lista de Carregamento")
                st.info("Abaixo estão os fardos selecionados. Dica: Disponha os fardos alternando entre os valores mais altos e mais baixos da lista para uma mistura íntima perfeita.")
                
                st.dataframe(
                    mix_final[['id_fardo', 'mic', 'len', 'str']].style.map(
                        lambda x: 'color: red; font-weight: bold' if abs(x - target_mic) > (tolerancia * 0.8) else '', subset=['mic']
                    ),
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"Erro: {e}")
