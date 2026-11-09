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

    def test_conversoes_concorrentes_nao_misturam_strings(self):
        codigos = ['mostrar "texto %d"\n' % n for n in range(80)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            resultados = list(executor.map(converter, codigos))
        for indice, resultado in enumerate(resultados):
            self.assertEqual(resultado, 'print("texto %d")\n' % indice)


if __name__ == "__main__":
    unittest.main()
