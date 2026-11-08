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

O dicionário traduz nomes de forma textual; ele não localiza nomes de APIs ou módulos externos.
