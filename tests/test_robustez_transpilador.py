import concurrent.futures
import subprocess
import sys
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
        class Externo:
            def adicionar(self, valor):
                return valor + 1

        contexto = {"obj": Externo()}
        exec(converter("resultado = obj.adicionar(1)\n"), contexto)
        self.assertEqual(contexto["resultado"], 2)

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
mostrar f"{obj.tipo()}" # palavra reservar
"""
        self.assertEqual(
            converter(codigo),
            """print('{"id": 1}')
print(r"{nome}")
print(f"{obj.tipo()}") # palavra reservar
""",
        )

    def test_alias_funciona_com_parametros_e_receptor_avaliado_uma_vez(self):
        codigo = """eventos = []
definir obter():
    eventos.adicionar("chamada")
    retornar []
definir preencher(alvo):
    acao = alvo.adicionar
    acao(42)
    retornar alvo
resultado = preencher(obter())
"""
        contexto = {}
        exec(converter(codigo), contexto)
        self.assertEqual(contexto["resultado"], [42])
        self.assertEqual(contexto["eventos"], ["chamada"])

    def test_atributo_proprio_tem_prioridade_em_subclasse(self):
        codigo = """classe Colecao(list):
    definir adicionar(self, valor):
        retornar valor + 1
alvo = Colecao()
resultado = alvo.adicionar(4)
"""
        contexto = {}
        exec(converter(codigo), contexto)
        self.assertEqual(contexto["resultado"], 5)
        self.assertEqual(contexto["alvo"], [])

    def test_alias_nao_aplica_em_objeto_externo_com_metodo_ingles(self):
        class Externo:
            def append(self, valor):
                raise AssertionError("append externo")

        with self.assertRaisesRegex(AttributeError, "adicionar"):
            exec(converter("obj.adicionar(1)"), {"obj": Externo()})

    def test_alias_nao_oculta_attribute_error_de_atributo_proprio(self):
        class Colecao(list):
            @property
            def adicionar(self):
                raise AttributeError("falha da propriedade")

        with self.assertRaisesRegex(AttributeError, "falha da propriedade"):
            exec(converter("obj.adicionar(1)"), {"obj": Colecao()})

    def test_alias_preserva_atribuicao_remocao_e_fstrings(self):
        codigo = """classe Externo:
    vazio
obj = Externo()
obj.copiar = 42
valor = f"{obj.copiar}"
del obj.copiar
nome = "acentuação"; resultado = ({"chave": 1}).copiar().copiar()
"""
        contexto = {}
        exec(converter(codigo), contexto)
        self.assertEqual(contexto["valor"], "42")
        self.assertFalse(hasattr(contexto["obj"], "copiar"))
        self.assertEqual(contexto["resultado"], {"chave": 1})

    def test_python_gerado_roda_sem_importar_o_pacote(self):
        codigo = "itens = []\nitens.adicionar(7)\nmostrar itens\n"
        resultado = subprocess.run(
            [sys.executable, "-I", "-c", converter(codigo)],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(resultado.stdout, "[7]\n")

    def test_alias_preserva_anotacoes_postergadas(self):
        codigo = """from __future__ import annotations
definir f(x: obj.copiar):
    retornar x
itens = [].copiar()
"""
        contexto = {}
        exec(converter(codigo), contexto)
        self.assertEqual(contexto["f"].__annotations__["x"], "obj.copiar")

    def test_alias_preserva_docstring_e_future_import(self):
        codigo = '"""Módulo"""\nfrom __future__ import annotations; resultado = [1].contar(1)'
        contexto = {}
        exec(converter(codigo), contexto)
        self.assertEqual(contexto["__doc__"], "Módulo")
        self.assertEqual(contexto["resultado"], 1)

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
