# Backend básico com YuukoLane e FastAPI

Este exemplo demonstra uma API REST pequena escrita em sintaxe YuukoLane e executada pelo runtime Python através do FastAPI. Ele implementa rotas CRUD e persiste os dados em SQLite. É uma demonstração de integração, não uma configuração pronta para produção.

## Executar a partir do checkout

Instale as dependências opcionais do exemplo:

```bash
python3 -m pip install -r requirements.txt
```

Gere Python e inicie o servidor:

```bash
PYTHONPATH=../../src python3 -m yuukolane.cli main.yl --so-transpilar > main.py
uvicorn main:app --reload
```

Abra `http://127.0.0.1:8000/docs` para a interface interativa do FastAPI.

Por padrão, o banco `backend.db` é criado no diretório atual. Configure `YUUKOLANE_BACKEND_DB` para escolher outro caminho.

## Executar o teste das rotas

```bash
PYTHONPATH=../../src python3 -m unittest -v test_backend
```

O teste usa HTTPX com o transporte ASGI local, sem abrir porta de rede.
