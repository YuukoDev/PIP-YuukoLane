import unittest

from yuukolane.validador import validar_codigo


class ValidatorTests(unittest.TestCase):
    def test_accepts_valid_function_return_and_async_await(self):
        code = """def calcular():
    return 1

async def buscar():
    await operacao()
"""
        self.assertTrue(validar_codigo(code))

    def test_rejects_assignment_to_reserved_literal(self):
        with self.assertRaisesRegex(SyntaxError, "YK101"):
            validar_codigo("verdadeiro = 1")

    def test_rejects_assignment_to_reserved_identifier(self):
        with self.assertRaisesRegex(SyntaxError, "YK102"):
            validar_codigo("mostrar = 1")

    def test_rejects_return_outside_function(self):
        with self.assertRaisesRegex(SyntaxError, "YK201"):
            validar_codigo("retornar 1")

    def test_rejects_await_outside_async_function(self):
        with self.assertRaisesRegex(SyntaxError, "YK202"):
            validar_codigo("await operacao()")

    def test_rejects_await_in_sync_function_nested_in_async_function(self):
        code = """async def externa():
    def interna():
        await operacao()
"""
        with self.assertRaisesRegex(SyntaxError, "YK202"):
            validar_codigo(code)

    def test_rejects_return_directly_in_class_body_inside_function(self):
        code = """def externa():
    class Interna:
        return 1
"""
        with self.assertRaisesRegex(SyntaxError, "YK201"):
            validar_codigo(code)


if __name__ == "__main__":
    unittest.main()
