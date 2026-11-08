import unittest
from contextlib import redirect_stdout
from io import StringIO

from yuukolane.yuukolane_transpiler import DIC, converter, traduzir_termos


class ConverterTests(unittest.TestCase):
    def test_every_dictionary_term_has_its_declared_translation(self):
        for categoria, pares in DIC.items():
            for termo, traducao in pares.items():
                with self.subTest(categoria=categoria, termo=termo):
                    if termo == "somar" and categoria == "funcoes_comuns":
                        self.assertEqual(traduzir_termos("somar(valores)"), "sum(valores)")
                    elif termo == "somar" and categoria == "operadores":
                        self.assertEqual(traduzir_termos("a somar b"), "a + b")
                    else:
                        self.assertEqual(traduzir_termos(termo), traducao)

    def test_translates_core_keywords_and_values(self):
        source = """se ativo:
    mostrar verdadeiro
senao:
    mostrar nulo
"""

        self.assertEqual(
            converter(source),
            """if ativo:
    print(True)
else:
    print(None)
""",
        )

    def test_translates_composed_operators_and_comparison_assignment(self):
        source = "se idade maior ou igual 18:\n    mostrar idade\n"

        self.assertEqual(
            converter(source),
            "if idade >= 18:\n    print(idade)\n",
        )

    def test_translates_functions_loops_and_return(self):
        source = """definir dobro(valor):
    retornar valor multiplicar 2

para item em intervalo(3):
    mostrar item
"""

        self.assertEqual(
            converter(source),
            """def dobro(valor):
    return valor * 2

for item in range(3):
    print(item)
""",
        )

    def test_preserves_language_words_inside_strings_and_comments(self):
        source = 'mostrar "se e verdadeiro" # senao\n'

        self.assertEqual(converter(source), 'print("se e verdadeiro") # senao\n')

    def test_interpolates_braced_values_in_mostrar(self):
        self.assertEqual(converter('mostrar "Olá {nome}"\n'), 'print(f"Olá {nome}")\n')

    def test_preserves_existing_python_f_string_prefix(self):
        self.assertEqual(converter('mostrar f"Olá {nome}"\n'), 'print(f"Olá {nome}")\n')

    def test_does_not_translate_identifiers_containing_language_words(self):
        source = 'senao_separado = "se"\nmostrar senao_separado\n'
        expected = 'senao_separado = "se"\nprint(senao_separado)\n'
        self.assertEqual(converter(source), expected)

    def test_mostrar_accepts_an_expression_without_parentheses(self):
        self.assertEqual(converter("mostrar resultado\n"), "print(resultado)\n")

    def test_mostrar_wraps_the_complete_string_expression(self):
        self.assertEqual(converter('mostrar "Olá, " somar nome\n'), 'print("Olá, " + nome)\n')

    def test_converted_program_is_valid_python_and_runs(self):
        source = """definir soma(a, b):
    retornar a somar b

mostrar soma(2, 3)
"""
        generated = converter(source)
        compile(generated, "<yuukolane>", "exec")
        namespace = {}
        with redirect_stdout(StringIO()):
            exec(generated, namespace)
        self.assertEqual(namespace["soma"](2, 3), 5)

    def test_somar_function_call_remains_an_aggregate_function(self):
        self.assertEqual(converter("resultado = somar([1, 2, 3])\n"), "resultado = sum([1, 2, 3])\n")

    def test_translates_multiword_empty_values(self):
        source = """a = lista vazia
b = dicionario vazio
c = texto vazio
d = conjunto vazio
par_resultado = tupla vazia
"""
        expected = """a = []
b = {}
c = ''
d = set()
par_resultado = ()
"""
        self.assertEqual(converter(source), expected)

    def test_translates_exception_blocks(self):
        source = """tentar:
    lancar ValueError("falha")
capturar ValueError:
    vazio
finalmente:
    vazio
"""
        generated = converter(source)
        self.assertEqual(
            generated,
            """try:
    raise ValueError("falha")
except ValueError:
    pass
finally:
    pass
""",
        )
        compile(generated, "<yuukolane>", "exec")

    def test_translates_async_functions_and_await(self):
        source = """async definir buscar():
    esperar operacao()
"""
        generated = converter(source)
        self.assertEqual(generated, """async def buscar():
    await operacao()
""")
        compile(generated, "<yuukolane>", "exec")

    def test_translates_logical_operators_and_types(self):
        source = """definir validar(valor: inteiro) -> booleano:
    retornar valor maior 0 e nao falso
"""
        generated = converter(source)
        self.assertEqual(
            generated,
            """def validar(valor: int) -> bool:
    return valor > 0 and not False
""",
        )
        compile(generated, "<yuukolane>", "exec")

    def test_rejects_return_outside_function_after_translation(self):
        with self.assertRaisesRegex(SyntaxError, "YK201"):
            converter("retornar 1")

    def test_rejects_invalid_generated_python_syntax(self):
        with self.assertRaises(SyntaxError):
            converter("resultado =\n")


if __name__ == "__main__":
    unittest.main()
