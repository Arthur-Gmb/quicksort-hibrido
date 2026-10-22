<div align="center">

# ⚡ Quicksort Híbrido

**Quicksort para os pedaços grandes, inserção para os pequenos — e onde fica o ponto de troca.**

👥 Arthur Gabriel Monteiro Barreiras · Cauã Evaristo da Cruz

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Testes](https://github.com/Arthur-Gmb/quicksort-hibrido/actions/workflows/testes.yml/badge.svg)
![Melhor corte](https://img.shields.io/badge/melhor%20corte-16-2a78d6)
![Ganho](https://img.shields.io/badge/ganho%20sobre%20o%20puro-−20,7%25%20de%20tempo-0ca30c)

[Relatório completo](RELATORIO.md) · [Código](src/ordenacao.py) · [Benchmark](src/benchmark.py) · [Dados brutos](resultados/)

</div>

---

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="graficos/tempo_por_corte_escuro.png">
  <img src="graficos/tempo_por_corte_claro.png" alt="Tempo do quicksort híbrido em função do corte: mínimo de 35 ms no corte 16, contra 44,2 ms do quicksort puro.">
</picture>

## 🎯 Resultado em 30 segundos

| | |
|---|---|
| 🏆 **Melhor corte** | **16** → 35,0 ms |
| 🐢 Quicksort puro | 44,2 ms |
| 📉 **Ganho** | **20,7 % menos tempo (1,26× mais rápido)** |
| ✅ Faixa boa | qualquer corte entre **10 e 50** ganha do puro |
| 💥 Corte grande demais | corte 200 já é 58 % mais lento; corte 2 000 é **12× mais lento** |
| 🟰 Corte = 1 | idêntico ao puro: mesmas 26 569 chamadas, **0** comparações de inserção |

*20 000 inteiros aleatórios · mediana de 21 rodadas · CPython 3.13*

## 🧠 A ideia

O quicksort é O(n log n), mas cada chamada tem um custo fixo alto (sortear pivô, criar três listas, duas chamadas recursivas, concatenar). A inserção é O(n²), mas quase não tem custo fixo. Para pedaços pequenos, a inserção ganha — e é por isso que bibliotecas reais (`std::sort` do C++, `Arrays.sort` do Java, `Array.Sort` do .NET) combinam os dois.

```mermaid
flowchart LR
    A["lista"] --> B{"tamanho &lt; corte?"}
    B -- "sim" --> C["🐇 inserção"]
    B -- "não" --> D["🎲 pivô aleatório"]
    D --> E["menores"]
    D --> F["iguais"]
    D --> G["maiores"]
    E --> A
    G --> A
```

## ✅ Tarefas

- [x] **1.** Quicksort com pivô aleatório, separando em menores, iguais e maiores → [`quicksort_puro`](src/ordenacao.py)
- [x] **2.** Versão que chama a inserção quando o pedaço tem menos que `corte` elementos → [`quicksort_hibrido(v, corte)`](src/ordenacao.py)
- [x] **3.** Tempo com 20 mil elementos para cortes 1, 5, 10, 16, 20, 32, 50, 100 e 200 → [`benchmark.py`](src/benchmark.py)
- [x] **4.** Comparação com o quicksort puro → [tabela](RELATORIO.md#3-tabela-de-resultados)
- [x] **5.** Gráfico do tempo em função do corte → [gráficos](RELATORIO.md#4-gráfico-tempo--corte)

**Extras:** varredura de 1 a 2 000, contagem de comparações por fase, gráficos com tema claro/escuro, testes automatizados e CI no GitHub Actions.

## 📊 Mais gráficos

<table>
<tr>
<td width="50%">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="graficos/ganho_por_corte_escuro.png">
  <img src="graficos/ganho_por_corte_claro.png" alt="Economia de tempo de cada corte em relação ao puro.">
</picture>
</td>
<td width="50%">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="graficos/varredura_estendida_escuro.png">
  <img src="graficos/varredura_estendida_claro.png" alt="Varredura de cortes de 1 a 2000 mostrando a explosão do tempo para cortes grandes.">
</picture>
</td>
</tr>
<tr>
<td colspan="2">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="graficos/operacoes_escuro.png">
  <img src="graficos/operacoes_claro.png" alt="Comparações da partição e da inserção em função do corte; as curvas se cruzam perto de 200.">
</picture>
</td>
</tr>
</table>

## 🚀 Como rodar

```bash
git clone https://github.com/Arthur-Gmb/quicksort-hibrido.git
cd quicksort-hibrido
pip install -r requirements.txt

python -m unittest discover -s tests -v   # testes de corretude
python src/benchmark.py                   # medição completa (~40 s)
python src/graficos.py                    # gera os gráficos em graficos/
```

> Quer só testar se tudo funciona? `python src/benchmark.py --rapido` roda em poucos segundos.

## 📁 Estrutura

```
quicksort-hibrido/
├── src/
│   ├── ordenacao.py      # inserção, quicksort puro e híbrido
│   ├── benchmark.py      # medição de tempo + contagem de operações
│   └── graficos.py       # gráficos (versões clara e escura)
├── tests/
│   └── test_ordenacao.py # corretude para todos os cortes e casos-limite
├── resultados/           # tempos brutos (CSV), operações (CSV) e resumo (JSON)
├── graficos/             # PNGs usados no README e no relatório
├── RELATORIO.md          # análise completa
└── .github/workflows/    # CI: roda os testes a cada push
```

## 🔍 Peculiaridades (resumo)

1. **O ótimo é uma faixa, não um número.** 16, 20 e 32 ficam a menos de 1,3 ms um do outro — menos que o ruído da medição.
2. **Corte = 1 e corte = 2 são idênticos ao puro**: a inserção só recebe listas com 0 ou 1 elemento, que já estão ordenadas.
3. **Em Python o ótimo tende a ser menor** que em C/Java, porque o `while` da inserção é interpretado passo a passo, enquanto a partição usa compreensões de lista enxutas.
4. **A partição em três listas faz 3·n comparações por nível** — é cara, e por isso cortar os níveis de baixo rende tanto.
5. **Corte grande faz a inserção dominar**: perto de 200 ela já faz mais comparações que toda a partição.

Detalhes, tabelas e explicações no **[RELATORIO.md](RELATORIO.md)**.

---

<div align="center">
<sub>Feito por <b>Arthur Gabriel Monteiro Barreiras</b> e <b>Cauã Evaristo da Cruz</b> · Ciência da Computação</sub>
</div>
