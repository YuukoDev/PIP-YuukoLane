# CLI

O pacote instala o comando `yuuko`.

```bash
yuuko arquivo.yl
yuuko arquivo.yl --checar
yuuko arquivo.yl --so-transpilar
yuuko arquivo.yl --debug
```

## Opções

- `--checar`: transpila e valida sem executar o programa. Erros de contexto conhecidos e sintaxe Python inválida são reportados.
- `--so-transpilar`: escreve o Python gerado na saída padrão, sem executar nem salvar um arquivo.
- `--debug`: mostra o Python gerado antes da execução e detalhes de preparação de módulos.
- Sem opção: transpila e executa.

A CLI também aceita um arquivo `.py` para execução. As opções de transpilação se destinam principalmente a arquivos `.yl`.

## Limites atuais

Falhas de arquivo inválido retornam status 2; erros de transpilação/validação retornam status 1. Sucesso retorna 0. A detecção de async que escolhe subprocesso procura as substrings `asyncio.run` e `async def main`, sem analisar a estrutura sintática.
