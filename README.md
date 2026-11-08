# YuukoLane

**YuukoLane** é uma linguagem de programação em português que transpila para Python. A implementação atual usa a sintaxe e o runtime do Python como base, com palavras-chave, valores e operadores localizados.

Este pacote inclui o transpilador, um validador básico e a CLI `yuuko`.

## Instalação

```bash
pip install yuukolane
```

## Exemplo

Salve como `ola.yl`:

```text
definir saudacao(nome):
    mostrar "Olá, {nome}!"

saudacao("Yuuko")
```

Execute ou valide:

```bash
yuuko ola.yl
yuuko ola.yl --checar
yuuko ola.yl --so-transpilar
```

## Documentação

A referência de sintaxe, comandos da CLI, validação, módulos e limites conhecidos está em [docs/](docs/README.md). O estado do desenvolvimento, bugs conhecidos e próximos passos ficam em [devlog/](devlog/README.md).

Há também um [backend CRUD de exemplo com FastAPI e SQLite](examples/backend_basico/README.md).

YuukoLane está em refinamento ativo. Consulte a documentação para distinguir recursos cobertos por testes dos limites ainda conhecidos.
