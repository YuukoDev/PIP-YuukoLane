# Estado atual

Atualizado em 2026-11-08.

## Direção definida pelo mantenedor

YuukoLane é uma sintaxe Python em português, transpilada e executada no runtime Python. A primeira meta de produto é construir backends comuns aproveitando frameworks e pacotes Python existentes. Bibliotecas próprias podem vir depois; não há objetivo atual de criar runtime ou sistema de tipos independente.

## Implementado nesta rodada

- Suíte de testes com `unittest`, sem dependência externa.
- Tradução de `mostrar`, interpolação, valores compostos e regra contextual de `somar`.
- Tradução de nomes agora usa o tokenizer Python, respeitando strings, comentários e limites de identificadores.
- Compilação do Python gerado para detectar sintaxe inválida.
- Validação contextual de retorno e espera pelo escopo mais próximo.
- Preparação de imports estáticos `.yl` e `.py`, incluindo pacote, import relativo em pacote e ciclos.
- Testes de CLI, validação, transpilação e imports.
- Exemplo FastAPI CRUD com SQLite e teste HTTP via ASGI; dependências isoladas no exemplo.

## Bugs e limites conhecidos

1. **Transformações regex residuais:** cabeçalhos de comparação e forma curta de `mostrar` ainda dependem de regex.
2. **Validação de nomes parcial:** YK101/YK102 cobrem atribuições simples, não todos os destinos de atribuição, parâmetros e declarações.
3. **Imports locais limitados:** busca a partir do diretório do programa, imports relativos do arquivo principal e imports dinâmicos de `.yl` não são suportados.
4. **Cache global de módulos:** nomes iguais em projetos diferentes podem conflitar em `sys.modules`.
5. **Detecção de async:** decisão de usar subprocesso baseada em busca textual, não análise sintática.
6. **Compatibilidade ainda incompleta:** falta uma matriz de recursos Python por versão e regras documentadas para construções que a tradução altera.
7. **Cobertura parcial:** testes cobrem os caminhos principais e cada termo isolado, não todas as combinações de sintaxe.

## Testes

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Última execução registrada: 33 testes principais aprovados e 2 testes de integração opcionais do backend aprovados; cada entrada do dicionário tem uma verificação de tradução.
