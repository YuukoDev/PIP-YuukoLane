# Validação

O validador aplica regras YuukoLane ao Python gerado. Em seguida, o transpilador chama `compile(..., "exec")` para detectar sintaxe Python inválida.

## Códigos

| Código | Significado |
| --- | --- |
| YK101 | Atribuição a literal reservado (`verdadeiro`, `falso`, `nulo`) |
| YK102 | Atribuição a identificador reservado detectado |
| YK201 | `retornar`/`return` fora de função |
| YK202 | `esperar`/`await` fora de função assíncrona |

O validador acompanha classes e funções por indentação. O escopo mais próximo define se retorno e espera são aceitos.

## Limites

A validação de identificadores e escopos ainda não cobre toda a gramática Python. Desempacotamento, alvos em laços, nomes em parâmetros e declarações complexas podem escapar às verificações YK101/YK102. A compilação final detecta sintaxe Python inválida.

Strings e comentários são protegidos durante as verificações para reduzir falsos positivos.
