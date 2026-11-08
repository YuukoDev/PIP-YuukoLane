# Documentação YuukoLane

YuukoLane é uma camada de sintaxe em português traduzida para Python. A referência descreve o comportamento da implementação atual; recursos que dependem de regras ainda não estabilizadas estão identificados como limites.

## Guias

- [Visão geral e primeiros passos](visao-geral.md)
- [Sintaxe e palavras da linguagem](sintaxe.md)
- [Funções e bibliotecas comuns](biblioteca.md)
- [CLI e execução](cli.md)
- [Módulos e imports](modulos.md)
- [Validação e erros](validacao.md)
- [Arquitetura atual e limites](arquitetura.md)
- [Backend FastAPI de exemplo](backend.md)

## Testes

Os testes automatizados em `tests/` servem como referência executável:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
```

O progresso, bugs e tarefas pendentes estão em [devlog/](../devlog/README.md).
