# Funções e tipos comuns

YuukoLane traduz nomes do dicionário para nomes Python. Os objetos e comportamentos continuam sendo os do Python.

## Funções comuns

| YuukoLane | Python |
| --- | --- |
| `mostrar` | `print` |
| `entrada` | `input` |
| `tamanho` | `len` |
| `somar(lista)` | `sum(lista)` |
| `maximo` / `minimo` | `max` / `min` |
| `str`, `int`, `float` | mesmos nomes |
| `tipo` | `type` |
| `abrir` | `open` |
| `intervalo` | `range` |
| `enumerar` | `enumerate` |
| `mapear` / `filtrar` | `map` / `filter` |
| `todos` / `algum` | `all` / `any` |

```text
nomes = ["Ana", "Ivo"]
mostrar tamanho(nomes)
para posicao, nome em enumerar(nomes):
    mostrar nome
```

## Métodos de coleções

Use estes nomes depois do ponto:

| YuukoLane | Python |
| --- | --- |
| `adicionar` | `append` |
| `remover` | `remove` |
| `ordenar` | `sort` |
| `reverter` | `reverse` |
| `contar` | `count` |
| `indexar` | `index` |
| `copiar` | `copy` |

```text
nomes = ["Ana"]
nomes.adicionar("Ivo")
nomes.ordenar()
```

## Tipos

| YuukoLane | Python |
| --- | --- |
| `inteiro` | `int` |
| `decimal` | `float` |
| `texto` | `str` |
| `lista` | `list` |
| `dicionario` | `dict` |
| `booleano` | `bool` |
| `conjunto` | `set` |
| `tupla` | `tuple` |

## Outros nomes

`classe` traduz para `class`; `global` permanece `global`; `nao local` traduz para `nonlocal`; `em` traduz para `in`; `del` e `lambda` permanecem iguais. `is` também permanece igual.

O nome depois do ponto tem prioridade. Se um objeto define `adicionar`, esse atributo é usado. Se o atributo está ausente e o receptor é uma coleção embutida do Python com o método correspondente, YuukoLane usa o alias. A regra vale para listas passadas como parâmetros ou retornadas por funções. Para outros objetos, um atributo ausente gera o erro normal do Python.

A regra cobre leituras de atributos e chamadas comuns. Atribuições, exclusões, nomes em padrões, anotações, referências a decoradores e rótulos de f-strings de depuração mantêm a sintaxe de atributo do Python.
