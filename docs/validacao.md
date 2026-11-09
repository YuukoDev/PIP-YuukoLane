# Validação

O validador aplica regras YuukoLane ao Python gerado. Em seguida, o transpilador chama `compile(..., "exec")` para detectar sintaxe Python inválida.

## Códigos

| Código | Significado |
| --- | --- |
| YK101 | Atribuição a literal reservado (`verdadeiro`, `falso`, `nulo`) |
| YK102 | Atribuição a identificador reservado detectado |
| YK201 | `retornar`/`return` fora de função |
| YK202 | `esperar`/`await` fora de função assíncrona |

O validador usa a árvore sintática do Python gerado. O corpo de cada função, classe ou lambda tem seu próprio contexto. Valores padrão, decoradores e bases de classes são avaliados no contexto externo.

## Limites

A validação de identificadores e escopos ainda não cobre toda a gramática Python. Desempacotamento, alvos em laços, nomes em parâmetros e declarações complexas podem escapar às verificações YK101/YK102. A compilação final detecta sintaxe Python inválida.

Erros de sintaxe e validação indicam o arquivo e a linha do código YuukoLane original. Quando a tradução altera a linha, o diagnóstico pode omitir a coluna.
