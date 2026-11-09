# Sintaxe da linguagem

YuukoLane usa indentação e a estrutura de comandos do Python. Os exemplos mostram a grafia reconhecida pelo dicionário incluído no pacote.

## Condições e laços

```text
se idade maior ou igual 18:
    mostrar "maior de idade"
senao se idade igual 17:
    mostrar "quase"
senao:
    mostrar "menor de idade"

enquanto ativo:
    parar

para item em intervalo(3):
    mostrar item
```

| YuukoLane | Python |
| --- | --- |
| `se` | `if` |
| `senao` | `else` |
| `senao se` | `elif` |
| `enquanto` | `while` |
| `para` | `for` |
| `com` | `with` |
| `continuar` | `continue` |
| `parar` | `break` |
| `vazio` | `pass` |

Nos cabeçalhos `se`, `senao se` e `enquanto`, um `=` simples é convertido em `==`, inclusive entre parênteses de agrupamento. Argumentos nomeados, como em `se verificar(valor=1):`, mantêm o `=`. Prefira escrever `igual` para comparação.

## Funções e retorno

```text
definir dobro(valor):
    retornar valor multiplicar 2

resultado = dobro(5)
```

`definir` e `funcao` introduzem função; `retornar` retorna um valor. Retorno fora de função é rejeitado.

Funções assíncronas combinam as palavras:

```text
async definir buscar():
    esperar obter_dados()
```

`esperar` precisa estar dentro de função `async`.

## Exceções

```text
tentar:
    lancar ValueError("entrada inválida")
capturar ValueError:
    mostrar "não foi possível processar"
finalmente:
    vazio
```

`capturar` e `exceto` são sinônimos de `except`.

## Valores vazios e literais

| YuukoLane | Python |
| --- | --- |
| `verdadeiro` | `True` |
| `falso` | `False` |
| `nulo` | `None` |
| `lista vazia` | `[]` |
| `dicionario vazio` | `{}` |
| `texto vazio` | `''` |
| `conjunto vazio` | `set()` |
| `tupla vazia` | `()` |

Esses literais não devem ser usados como nomes de variáveis.

## Operadores

| YuukoLane | Python |
| --- | --- |
| `e` / `ou` / `nao` | `and` / `or` / `not` |
| `igual` / `diferente` | `==` / `!=` |
| `maior` / `menor` | `>` / `<` |
| `maior ou igual` / `menor ou igual` | `>=` / `<=` |
| `subtrair` / `multiplicar` / `dividir` | `-` / `*` / `/` |
| `divisao inteira` / `resto` / `potencia` | `//` / `%` / `**` |
| `atribuir` | `=` |
| `somar e atribuir` / `subtrair e atribuir` | `+=` / `-=` |
| `multiplicar e atribuir` / `dividir e atribuir` | `*=` / `/=` |
| `resto e atribuir` | `%=` |

`somar` tem dois usos preservados: entre operandos, como em `a somar b`, representa adição; antes de parênteses, como em `somar(valores)`, representa a função Python `sum`.

## Strings e saída

`mostrar expressão` imprime uma expressão sem parênteses:

```text
mostrar "Olá, " somar nome
mostrar "Total: {total}"
```

Em `mostrar expressão`, strings sem prefixo que contêm campos válidos são convertidas em f-strings. Campos podem incluir expressões e formatos Python. Chaves duplas são preservadas em strings sem campos e representam chaves literais quando há interpolação. Prefixos explícitos, como `r` e `f`, mantêm o comportamento do Python.

## Identificadores

Use nomes que não sejam palavras reservadas em atribuições. Nomes de funções, classes e parâmetros são preservados nas declarações. Quando um desses nomes coincide com um alias de função ou tipo, suas referências no escopo correspondente preservam a grafia original. A análise lexical não cobre todos os casos de vinculação do Python.


## Laços, desempacotamento e compreensões

```text
nomes = [nome para nome, quantidade em [("Ana", 2), ("Ivo", 1)] se quantidade maior 1]
primeiro, segundo = ("Ana", "Ivo")
```

Alvos de laços e de desempacotamento preservam nomes que coincidem com aliases de funções ou tipos. Compreensões criam um escopo próprio. Por exemplo, em `[lista para lista em lista((1, 2))]`, o primeiro iterável usa o alias `lista(...)` do escopo externo, e o resultado usa a variável local `lista`.
