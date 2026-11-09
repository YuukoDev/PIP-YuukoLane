import concurrent.futures
import unittest

from yuukolane.yuukolane_transpiler import converter


class RobustezTranspiladorTests(unittest.TestCase):
    def test_placeholder_literal_nao_e_substituido(self):
        codigo = 'nome = "__STR_0__"\nmostrar nome\n'
        resultado = converter(codigo)
        self.assertIn('"__STR_0__"', resultado)

    def test_strings_e_comentarios_sao_preservados(self):
        codigo = '# se verdadeiro\nmostrar "se verdadeiro"\n'
        resultado = converter(codigo)
        self.assertIn('# se verdadeiro', resultado)
        self.assertIn('print("se verdadeiro")', resultado)

    def test_comparacao_simples(self):
        self.assertIn('if numero == 1:', converter('se numero = 1:\n    vazio\n'))

    def test_argumento_nomeado_em_condicional(self):
        codigo = 'se verificar(valor=1):\n    vazio\n'
        self.assertIn('if verificar(valor=1):', converter(codigo))

    def test_nome_de_funcao_definida_nao_e_traduzido(self):
        codigo = 'definir adicionar(valor):\n    retornar valor\nmostrar adicionar(2)\n'
        resultado = converter(codigo)
        self.assertIn('def adicionar(valor):', resultado)
        self.assertIn('print(adicionar(2))', resultado)

    def test_nome_de_classe_definida_nao_e_traduzido(self):
        codigo = 'classe ordenar:\n    vazio\n'
        self.assertIn('class ordenar:', converter(codigo))

    def test_atributo_nao_e_traduzido(self):
        codigo = 'obj.adicionar(1)\n'
        self.assertEqual(converter(codigo), codigo)

    def test_chaves_literais_nao_viram_interpolacao(self):
        codigo = 'mostrar "JSON: {{valor}}"\n'
        self.assertEqual(converter(codigo), 'print("JSON: {{valor}}")\n')

    def test_interpolacao_nome_simples_continua_funcionando(self):
        self.assertEqual(converter('mostrar "Olá {nome}"\n'), 'print(f"Olá {nome}")\n')

    def test_atributo_nao_desativa_alias_no_mesmo_arquivo(self):
        codigo = "obj.tipo()\nresultado = tipo(42)\n"
        self.assertEqual(converter(codigo), "obj.tipo()\nresultado = type(42)\n")

    def test_metodos_documentados_de_lista_e_metodos_proprios(self):
        codigo = """classe Colecao:
    definir adicionar(self, valor):
        retornar valor
nomes = ["Ivo"]
nomes.adicionar("Ana")
nomes.ordenar()
propria = Colecao()
resultado = propria.adicionar(3)
"""
        contexto = {}
        exec(converter(codigo), contexto)
        self.assertEqual(contexto["nomes"], ["Ana", "Ivo"])
        self.assertEqual(contexto["resultado"], 3)

    def test_parametros_e_argumentos_nomeados_preservam_somente_seu_contexto(self):
        codigo = """definir externa(
    tamanho: inteiro = tamanho([]),
    /,
    *lista,
    texto: texto = "ok",
    **copiar,
):
    definir interna():
        retornar tamanho, lista, texto, copiar
    retornar interna()
resultado = externa(2, 3, texto="sim", copiar=4)
global_len = tamanho([1])
"""
        python = converter(codigo)
        self.assertIn("texto: str", python)
        contexto = {}
        exec(python, contexto)
        self.assertEqual(contexto["resultado"], (2, (3,), "sim", {"copiar": 4}))
        self.assertEqual(contexto["global_len"], 1)

    def test_importacao_preserva_nome_e_alias(self):
        codigo = "from modulo import ordenar as copiar\nresultado = copiar()\n"
        self.assertEqual(converter(codigo), codigo)

    def test_metodo_nao_herda_nomes_do_escopo_da_classe(self):
        codigo = """classe Colecao:
    definir tamanho(self):
        retornar 0
    definir contar(self):
        retornar tamanho([1, 2])
resultado = Colecao().contar()
"""
        contexto = {}
        exec(converter(codigo), contexto)
        self.assertEqual(contexto["resultado"], 2)

    def test_somar_antes_de_parenteses_distingue_operador_e_funcao(self):
        codigo = "a = 1 somar (2 somar 3)\nb = somar([a, 4])\n"
        contexto = {}
        exec(converter(codigo), contexto)
        self.assertEqual((contexto["a"], contexto["b"]), (6, 10))

    def test_interpolacao_preserva_formatos_expressoes_e_chaves_escapadas(self):
        codigo = """valor = 3
mostrar "{{total}} {valor + 1:03d}"
"""
        self.assertIn('print(f"{{total}} {valor + 1:03d}")', converter(codigo))

    def test_interpolacao_preserva_json_e_prefixos_explicitos(self):
        codigo = """mostrar '{"id": 1}'
mostrar r"{nome}"
mostrar f"{obj.ordenar()}" # palavra reservar
"""
        self.assertEqual(
            converter(codigo),
            """print('{"id": 1}')
print(r"{nome}")
print(f"{obj.ordenar()}") # palavra reservar
""",
        )

    def test_interpolacao_em_string_multilinha_preserva_as_linhas(self):
        codigo = 'mostrar """Olá\n{nome}""" # fim\nmostrar 42\n'
        self.assertEqual(converter(codigo), 'print(f"""Olá\n{nome}""") # fim\nprint(42)\n')

    def test_condicional_multilinha_preserva_keyword_argument(self):
        codigo = "se verificar(\n    valor=1,\n) = verdadeiro:\n    vazio\n"
        self.assertEqual(converter(codigo), "if verificar(\n    valor=1,\n) == True:\n    pass\n")

    def test_diagnostico_mantem_linha_original_apos_string_multilinha(self):
        codigo = 'texto_longo = """x\ny"""\nretornar 1\n'
        with self.assertRaisesRegex(SyntaxError, "YK201") as erro:
            converter(codigo, filename="principal.yl")
        self.assertEqual(erro.exception.filename, "principal.yl")
        self.assertEqual(erro.exception.lineno, 3)
        self.assertEqual(erro.exception.text, "retornar 1\n")

    def test_diagnostico_inclui_arquivo_em_falha_de_tokenizacao(self):
        with self.assertRaises(SyntaxError) as erro:
            converter("mostrar (42\n", filename="quebrado.yl")
        self.assertEqual(erro.exception.filename, "quebrado.yl")
        self.assertEqual(erro.exception.lineno, 1)
        self.assertEqual(erro.exception.text, "mostrar (42\n")

    def test_conversoes_concorrentes_nao_misturam_strings(self):
        codigos = ['mostrar "texto %d"\n' % n for n in range(80)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            resultados = list(executor.map(converter, codigos))
        for indice, resultado in enumerate(resultados):
            self.assertEqual(resultado, 'print("texto %d")\n' % indice)


if __name__ == "__main__":
    unittest.main()
