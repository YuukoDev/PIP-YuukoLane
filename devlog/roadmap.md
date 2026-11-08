# Roadmap

## Meta de produto

Direção definida pelo mantenedor: uma sintaxe Python em português, transpilada para Python e executada no runtime Python. A meta inicial é sustentar backends comuns usando o ecossistema existente. Bibliotecas próprias podem vir depois.

O objetivo é tornar Python mais simples e acessível em português, não criar runtime, ecossistema de pacotes ou linguagem incompatível independentes. A comparação anterior com TypeScript significa ambição de uso e qualidade, não um sistema de tipos próprio nem compatibilidade com TypeScript.

Critérios iniciais para um backend comum: sintaxe previsível para funções, classes, async, exceções e imports; interoperabilidade com frameworks Python; validação e diagnósticos confiáveis; fluxo reproduzível de projeto, testes e empacotamento.

## Fase 1 — Regressões e correções iniciais

- [x] Testar conversão, validação e CLI.
- [x] Corrigir impressão, interpolação e valores compostos.
- [x] Manter os dois usos atuais de `somar`.
- [x] Corrigir escopos aninhados e compilar o Python gerado.
- [x] Testar import relativo em pacote e import circular.
- [x] Criar primeira referência pública e devlog de manutenção.

## Fase 2 — Estabilizar a linguagem

- [x] Testar cada entrada do dicionário isoladamente.
- [ ] Inventariar interações e limitações entre os termos.
- [x] Traduzir nomes e termos compostos com base nos tokens do Python, sem substituir conteúdo de strings e comentários.
- [ ] Definir a matriz de compatibilidade com sintaxe Python e versões de runtime suportadas.
- [ ] Revisar palavras reservadas e colisões de nomes do Python com as traduções portuguesas.
- [ ] Padronizar erros do transpilador com linha e coluna do arquivo `.yl`.
- [ ] Remover gradualmente transformações regex especiais quando houver forma token-aware equivalente.

## Fase 3 — Construção de aplicações

- [x] Criar um backend de exemplo com framework Python existente, persistência SQLite e teste de rotas.
- [ ] Revisar isolamento e ciclo de vida dos módulos em `sys.modules`.
- [ ] Definir resolução configurável de módulos e dependências.
- [ ] Planejar uma ou duas bibliotecas próprias apenas após validar as necessidades dos primeiros backends.
- [ ] Melhorar scaffolding, execução, testes e empacotamento de projetos.
- [ ] Padronizar códigos de saída, caminhos e diagnósticos da CLI.
- [ ] Validar Python 3.8 em CI.
- [ ] Ampliar o exemplo para configuração por ambiente, concorrência e estrutura multi-módulo.

## Fase 4 — Publicação e manutenção

- [ ] Documentar API, instalação e suporte por versão/plataforma.
- [ ] Validar sdist/wheel e instalação isolada.
- [ ] Definir política de versionamento e compatibilidade antes da próxima publicação.
- [ ] Criar CI para testes, lint e build.

O roadmap não autoriza publicação, release ou deploy; isso permanece sob controle do mantenedor.
