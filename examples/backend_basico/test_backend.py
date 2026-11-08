import asyncio
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import httpx

from yuukolane.yuukolane_transpiler import converter


SOURCE = Path(__file__).with_name("main.yl")
NAMESPACE = {"__name__": "yuukolane_backend_example"}
with patch.dict(os.environ, {"YUUKOLANE_BACKEND_DB": ":memory:"}):
    exec(converter(SOURCE.read_text(encoding="utf-8")), NAMESPACE)
APP = NAMESPACE["app"]


class BackendApiTests(unittest.TestCase):
    def setUp(self):
        NAMESPACE["_banco"].execute("DELETE FROM itens")
        NAMESPACE["_banco"].commit()

    def test_crud_endpoints(self):
        async def exercise_api():
            transport = httpx.ASGITransport(app=APP)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://yuukolane.test",
            ) as client:
                created = await client.post(
                    "/itens",
                    json={"id": 7, "nome": "Caderno", "descricao": "Azul"},
                )
                self.assertEqual(created.status_code, 201)
                self.assertEqual(created.json()["nome"], "Caderno")

                collection = await client.get("/itens")
                self.assertEqual(collection.status_code, 200)
                self.assertEqual(len(collection.json()), 1)

                fetched = await client.get("/itens/7")
                self.assertEqual(fetched.json()["descricao"], "Azul")

                updated = await client.put(
                    "/itens/7",
                    json={"id": 7, "nome": "Caderno novo", "descricao": "Verde"},
                )
                self.assertEqual(updated.json()["nome"], "Caderno novo")

                deleted = await client.delete("/itens/7")
                self.assertEqual(deleted.json(), {"removido": True})

                missing = await client.get("/itens/7")
                self.assertEqual(missing.status_code, 404)

        asyncio.run(exercise_api())

    def test_sqlite_data_survives_application_reinitialization(self):
        async def exercise_persistence(database_path):
            with patch.dict(os.environ, {"YUUKOLANE_BACKEND_DB": database_path}):
                first_namespace = {"__name__": "yuukolane_backend_first"}
                exec(converter(SOURCE.read_text(encoding="utf-8")), first_namespace)
                first_app = first_namespace["app"]

                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=first_app),
                    base_url="http://yuukolane.test",
                ) as client:
                    created = await client.post(
                        "/itens",
                        json={"id": 9, "nome": "Persistente", "descricao": "SQLite"},
                    )
                    self.assertEqual(created.status_code, 201)

                second_namespace = {"__name__": "yuukolane_backend_second"}
                exec(converter(SOURCE.read_text(encoding="utf-8")), second_namespace)
                second_app = second_namespace["app"]
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=second_app),
                    base_url="http://yuukolane.test",
                ) as client:
                    fetched = await client.get("/itens/9")
                    self.assertEqual(fetched.status_code, 200)
                    self.assertEqual(fetched.json()["nome"], "Persistente")

                first_namespace["_banco"].close()
                second_namespace["_banco"].close()

        with TemporaryDirectory() as directory:
            database_path = str(Path(directory) / "teste.db")
            asyncio.run(exercise_persistence(database_path))


if __name__ == "__main__":
    unittest.main()
