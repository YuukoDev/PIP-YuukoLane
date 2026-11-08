# Módulos e imports

Arquivos locais podem usar a sintaxe de import do Python:

```text
from calculos import dobro
mostrar dobro(4)
```

O carregador procura módulos `.yl` e `.py` locais a partir do diretório do programa principal. Os arquivos `.yl` são transpilados; os arquivos `.py` são usados como estão. Módulos são preparados como Python e carregados pelo mecanismo normal de imports.

## Pacotes e imports relativos

Imports de módulos em subdiretórios são suportados:

```text
from aplicacao.calculos import dobro
```

Imports relativos dentro de um módulo de pacote também são suportados:

```text
from .constantes import FATOR
```

Imports circulares seguem a ordem de execução do Python. Como em Python, um módulo não pode importar um nome que ainda não foi definido durante o ciclo.

## Bibliotecas externas

Imports sem arquivo correspondente no projeto são deixados para o Python. Instale dependências externas no mesmo ambiente que executa `yuuko`.

## Limites

- Imports relativos no arquivo principal executado diretamente não têm pacote de origem e não são suportados.
- Imports dinâmicos de módulos `.yl` não podem ser descobertos antecipadamente para transpilação.
- A busca começa no diretório do programa; não há configuração própria de caminhos ou dependências.
- Módulos preparados são armazenados em `sys.modules`; projetos diferentes com nomes iguais podem interferir quando executados no mesmo processo.
