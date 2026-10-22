"""
Gera os gráficos a partir de resultados/ (rode antes o benchmark.py).

Cada gráfico sai em duas versões - clara e escura - para o README do GitHub
mostrar a certa conforme o tema de quem visita.
"""

import csv
import json
import os
import statistics
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullLocator  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), "..")
RES = os.path.join(RAIZ, "resultados")
OUT = os.path.join(RAIZ, "graficos")

TEMAS = {
    "claro": dict(fundo="#fcfcfb", tinta="#0b0b0b", tinta2="#52514e", mudo="#898781",
                  grade="#e1e0d9", eixo="#c3c2b7", s1="#2a78d6", s2="#eb6834",
                  ruim="#e34948", neutro="#f0efec", faixa="#2a78d6"),
    "escuro": dict(fundo="#1a1a19", tinta="#f0efec", tinta2="#c3c2b7", mudo="#898781",
                   grade="#2c2c2a", eixo="#383835", s1="#3987e5", s2="#d95926",
                   ruim="#e66767", neutro="#383835", faixa="#3987e5"),
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 200,
})


def carregar():
    with open(os.path.join(RES, "resumo.json")) as f:
        resumo = json.load(f)
    brutos = defaultdict(list)
    with open(os.path.join(RES, "tempos_brutos.csv")) as f:
        for linha in csv.DictReader(f):
            brutos[linha["config"]].append(float(linha["tempo_ms"]))
    return resumo, brutos


def preparar(t, titulo, subtitulo, largura=10, altura=5.4):
    fig, ax = plt.subplots(figsize=(largura, altura))
    fig.patch.set_facecolor(t["fundo"])
    ax.set_facecolor(t["fundo"])
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(t["eixo"])
    ax.tick_params(colors=t["mudo"], length=0, pad=8)
    ax.grid(axis="y", color=t["grade"], linewidth=0.8)
    ax.set_axisbelow(True)
    fig.text(0.06, 0.95, titulo, fontsize=16, fontweight="bold", color=t["tinta"], va="top")
    fig.text(0.06, 0.885, subtitulo, fontsize=10.5, color=t["tinta2"], va="top")
    fig.subplots_adjust(left=0.09, right=0.96, top=0.78, bottom=0.14)
    return fig, ax


def rotulo_eixos(ax, t, x, y):
    ax.set_xlabel(x, color=t["tinta2"], labelpad=10)
    ax.set_ylabel(y, color=t["tinta2"], labelpad=10)


def salvar(fig, nome, tema):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, f"{nome}_{tema}.png"), facecolor=fig.get_facecolor())
    plt.close(fig)


def quartis(v):
    q = statistics.quantiles(v, n=4)
    return q[0], q[2]


# 1) Tempo em função do corte -------------------------------------------------
def grafico_tempo(resumo, brutos, t, tema):
    p = resumo["principal"]
    cortes = [k for k in p if k != "puro"]
    x = list(range(len(cortes)))
    med = [p[c]["mediana_ms"] for c in cortes]
    q1q3 = [quartis(brutos[c]) for c in cortes]
    puro = p["puro"]["mediana_ms"]
    i_best = min(range(len(med)), key=med.__getitem__)

    fig, ax = preparar(
        t, "Tempo do quicksort híbrido em função do corte",
        f"n = 20 000 inteiros aleatórios · mediana de {resumo['parametros']['rodadas']} "
        "rodadas · faixa = intervalo interquartil (25%–75%)")

    ax.fill_between(x, [a for a, _ in q1q3], [b for _, b in q1q3],
                    color=t["faixa"], alpha=0.14, linewidth=0)
    ax.axhline(puro, color=t["mudo"], linestyle=(0, (5, 4)), linewidth=1.4)
    ax.text(4, puro + 0.8, f"quicksort puro · {puro:.1f} ms", color=t["tinta2"],
            va="bottom", ha="center", fontsize=10)
    ax.plot(x, med, color=t["s1"], linewidth=2.2, marker="o", markersize=8,
            markeredgecolor=t["fundo"], markeredgewidth=2, zorder=3)
    ax.plot(x[i_best], med[i_best], marker="o", markersize=15, color=t["s1"],
            markeredgecolor=t["fundo"], markeredgewidth=3, zorder=4)
    ganho = (1 - med[i_best] / puro) * 100
    ax.annotate(f"melhor: corte = {cortes[i_best]}\n{med[i_best]:.1f} ms  (−{ganho:.0f}%)",
                xy=(x[i_best], med[i_best]), xytext=(0, -52), textcoords="offset points",
                ha="center", fontsize=10.5, fontweight="bold", color=t["tinta"],
                arrowprops=dict(arrowstyle="-", color=t["mudo"], lw=1))
    ax.set_xticks(x, cortes)
    ax.set_ylim(min(med) * 0.55, max(med) * 1.12)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))
    rotulo_eixos(ax, t, "corte (tamanho abaixo do qual usa inserção)", "tempo (ms)")
    salvar(fig, "tempo_por_corte", tema)


