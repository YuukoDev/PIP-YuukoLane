# Visão geral

YuukoLane permite escrever comandos e expressões do Python usando palavras em português. É uma camada transpilada de sintaxe, não um runtime independente: o transpilador lê um arquivo `.yl`, localiza termos do dicionário e entrega código Python para o interpretador executar.

## Primeiro programa

Crie `ola.yl`:

```text
definir saudacao(nome):
    mostrar "Olá, {nome}!"

saudacao("Yuuko")
```

Execute:

```bash
yuuko ola.yl
```

O trecho é convertido para Python equivalente a:

```python
def saudacao(nome):
    print(f"Olá, {nome}!")

saudacao("Yuuko")
```

## Modelo mental

- Indentação, expressões, funções, classes, coleções e chamadas seguem a base de Python.
- Palavras localizadas estão listadas em [sintaxe](sintaxe.md) e [biblioteca](biblioteca.md).
- Imports locais `.yl` são convertidos para Python antes do carregamento.
- Não há runtime independente: APIs e pacotes Python são a base de interoperabilidade.
- A meta inicial é permitir aplicações comuns, como backends web, usando frameworks Python existentes.
- Bibliotecas próprias podem ser acrescentadas depois, sem substituir a interoperabilidade com Python.

## Compatibilidade

O pacote declara Python 3.8 ou superior. Os testes de desenvolvimento usam `unittest`, sem adicionar dependências de teste ao pacote.

## Limites

YuukoLane está em evolução. A tradução dos nomes usa tokens Python; algumas transformações específicas ainda usam regex e nem todos os recursos do Python foram auditados. Consulte [arquitetura e limites](arquitetura.md) e o [devlog](../devlog/README.md) antes de depender de construções menos comuns.
