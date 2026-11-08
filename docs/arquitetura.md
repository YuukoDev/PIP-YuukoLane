# Arquitetura atual e limites

## Pipeline de transpilação

1. O tokenizer padrão do Python identifica strings, comentários, nomes e pontuação.
2. Strings e comentários são protegidos enquanto os nomes YuukoLane são traduzidos; nomes de várias palavras são reconhecidos como sequências de tokens.
3. `somar(...)` é reconhecido como a função agregadora, enquanto `somar` entre operandos é o operador.
4. Cabeçalhos condicionais recebem uma correção legada de comparação.
5. `mostrar expressão` é convertido em `print(...)`; chaves em strings ativam f-string.
6. Marcadores são restaurados, regras YK são aplicadas e o Python final é compilado.

## Componentes

- `src/yuukolane/dicionario.json`: vocabulário e traduções.
- `src/yuukolane/yuukolane_transpiler.py`: conversão, validação e conversão de arquivo.
- `src/yuukolane/validador.py`: regras de identificadores e contexto.
- `src/yuukolane/cli.py`: CLI, preparação de módulos e execução.
- `tests/`: regressões de transpilação, validação, imports e CLI.

## Limites de desenho

- A tradução dos nomes é lexical, mas as transformações especiais de cabeçalhos e saída ainda usam regex.
- O validador de escopo aproxima blocos a partir da indentação.
- Não há gramática formal versionada nem regras completas de precedência próprias.
- A semântica das expressões e APIs vem do Python.
- A compatibilidade declarada com Python 3.8 ainda precisa de validação automatizada nessa versão.

O objetivo é acompanhar a gramática do Python e localizar apenas os tokens definidos pelo dicionário, preservando o runtime e o ecossistema Python. O devlog acompanha as diferenças e limitações que ainda precisam de compatibilidade explícita.