# 2) Ganho percentual sobre o puro --------------------------------------------
def grafico_ganho(resumo, t, tema):
    p = resumo["principal"]
    cortes = [k for k in p if k != "puro"]
    puro = p["puro"]["mediana_ms"]
    ganho = [(1 - p[c]["mediana_ms"] / puro) * 100 for c in cortes]
    cores = [t["s1"] if g >= 0 else t["ruim"] for g in ganho]

    fig, ax = preparar(t, "Quanto cada corte economiza em relação ao quicksort puro",
                       "redução do tempo mediano · azul = mais rápido · vermelho = mais lento")
    barras = ax.bar(range(len(cortes)), ganho, color=cores, width=0.62, zorder=3)
    ax.axhline(0, color=t["eixo"], linewidth=1.2, zorder=4)
    for b, g in zip(barras, ganho):
        ax.text(b.get_x() + b.get_width() / 2, g + (1.2 if g >= 0 else -1.2),
                f"{g:+.1f}%", ha="center", va="bottom" if g >= 0 else "top",
                fontsize=10, color=t["tinta"], fontweight="bold")
    ax.set_xticks(range(len(cortes)), cortes)
    ax.set_ylim(min(ganho) * 1.25 if min(ganho) < 0 else -5, max(ganho) * 1.3)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+.0f}%"))
    rotulo_eixos(ax, t, "corte", "economia de tempo")
    salvar(fig, "ganho_por_corte", tema)


# 3) Varredura estendida ------------------------------------------------------
def grafico_estendido(resumo, t, tema):
    e = resumo["estendido"]
    cortes = [int(k) for k in e if k != "puro"]
    med = [e[str(c)]["mediana_ms"] for c in cortes]
    puro = e["puro"]["mediana_ms"]

    fig, ax = preparar(t, "O que acontece quando o corte cresce demais",
                       "varredura de 1 a 2 000 · eixo x em escala logarítmica · "
                       f"mediana de {resumo['parametros']['rodadas_estendido']} rodadas")
    melhores = [c for c, m in zip(cortes, med) if m < puro]
    ax.axvspan(min(melhores), max(melhores), color=t["s1"], alpha=0.08, linewidth=0)
    ax.text((min(melhores) * max(melhores)) ** 0.5, max(med) * 0.93,
            "híbrido vence\no puro aqui", ha="center", color=t["tinta2"], fontsize=10)
    ax.axhline(puro, color=t["mudo"], linestyle=(0, (5, 4)), linewidth=1.4)
    ax.text(1, puro + 22, f"quicksort puro · {puro:.0f} ms", color=t["tinta2"],
            va="bottom", fontsize=10)
    ax.plot(cortes, med, color=t["s1"], linewidth=2.2, marker="o", markersize=6,
            markeredgecolor=t["fundo"], markeredgewidth=1.5, zorder=3)
    ax.set_xscale("log")
    ax.xaxis.set_minor_locator(NullLocator())
    ticks = [1, 5, 16, 50, 200, 500, 2000]
    ax.set_xticks(ticks, [str(v) for v in ticks])
    c_fim, m_fim = cortes[-1], med[-1]
    ax.annotate(f"{m_fim / puro:.0f}× mais lento\nque o puro", xy=(c_fim, m_fim),
                xytext=(-14, -4), textcoords="offset points", ha="right", va="top",
                fontsize=10.5, fontweight="bold", color=t["tinta"])
    rotulo_eixos(ax, t, "corte (escala log)", "tempo (ms)")
    salvar(fig, "varredura_estendida", tema)


# 4) Contagem de comparações --------------------------------------------------
def grafico_operacoes(resumo, t, tema):
    ops = resumo["operacoes"]
    cortes = [o["corte"] for o in ops]
    part = [o["comp_particao"] / 1e6 for o in ops]
    ins = [o["comp_insercao"] / 1e6 for o in ops]

    fig, ax = preparar(t, "Por que a curva tem formato de U: o trabalho muda de lugar",
                       "comparações feitas em cada fase (milhões) · n = 20 000 · "
                       "eixo x em escala logarítmica")
    ax.plot(cortes, part, color=t["s1"], linewidth=2.2, label="partição (quicksort)")
    ax.plot(cortes, ins, color=t["s2"], linewidth=2.2, label="inserção")
    ax.text(cortes[-1], part[-1], "  partição", color=t["tinta"], va="center", fontsize=10.5)
    ax.text(cortes[-1], ins[-1], "  inserção", color=t["tinta"], va="center", fontsize=10.5)
    # cruzamento
    for i in range(1, len(cortes)):
        if ins[i - 1] < part[i - 1] and ins[i] >= part[i]:
            ax.axvline(cortes[i], color=t["mudo"], linestyle=(0, (2, 3)), linewidth=1)
            ax.text(cortes[i], max(ins) * 0.55, f"  a partir de ~{cortes[i]}\n  a inserção já faz\n"
                    "  mais comparações\n  que a partição", color=t["tinta2"], fontsize=9.5)
            break
    ax.set_xscale("log")
    ax.xaxis.set_minor_locator(NullLocator())
    ticks = [1, 5, 16, 50, 200, 500, 2000]
    ax.set_xticks(ticks, [str(v) for v in ticks])
    ax.legend(frameon=False, labelcolor=t["tinta2"], loc="upper left")
    ax.set_xlim(right=cortes[-1] * 2.4)
    rotulo_eixos(ax, t, "corte (escala log)", "comparações (milhões)")
    salvar(fig, "operacoes", tema)


def main():
    resumo, brutos = carregar()
    for tema, t in TEMAS.items():
        grafico_tempo(resumo, brutos, t, tema)
        grafico_ganho(resumo, t, tema)
        grafico_estendido(resumo, t, tema)
        grafico_operacoes(resumo, t, tema)
    print("Gráficos salvos em", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
