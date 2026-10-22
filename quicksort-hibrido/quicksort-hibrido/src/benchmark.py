"""
Mede o tempo do quicksort híbrido para vários cortes e compara com o puro.

Uso:
    python src/benchmark.py              # experimento principal (20 mil elementos)
    python src/benchmark.py --rapido     # versão curta, para testar o script

Metodologia
-----------
* Cada rodada gera UMA lista de 20 000 inteiros aleatórios e a MESMA lista é
  usada por todas as configurações (puro + 9 cortes). Assim nenhuma
  configuração tem "sorte" com a entrada.
* A ordem das configurações é embaralhada a cada rodada, para que efeitos de
  aquecimento de cache/CPU não favoreçam sempre a mesma.
* O coletor de lixo (gc) fica desligado durante a medição.
* O valor reportado é a MEDIANA das rodadas (robusta a picos do sistema);
  também guardamos mínimo, média e desvio-padrão.
"""

import argparse
import csv
import gc
import json
import os
import platform
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.setrecursionlimit(10_000)

import ordenacao  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), "..")
CORTES = [1, 5, 10, 16, 20, 32, 50, 100, 200]
CORTES_ESTENDIDOS = [1, 2, 3, 5, 8, 10, 12, 16, 20, 24, 32, 40, 50, 64, 80,
                     100, 128, 160, 200, 300, 500, 800, 1000, 1500, 2000]


def cronometrar(funcao, dados) -> float:
    gc.disable()
    try:
        inicio = time.perf_counter()
        resultado = funcao(dados)
        fim = time.perf_counter()
    finally:
        gc.enable()
    assert resultado == sorted(dados), "ordenação incorreta!"
    return fim - inicio


def experimento(n, cortes, rodadas, semente, incluir_puro=True):
    configs = []
    if incluir_puro:
        configs.append(("puro", ordenacao.quicksort_puro))
    for c in cortes:
        configs.append((c, lambda v, c=c: ordenacao.quicksort_hibrido(v, c)))

    tempos = {nome: [] for nome, _ in configs}
    rng = random.Random(semente)
    for r in range(rodadas):
        dados = [rng.randint(0, 10**9) for _ in range(n)]
        ordem = configs[:]
        rng.shuffle(ordem)
        for nome, f in ordem:
            random.seed(semente * 1000 + r)  # mesmos pivôs para todos
            tempos[nome].append(cronometrar(f, dados))
        print(f"  rodada {r + 1:>2}/{rodadas} ok", file=sys.stderr)
    return tempos


# ---------------------------------------------------------------------------
# Contagem de operações (fora da medição de tempo) - ajuda a EXPLICAR a curva
# ---------------------------------------------------------------------------
def contar_operacoes(v, corte, cont):
    """Reproduz o híbrido contando chamadas e comparações."""
    cont["chamadas"] += 1
    if len(v) < corte:
        cont["chamadas_insercao"] += 1
        a = list(v)
        for i in range(1, len(a)):
            chave, j = a[i], i - 1
            while j >= 0:
                cont["comp_insercao"] += 1
                if a[j] > chave:
                    a[j + 1] = a[j]
                    j -= 1
                else:
                    break
            a[j + 1] = chave
        return a
    if len(v) <= 1:
        return list(v)
    pivo = random.choice(v)
    cont["comp_particao"] += 3 * len(v)  # três compreensões de lista
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return (contar_operacoes(menores, corte, cont) + iguais
            + contar_operacoes(maiores, corte, cont))


def operacoes_por_corte(n, cortes, semente):
    rng = random.Random(semente)
    dados = [rng.randint(0, 10**9) for _ in range(n)]
    linhas = []
    for c in cortes:
        random.seed(semente)
        cont = dict(chamadas=0, chamadas_insercao=0, comp_particao=0, comp_insercao=0)
        assert contar_operacoes(dados, c, cont) == sorted(dados)
        linhas.append({"corte": c, **cont})
    return linhas


def resumo(amostras):
    return {
        "mediana_ms": statistics.median(amostras) * 1000,
        "media_ms": statistics.mean(amostras) * 1000,
        "min_ms": min(amostras) * 1000,
        "desvio_ms": statistics.stdev(amostras) * 1000 if len(amostras) > 1 else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20_000)
    ap.add_argument("--rodadas", type=int, default=21)
    ap.add_argument("--rodadas-estendido", type=int, default=9)
    ap.add_argument("--semente", type=int, default=2026)
    ap.add_argument("--rapido", action="store_true")
    a = ap.parse_args()
    if a.rapido:
        a.n, a.rodadas, a.rodadas_estendido = 2_000, 3, 2

    saida = os.path.join(RAIZ, "resultados")
    os.makedirs(saida, exist_ok=True)

    print(f"Experimento principal: n={a.n}, {a.rodadas} rodadas", file=sys.stderr)
    t = experimento(a.n, CORTES, a.rodadas, a.semente)

    print("Varredura estendida de cortes", file=sys.stderr)
    te = experimento(a.n, CORTES_ESTENDIDOS, a.rodadas_estendido, a.semente + 1,
                     incluir_puro=True)

    print("Contando operações", file=sys.stderr)
    ops = operacoes_por_corte(a.n, CORTES_ESTENDIDOS, a.semente)

    principal = {str(k): resumo(v) for k, v in t.items()}
    estendido = {str(k): resumo(v) for k, v in te.items()}

    with open(os.path.join(saida, "tempos_brutos.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["config", "rodada", "tempo_ms"])
        for k, v in t.items():
            for i, x in enumerate(v):
                w.writerow([k, i + 1, f"{x * 1000:.4f}"])

    with open(os.path.join(saida, "operacoes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ops[0].keys()))
        w.writeheader()
        w.writerows(ops)

    with open(os.path.join(saida, "resumo.json"), "w") as f:
        json.dump({
            "ambiente": {
                "python": platform.python_version(),
                "implementacao": platform.python_implementation(),
                "sistema": platform.platform(),
                "processador": platform.processor() or platform.machine(),
            },
            "parametros": vars(a),
            "principal": principal,
            "estendido": estendido,
            "operacoes": ops,
        }, f, indent=2, ensure_ascii=False)

    puro = principal["puro"]["mediana_ms"]
    print(f"\n{'config':>8} | {'mediana (ms)':>12} | {'vs puro':>8}")
    for k, s in principal.items():
        print(f"{k:>8} | {s['mediana_ms']:12.2f} | {(puro / s['mediana_ms'] - 1) * 100:+7.1f}%")


if __name__ == "__main__":
    main()
