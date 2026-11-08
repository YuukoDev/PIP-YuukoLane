AGENTS.md — PIP-YuukoLane

1. Objetivo

Este arquivo define as regras, limites e orientações para agentes de IA que trabalham no repositório PIP-YuukoLane.

O agente deve utilizar este arquivo como conjunto de regras operacionais permanentes.

O PIP-YuukoLane é um projeto de biblioteca Python, com código-fonte em "src/", configuração de empacotamento em "pyproject.toml" e distribuição potencial pelo PyPI.

A documentação localizada em "docs/", quando existir, é a principal fonte de verdade sobre o comportamento e os requisitos do projeto.

---

2. Regra fundamental

Antes de implementar qualquer funcionalidade:

1. Leia a tarefa atual em ".codex/task.md", quando existir.
2. Leia ".codex/checkpoint.md", quando existir.
3. Consulte a documentação relevante em "docs/", quando existir.
4. Consulte "README.md" e "pyproject.toml" quando relevantes.
5. Inspecione o código existente em "src/" relacionado ao problema.
6. Entenda as dependências entre módulos, interfaces públicas e componentes antes de alterar arquivos.

Não implemente funcionalidades importantes apenas com base em suposições.

Quando a documentação não definir determinado comportamento suficientemente, não invente regras de negócio ou contratos públicos silenciosamente.

Registre a dúvida em ".codex/interventions.md" e interrompa apenas a parte da implementação que depende dessa decisão.

---

3. Escopo de atuação

O agente está autorizado a:

- Criar arquivos necessários para a implementação.
- Alterar arquivos pertencentes ao PIP-YuukoLane.
- Implementar funcionalidades documentadas.
- Criar e executar testes automatizados.
- Executar ferramentas de análise, lint e validação.
- Construir pacotes locais para verificar o empacotamento.
- Corrigir erros encontrados durante os testes.
- Refatorar código quando necessário.
- Atualizar documentação técnica.
- Atualizar arquivos de estado dentro de ".codex/".
- Gerenciar ambientes virtuais e dependências locais do projeto quando necessário.

O agente não deve expandir o escopo da tarefa sem necessidade.

3.1. Execução fora do sandbox

O agente está autorizado a executar comandos diretamente no ambiente da VPS e fora do sandbox fornecido pela interface, desde que:

- O comando esteja relacionado ao PIP-YuukoLane.
- Seja necessário para implementar, testar, validar ou diagnosticar a tarefa.
- Não altere outros projetos, produção ou infraestrutura.
- Não seja destrutivo sem necessidade.
- Não exponha credenciais, secrets ou dados sensíveis.

Essa autorização não permite:

- Fazer deploy.
- Publicar pacotes no PyPI ou TestPyPI.
- Publicar releases.
- Executar "git push".
- Alterar Nginx, firewall, SSH ou DNS.
- Reiniciar serviços de produção.
- Alterar outros projetos.
- Executar comandos destrutivos fora do projeto.

Quando um comando necessário estiver bloqueado pelo sandbox, o agente pode solicitar autorização para executá-lo diretamente no ambiente permitido da VPS, respeitando os limites deste documento.

As regras deste arquivo não substituem políticas ou restrições de segurança impostas pela ferramenta.

---

4. Fonte de verdade

A prioridade das informações é:

1. Requisitos explícitos da tarefa atual.
2. Documentação do projeto em "docs/", quando existir.
3. Contratos públicos e comportamentos documentados no "README.md".
4. Arquitetura e padrões existentes no código.
5. Configurações do "pyproject.toml".
6. Convenções do projeto.
7. Inferência técnica.

Nunca substitua uma regra explícita por preferência pessoal.

Quando duas fontes entrarem em conflito, registre o conflito em ".codex/interventions.md".

Não resolva conflitos relevantes silenciosamente.

---

5. Limites de produto

O agente não deve:

- Criar funcionalidades não especificadas.
- Alterar comportamentos públicos sem justificativa.
- Remover funcionalidades documentadas sem autorização.
- Simplificar requisitos importantes.
- Introduzir dependências externas desnecessárias.
- Trocar tecnologias ou arquitetura sem autorização.
- Alterar interfaces públicas sem avaliar compatibilidade.
- Modificar contratos de entrada e saída sem documentação.
- Alterar a versão do pacote sem necessidade ou autorização.
- Publicar versões automaticamente.

Mudanças incompatíveis devem ser identificadas e documentadas.

---

6. Segurança

Segurança possui prioridade sobre velocidade.

Nunca:

- Exponha secrets.
- Imprima tokens ou credenciais em logs.
- Commite arquivos ".env" contendo credenciais.
- Copie credenciais para código-fonte.
- Desative validações de segurança para facilitar testes.
- Utilize dados reais de produção em testes.
- Apague dados de produção.
- Execute comandos destrutivos fora do escopo.
- Inclua credenciais nos artefatos de distribuição.
- Publique pacotes contendo informações privadas.

Se uma tarefa exigir credenciais indisponíveis, registre a necessidade em ".codex/interventions.md".

---

7. Limites da VPS

O agente deve considerar a VPS um ambiente compartilhado.

É proibido, salvo autorização explícita:

