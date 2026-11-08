# Contribuindo com a YuukoLane

Obrigado por ajudar a tornar a YuukoLane mais confiável! A proposta é oferecer sintaxe em português que transpila para Python, preservando o runtime e o ecossistema Python.

## Antes de contribuir

- Leia [a documentação](docs/README.md), [os limites atuais](docs/arquitetura.md) e [o roadmap](devlog/roadmap.md).
- Para bugs e correções pequenas, você pode abrir um pull request diretamente.
- Para novas palavras reservadas, mudanças de sintaxe, compatibilidade ou arquitetura, abra uma issue primeiro para discutir o comportamento esperado.
- Não inclua credenciais, tokens, dados pessoais ou dependências desnecessárias.

## Como reportar um bug

Use o formulário **Bug report** em Issues. Inclua um exemplo mínimo de código `.yl`, saída esperada, saída real, comando usado e versão do Python. Remova segredos dos logs.

## Como propor uma funcionalidade

Use o formulário **Feature request**. Explique o problema, a sintaxe sugerida, o Python esperado e possíveis colisões com identificadores existentes.

## Desenvolvimento local

Requer Python 3.8+.

```bash
python -m pip install -e .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
python -m pip install -r examples/backend_basico/requirements.txt
cd examples/backend_basico
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../src python -m unittest -v test_backend
```

Os testes do backend usam dependências opcionais e não fazem parte das dependências obrigatórias do pacote.

## Fluxo de contribuição

1. Faça fork do projeto e crie uma branch descritiva a partir de `master`.
2. Faça alterações pequenas e focadas, incluindo testes de regressão para correções de bugs.
3. Atualize documentação e exemplos quando alterar comportamento público.
4. Execute os testes localmente.
5. Abra um **pull request** para `master`, preenchendo o template.
6. Aguarde a revisão e o CI. Não faça push direto em `master` para contribuições.

**Toda contribuição de código deve ser submetida por pull request.** Abrir issue antes do PR é recomendado para mudanças de design, mas não obrigatório para correções simples.

O CI verifica testes em múltiplas versões de Python, testes opcionais de backend e build. Aprovação do CI não garante que uma mudança será aceita; mantenedores também revisam compatibilidade e escopo.

## Princípios de compatibilidade

- Não traduza conteúdo de strings ou comentários acidentalmente.
- Preserve semântica Python e documente diferenças intencionais.
- Cuidado com colisões entre nomes de usuário e palavras do dicionário.
- Não introduza novas dependências de runtime sem justificativa.
- Não publique versões ou faça deploy como parte de um PR comum.

## Código de conduta

Seja respeitoso e construtivo nas discussões. Relate problemas de segurança de forma privada ao mantenedor, evitando publicar detalhes exploráveis em issues.
