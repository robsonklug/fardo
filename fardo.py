# --- BOTÃO DE EXPLICAÇÃO (POPUP / POPOVER) ---
with st.popover("Entenda o Cálculo de Seleção"):
    st.markdown("""
    ### Lógica de Engenharia da Mistura
    O algoritmo opera em três camadas para garantir a fiabilidade do fio:

    **1. Filtragem por Tolerância (Estabilidade):**
    Primeiro, o sistema isola apenas os fardos que estão dentro da janela de aceitação 
    $$(Target - Tolerância) \leq Mic \leq (Target + Tolerância)$$. 
    Isso elimina os *outliers* que elevam o **CV%** e causam o barramento no tingimento.

    **2. Ordenação por Vetor de Diferença:**
    Calculamos a distância de cada fardo em relação ao alvo:  
    $$\Delta = Mic_{fardo} - Mic_{target}$$.  
    Os fardos são então ordenados do mais "fino" para o mais "grosso".

    **3. Equilíbrio de Massa (Sanduíche):**
    O sistema seleciona metade dos fardos no topo da lista (abaixo do alvo) e metade na base (acima do alvo). 
    * Exemplo: Para compensar um fardo de 3.8, o sistema busca um de 4.2. 
    * Resultado: A média aritmética converge para o Target, enquanto a variância permanece controlada pela filtragem inicial.

    **Indicador SCI:**
    O *Spinning Consistency Index* é recalculado para cada mix, ponderando resistência, comprimento e finura, servindo como o selo de aprovação final do PCP.
    """)
