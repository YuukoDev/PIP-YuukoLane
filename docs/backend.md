# Backend web de exemplo

O repositório contém um backend CRUD de demonstração em [examples/backend_basico/](../examples/backend_basico/). Ele usa FastAPI, Pydantic e SQLite por meio da interoperabilidade Python.

O exemplo demonstra:

- rotas GET, POST, PUT e DELETE;
- modelos Pydantic e anotações Python;
- tratamento de erros HTTP;
- persistência SQLite;
- tradução de funções, classes, condições, exceções, valores e list comprehensions;
- teste das rotas usando HTTPX/ASGI sem abrir uma porta de rede.

FastAPI, HTTPX e Uvicorn são dependências opcionais desse exemplo; não são dependências do pacote YuukoLane.

Consulte o [README do exemplo](../examples/backend_basico/README.md) para instalar dependências, transpilar e executar.

O exemplo é didático. Antes de produção, reveja configuração do banco, concorrência, migrações, autenticação, secrets, logs, observabilidade e implantação.
