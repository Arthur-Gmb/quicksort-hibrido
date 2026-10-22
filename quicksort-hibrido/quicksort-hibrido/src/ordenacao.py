"""
Algoritmos de ordenação: inserção, quicksort puro e quicksort híbrido.

O quicksort usa pivô aleatório e particionamento em três listas
(menores, iguais e maiores que o pivô). A versão híbrida troca para a
ordenação por inserção quando o pedaço tem menos que `corte` elementos.
"""

import random


def insercao(v: list) -> list:
    """Ordenação por inserção. Ordena uma cópia e devolve a lista ordenada.

    O(n²) no pior caso, mas com constante muito baixa: em listas pequenas
    é mais rápida que o quicksort, que paga o custo de criar listas e
    fazer chamadas recursivas.
    """
    a = list(v)
    for i in range(1, len(a)):
        chave = a[i]
        j = i - 1
        while j >= 0 and a[j] > chave:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = chave
    return a


def quicksort_puro(v: list) -> list:
    """Quicksort com pivô aleatório e partição em menores/iguais/maiores."""
    if len(v) <= 1:
        return list(v)
    pivo = random.choice(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return quicksort_puro(menores) + iguais + quicksort_puro(maiores)


def quicksort_hibrido(v: list, corte: int) -> list:
    """Quicksort que chama a inserção quando o pedaço tem menos que `corte` elementos.

    Com corte = 1 a condição `len(v) < 1` só vale para a lista vazia,
    então a inserção nunca ordena nada de verdade e o algoritmo se
    comporta exatamente como o quicksort puro.
    """
    if len(v) < corte:
        return insercao(v)
    if len(v) <= 1:
        return list(v)
    pivo = random.choice(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return quicksort_hibrido(menores, corte) + iguais + quicksort_hibrido(maiores, corte)
