"""Classifica embalagens sintéticas em imagens PPM RGB (P6)."""
import argparse
from collections import Counter
from math import dist
from pathlib import Path
from random import Random
from statistics import mean

LABELS = {
    "frasco-estreito": (11, 36, (35, 96, 170)),
    "caixa-media": (23, 31, (151, 39, 89)),
    "estojo-largo": (36, 16, (25, 126, 91)),
}
SIZE = 48


def sample(label, seed):
    rng = Random(seed)
    width, height, color = LABELS[label]
    width += rng.randint(-4, 4)
    height += rng.randint(-4, 4)
    left, top = rng.randint(0, SIZE - width), rng.randint(0, SIZE - height)
    tint = [rng.randint(-16, 16) for _ in color]
    fg = bytes(channel + offset for channel, offset in zip(color, tint))
    bg = bytes([rng.randint(234, 255)] * 3)
    return b"".join(
        fg if left <= x < left + width and top <= y < top + height else bg
        for y in range(SIZE) for x in range(SIZE)
    )


def features(pixels, width):
    points = []
    for offset in range(0, len(pixels), 3):
        rgb = pixels[offset:offset + 3]
        if min(rgb) < 210:
            y, x = divmod(offset // 3, width)
            points.append((x, y, *rgb))
    if len(points) < 20:
        return None
    xs, ys, *colors = zip(*points)
    horizontal = max(xs) - min(xs) + 1
    vertical = max(ys) - min(ys) + 1
    return (horizontal / (horizontal + vertical), *(mean(c) / 255 for c in colors))


def train():
    result = {}
    for label in LABELS:
        vectors = [features(sample(label, seed), SIZE) for seed in range(12)]
        result[label] = tuple(mean(values) for values in zip(*vectors))
    return result


def predict(vector, classes):
    if vector is None:
        return "revisão manual"
    first, second, *_ = sorted((dist(vector, center), label) for label, center in classes.items())
    return first[1] if first[0] <= 0.16 and second[0] - first[0] >= 0.06 else "revisão manual"


def read_ppm(path):
    with path.open("rb") as stream:
        if stream.readline(32).strip() != b"P6":
            raise ValueError("Use PPM P6 com cabeçalho de três linhas.")
        width, height = map(int, stream.readline(64).split())
        if not (1 <= width <= 512 and 1 <= height <= 512):
            raise ValueError("Dimensões inválidas.")
        if stream.readline(32).strip() != b"255":
            raise ValueError("A escala de cor deve ser 255.")
        expected = width * height * 3
        pixels = stream.read(expected + 1)
        if len(pixels) != expected:
            raise ValueError("Tamanho de imagem incompatível com o cabeçalho.")
        return pixels, width


def evaluate(classes):
    counts = Counter((label, predict(features(sample(label, seed), SIZE), classes))
                     for label in LABELS for seed in range(100, 120))
    print("Esperado / previsto:", " | ".join([*LABELS, "revisão manual"]))
    for label in LABELS:
        print(label, "|", " | ".join(str(counts[label, result]) for result in [*LABELS, "revisão manual"]))
    print("Acertos:", sum(counts[label, label] for label in LABELS), "/", sum(counts.values()))
    print("Imagem sem produto:", predict(features(bytes([255] * SIZE * SIZE * 3), SIZE), classes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--avaliar", action="store_true")
    group.add_argument("--gerar", type=Path, metavar="PASTA")
    group.add_argument("--imagem", type=Path, metavar="ARQUIVO.PPM")
    args = parser.parse_args()
    classes = train()
    try:
        if args.avaliar:
            evaluate(classes)
        elif args.gerar:
            args.gerar.mkdir(parents=True, exist_ok=True)
            for label in LABELS:
                path = args.gerar / (label + ".ppm")
                with path.open("xb") as stream:
                    stream.write(f"P6\n{SIZE} {SIZE}\n255\n".encode() + sample(label, 42))
                print(path)
        else:
            print(predict(features(*read_ppm(args.imagem)), classes))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
