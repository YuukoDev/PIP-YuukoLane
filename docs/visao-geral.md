# Primeiros passos com YuukoLane

Você escreve um arquivo `.yl` em português, e o comando `yuuko` traduz e executa o código no Python. A indentação e as APIs de bibliotecas seguem as regras do Python.

## 1. Instale a CLI

Em um ambiente com Python, execute:

```bash
python -m pip install yuukolane
yuuko --help
```

Para testar a versão deste repositório, rode `python -m pip install .` na raiz do checkout.

## 2. Escreva seu primeiro programa

Crie `ola.yl` com o seguinte conteúdo:

```text
definir saudacao(nome):
    mostrar "Olá, {nome}!"

saudacao("Yuuko")
```

```bash
yuuko ola.yl
```

A saída é `Olá, Yuuko!`. Use quatro espaços para os comandos dentro da função. Em `mostrar`, o campo `{nome}` recebe o valor do parâmetro.

## 3. Use listas, laços e condições

Salve este exemplo como `pedidos.yl`:

```text
definir pedidos_validos(pedidos):
    validos = lista vazia
    para nome, quantidade em pedidos:
        se quantidade maior ou igual 2:
            validos.adicionar(nome)
    retornar validos

pedidos = [("Ana", 2), ("Ivo", 1)]
validos = pedidos_validos(pedidos)
mostrar "Pedidos válidos: {validos}"
```

O programa imprime `Pedidos válidos: ['Ana']`. O laço desempacota cada par em `nome` e `quantidade`. A condição filtra os pedidos e `.adicionar()` usa o método `.append()` da lista.

## 4. Use uma biblioteca Python

O comando `import` e os métodos de bibliotecas mantêm a grafia da API Python:

```text
import json

dados = {"nome": "Ana", "quantidade": 2}
mostrar json.dumps(dados)
```

Para separar um programa em arquivos, veja [módulos e imports](modulos.md). Para um exemplo maior, veja o [backend com FastAPI e SQLite](backend.md).

## 5. Valide e veja o Python gerado

```bash
yuuko pedidos.yl --checar
yuuko pedidos.yl --so-transpilar
```

`--checar` aponta erros sem executar o programa. `--so-transpilar` imprime o Python gerado, o que ajuda a entender a tradução de um trecho.

Consulte a [referência de sintaxe](sintaxe.md) para operadores, funções, exceções e assincronismo. A [página de validação](validacao.md) explica os códigos de erro da linguagem. O CI testa o pacote do Python 3.8 ao 3.14.
