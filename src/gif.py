"""Gera graficos/animacao.gif: o quicksort híbrido ordenando barras (corte = 8)."""

import os
import random

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.join(os.path.dirname(__file__), "..")
N, CORTE = 48, 8
W, H = 900, 380
FUNDO, PALCO = (232, 237, 243), (245, 247, 250)
TINTA, TINTA2 = (19, 32, 58), (74, 88, 116)
FORA, ATIVA = (195, 204, 217), (131, 145, 168)
QUICK, QUICK_CLARO = (49, 86, 211), (159, 178, 239)
INS, INS_CLARO, PIVO, PRONTO = (238, 155, 0), (247, 205, 128), (224, 51, 90), (27, 127, 107)


def fonte(tam, negrito=False):
    nome = "DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf"
    for base in ("/usr/share/fonts/truetype/dejavu/", ""):
        try:
            return ImageFont.truetype(base + nome, tam)
        except OSError:
            pass
    return ImageFont.load_default()


F_T, F_N, F_P = fonte(22, True), fonte(15), fonte(13)


def gerar_quadros():
    rng = random.Random(11)
    vals = [6 + round(i / (N - 1) * 94) for i in range(N)]
    rng.shuffle(vals)
    a = list(range(N))  # ids; valor = vals[id]
    quadros = []
    pronto = set()

    def foto(cores, msg, faixa=None, modo=None, dur=70):
        quadros.append((list(a), dict(cores), set(pronto), msg, faixa, modo, dur))

    def rec(lo, hi):
        n = hi - lo
        if n < CORTE:
            ids = a[lo:hi]
            base = {i: INS_CLARO for i in ids}
            if n:
                foto(base, f"Pedaço de {n} < corte: inserção", (lo, hi), "ins", 260)
            for i in range(lo + 1, hi):
                j = i
                while j > lo:
                    foto({**base, a[j - 1]: INS, a[j]: INS}, f"Pedaço de {n} < corte: inserção", (lo, hi), "ins", 70)
                    if vals[a[j - 1]] > vals[a[j]]:
                        a[j - 1], a[j] = a[j], a[j - 1]
                        j -= 1
                    else:
                        break
            pronto.update(a[lo:hi])
            return
        if n <= 1:
            pronto.update(a[lo:hi])
            return
        pedaco = a[lo:hi]
        pid = pedaco[rng.randrange(n)]
        p = vals[pid]
        me = [i for i in pedaco if vals[i] < p]
        ig = [i for i in pedaco if vals[i] == p]
        ma = [i for i in pedaco if vals[i] > p]
        foto({i: ATIVA for i in pedaco}, f"Quicksort em {n} elementos", (lo, hi), "quick", 320)
        cores = {**{i: QUICK for i in me}, **{i: QUICK_CLARO for i in ma}, **{i: PIVO for i in ig}}
        foto(cores, f"Pivô {p}: {len(me)} menores, {len(ma)} maiores", (lo, hi), "quick", 650)
        a[lo:hi] = me + ig + ma
        foto(cores, "Separa em menores · iguais · maiores", (lo, hi), "quick", 650)
        pronto.update(ig)
        rec(lo, lo + len(me))
        rec(lo + len(me) + len(ig), hi)

    foto({}, "Lista embaralhada", None, None, 900)
    rec(0, N)
    foto({}, "Ordenado!", None, None, 2200)
    return quadros, vals


def desenhar(q, vals):
    ordem, cores, pronto, msg, faixa, modo, _ = q
    im = Image.new("RGB", (W, H), FUNDO)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, W - 12, H - 12), 18, fill=PALCO, outline=(205, 213, 225))
    d.text((36, 30), "Quicksort híbrido", font=F_T, fill=TINTA)
    d.text((W - 36, 36), f"corte = {CORTE}", font=F_N, fill=INS, anchor="ra")
    x0, x1, base, alt = 36, W - 36, H - 78, 220
    passo = (x1 - x0) / N
    larg = passo * 0.78
    for pos, i in enumerate(ordem):
        cor = PRONTO if i in pronto and i not in cores else cores.get(i, FORA)
        h = vals[i] / 100 * alt
        x = x0 + pos * passo
        d.rounded_rectangle((x, base - h, x + larg, base), 3, fill=cor)
    d.line((x0, base + 1, x1, base + 1), fill=(205, 213, 225), width=2)
    if faixa:
        lo, hi = faixa
        d.rounded_rectangle((x0 + lo * passo, base + 9, x0 + hi * passo - 3, base + 15), 3,
                            fill=INS if modo == "ins" else QUICK)
    d.text((36, H - 46), msg, font=F_N, fill=TINTA2)
    leg = [(PIVO, "pivô"), (QUICK, "menores"), (INS, "inserção"), (PRONTO, "no lugar")]
    x = W - 36
    for cor, nome in reversed(leg):
        tw = d.textlength(nome, font=F_P)
        x -= tw
        d.text((x, H - 44), nome, font=F_P, fill=TINTA2)
        x -= 18
        d.rounded_rectangle((x, H - 41, x + 11, H - 30), 2, fill=cor)
        x -= 16
    return im


def main():
    quadros, vals = gerar_quadros()
    imgs = [desenhar(q, vals) for q in quadros]
    dur = [q[6] for q in quadros]
    # paleta única para todos os quadros (cores estáveis entre quadros)
    amostra = Image.new("RGB", (W, H * len(imgs[::6])))
    for k, im in enumerate(imgs[::6]):
        amostra.paste(im, (0, H * k))
    paleta = amostra.quantize(colors=64, method=Image.MEDIANCUT)
    pal = [im.quantize(palette=paleta, dither=Image.Dither.NONE) for im in imgs]
    destino = os.path.join(RAIZ, "graficos", "animacao.gif")
    pal[0].save(destino, save_all=True, append_images=pal[1:], duration=dur, loop=0, optimize=True)
    print(destino, len(imgs), "quadros", os.path.getsize(destino) // 1024, "KB")


if __name__ == "__main__":
    main()
