"""Testes de corretude. Rode com: python -m unittest discover -s tests"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ordenacao import insercao, quicksort_hibrido, quicksort_puro  # noqa: E402

CORTES = [1, 5, 10, 16, 20, 32, 50, 100, 200]


class TestOrdenacao(unittest.TestCase):
    def casos(self):
        rng = random.Random(42)
        yield []
        yield [7]
        yield [2, 1]
        yield [5] * 50                                  # todos iguais
        yield list(range(300))                          # já ordenada
        yield list(range(300, 0, -1))                   # ordem inversa
        yield [rng.randint(0, 10) for _ in range(500)]  # muitas repetições
        yield [rng.random() for _ in range(1000)]       # floats
        yield [rng.randint(-10**6, 10**6) for _ in range(2000)]

    def test_insercao(self):
        for v in self.casos():
            self.assertEqual(insercao(v), sorted(v))

    def test_quicksort_puro(self):
        for v in self.casos():
            self.assertEqual(quicksort_puro(v), sorted(v))

    def test_quicksort_hibrido_todos_os_cortes(self):
        for corte in CORTES + [10_000]:
            for v in self.casos():
                with self.subTest(corte=corte, n=len(v)):
                    self.assertEqual(quicksort_hibrido(v, corte), sorted(v))

    def test_nao_altera_entrada(self):
        v = [3, 1, 2]
        quicksort_hibrido(v, 16)
        quicksort_puro(v)
        self.assertEqual(v, [3, 1, 2])

    def test_corte_1_nunca_usa_insercao(self):
        """Com corte = 1, a inserção só é chamada para a lista vazia."""
        import ordenacao

        chamadas = []
        original = ordenacao.insercao
        ordenacao.insercao = lambda v: chamadas.append(len(v)) or original(v)
        try:
            ordenacao.quicksort_hibrido(list(range(1000, 0, -1)), 1)
        finally:
            ordenacao.insercao = original
        self.assertTrue(all(n == 0 for n in chamadas))


if __name__ == "__main__":
    unittest.main()
