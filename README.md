# Visão computacional para identificação de embalagens

Demo em Python 3.10+ que gera imagens sintéticas de embalagens, extrai cor e proporção do objeto e compara os atributos com o centro de cada categoria. Objetos distantes das classes, sem margem suficiente ou sem primeiro plano vão para revisão manual.

```sh
python classificador.py --avaliar
python classificador.py --gerar amostras
python classificador.py --imagem amostras/frasco-estreito.ppm
```

A avaliação usa 60 imagens geradas com sementes distintas das 36 usadas para calibrar o classificador. Também verifica uma imagem vazia. Mede apenas o comportamento no conjunto sintético. Os objetos são retângulos coloridos sobre fundo claro, sem texturas ou sombras. O leitor aceita PPM P6 RGB com cabeçalho de três linhas e escala 255. Nenhuma dependência externa.