- Alterar Nginx.
- Alterar firewall.
- Alterar SSH.
- Alterar usuários do sistema.
- Alterar permissões de outros projetos.
- Alterar serviços de outros projetos.
- Parar ou reiniciar PM2 de produção.
- Parar ou reiniciar serviços de produção.
- Alterar configurações globais do sistema operacional.
- Reiniciar a VPS.
- Executar comandos destrutivos fora do projeto.
- Alterar configurações de rede.
- Alterar DNS.
- Fazer deploy.
- Publicar pacotes.

O agente deve permanecer restrito ao PIP-YuukoLane e aos ambientes de desenvolvimento e testes necessários.

Preferir ambientes virtuais Python para evitar interferência nas dependências globais da VPS.

---

8. Git

O agente pode:

- Consultar o estado do Git.
- Consultar o histórico.
- Comparar alterações.
- Inspecionar diffs.
- Identificar arquivos não rastreados.

O agente não deve:

- Executar "git push".
- Fazer deploy.
- Publicar releases.
- Alterar branches remotas.
- Forçar alterações no repositório remoto.

Commits são responsabilidade do usuário, salvo autorização explícita na tarefa.

Nunca executar "git push --force" ou comandos equivalentes.

---

9. Implementação

Priorize:

- Código Python simples e legível.
- Separação de responsabilidades.
- Validação adequada.
- Tratamento consistente de exceções.
- Tipagem quando aplicável.
- Reutilização de módulos existentes.
- Compatibilidade com a arquitetura documentada.
- Preservação das interfaces públicas.
- Compatibilidade com as versões de Python declaradas no projeto.
- Dependências mínimas e justificadas.

Não reescreva grandes partes do projeto apenas por preferência estética.

Não modifique APIs públicas desnecessariamente.

Não altere a organização do pacote sem justificativa técnica.

Evite alterações fora do escopo.

---

10. Testes

Toda funcionalidade implementada deve possuir testes apropriados quando a arquitetura permitir.

Antes de considerar uma tarefa concluída:

1. Identifique o framework de testes utilizado.
2. Execute os testes relevantes.
3. Corrija falhas relacionadas à implementação.
4. Execute novamente os testes.
5. Verifique regressões relevantes.
6. Registre os resultados.

Quando aplicável, valide também:

- Importação dos módulos.
- Compatibilidade das interfaces públicas.
- Dependências declaradas.
- Construção do pacote.
- Conteúdo dos artefatos de distribuição.
- Instalação local em ambiente isolado.

Não presuma que "pytest" ou outras ferramentas estejam configuradas sem verificar.

Nunca altere um teste apenas para fazê-lo passar sem confirmar o comportamento esperado.

Se os testes não puderem ser executados, registre o bloqueio.

---

11. Falhas

Se ocorrer um erro:

1. Identifique a causa.
2. Tente uma correção fundamentada.
3. Execute novamente os testes.
4. Se necessário, faça uma segunda tentativa.
5. Se necessário, faça uma terceira tentativa.

Após três tentativas sem solução clara, interrompa a parte afetada da tarefa.

Não entre em ciclos indefinidos.

Registre o problema em ".codex/interventions.md".

---

12. Checkpoints

O agente deve manter ".codex/checkpoint.md" atualizado.

O checkpoint deve indicar:

- Estado atual.
- Última tarefa executada.
- O que foi concluído.
- O que está em andamento.
- Próximo passo.
- Bloqueios.
- Testes executados.
- Data da última atualização.

O checkpoint deve ser atualizado antes de finalizar uma tarefa ou interromper uma execução relevante.

---

13. Registro de alterações

O agente deve atualizar ".codex/what_i_did.md" ao concluir uma etapa significativa.

Registrar:

- Data.
- Tarefa.
- Arquivos criados.
- Arquivos alterados.
- Principais funções, classes e módulos criados ou modificados.
- Testes executados.
- Resultado dos testes.
- Observações relevantes.

O registro deve ser objetivo.

---

14. Intervenções humanas

Quando uma decisão depender do usuário, registrar em ".codex/interventions.md".

Cada intervenção deve informar:

- Data.
- Problema.
- Contexto.
- Impacto.
- Decisão necessária.
- Status.

Não continue implementando decisões de produto que dependem do usuário apenas assumindo uma resposta.

---

15. Controle de escopo

Uma tarefa deve permanecer dentro do escopo definido em ".codex/task.md", quando existir.

Se for identificada uma melhoria fora do escopo:

- Não implemente automaticamente.
- Registre a sugestão.
- Continue somente com o escopo atual.

---

16. Conclusão de tarefa

Uma tarefa somente pode ser considerada concluída quando:

- O código necessário foi implementado.
- O comportamento corresponde à documentação.
- As interfaces públicas relevantes foram preservadas ou as mudanças foram autorizadas.
- Os testes relevantes foram executados.
- Os testes passaram ou os bloqueios foram registrados.
- O empacotamento foi validado quando aplicável.
- O checkpoint foi atualizado.
- "what_i_did.md" foi atualizado.
- Não existem decisões pendentes ocultas.

"Codifiquei" não significa "concluído".

"Testado e validado" é o critério de conclusão.

---

17. Autonomia

O agente possui autonomia para implementar e testar código dentro dos limites definidos neste arquivo.

O usuário mantém controle sobre:

- Arquitetura final.
- Decisões de produto.
- Git.
- Publicação no PyPI.
- Releases.
- Deploy.
- Produção.
- Infraestrutura.
- Alterações irreversíveis.

Na dúvida entre autonomia e segurança, prefira interromper a operação que exige autorização e solicitar intervenção.
