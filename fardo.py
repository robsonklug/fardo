# --- SUBSTITUTO PARA VERSÕES ANTIGAS ---
with st.expander("Entenda o Cálculo de Seleção"):
    st.markdown("""
    ### Lógica de Engenharia da Mistura
    O algoritmo opera em três camadas para garantir a fiabilidade do fio:

    **1. Filtragem por Tolerância (Estabilidade):**
    Primeiro, o sistema isola apenas os fardos que estão dentro da janela de aceitação 
    $$(Target - Tolerância) \leq Mic \leq (Target + Tolerância)$$. 
    Isso elimina os *outliers* que elevam o **CV%**.

    **2. Ordenação por Vetor de Diferença:**
    Calculamos a distância de cada fardo em relação ao alvo:  
    $$\Delta = Mic_{fardo} - Mic_{target}$$.

    **3. Equilíbrio de Massa (Sanduíche):**
    O sistema seleciona metade dos fardos no topo da lista (abaixo do alvo) e metade na base (acima do alvo).
    """)
