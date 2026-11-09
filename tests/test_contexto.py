import unittest

from yuukolane.yuukolane_transpiler import converter


class ContextoTests(unittest.TestCase):
    def executar(self, codigo):
        namespace = {}
        exec(converter(codigo), namespace)
        return namespace

    def test_laco_e_desempacotamento_preservam_aliases_no_escopo(self):
        namespace = self.executar("""definir calcular():
    para (lista, *ordenar) em [(10, 20, 30)]:
        primeiro = lista
    texto, (tamanho, outro) = (1, (2, 3))
    retornar primeiro, ordenar, texto, tamanho, outro
resultado = calcular()
fora = tamanho([1, 2, 3])
""")
        self.assertEqual(namespace["resultado"], (10, [20, 30], 1, 2, 3))
        self.assertEqual(namespace["fora"], 3)

    def test_alvos_indexados_e_atributos_nao_vinculam_receptores(self):
        namespace = self.executar("""class Caixa:
    pass
caixa = Caixa()
dados = [0]
caixa.tamanho, dados[tamanho([])] = (1, 2)
resultado = (caixa.tamanho, dados[0], tamanho(dados))
""")
        self.assertEqual(namespace["resultado"], (1, 2, 1))

    def test_compreensoes_nao_vazam_aliases_e_iteravel_externo(self):
        namespace = self.executar("""resultado = [lista para lista em lista((1, 2))]
pares = [(lista, tamanho) para lista em resultado para tamanho em [lista + 1] se tamanho > 1]
mapa = {texto: tamanho para (texto, tamanho) em pares}
fora = tamanho(resultado)
""")
        self.assertEqual(namespace["resultado"], [1, 2])
        self.assertEqual(namespace["pares"], [(1, 2), (2, 3)])
        self.assertEqual(namespace["mapa"], {1: 2, 2: 3})
        self.assertEqual(namespace["fora"], 2)
        self.assertNotIn("lista", namespace)

    def test_compreensao_aninhada_e_gerador_em_chamada(self):
        namespace = self.executar("""resultado = [[lista para lista em [lista + 1]] para lista em [1, 2]]
total = somar(tamanho para tamanho em [1, 2])
""")
        self.assertEqual(namespace["resultado"], [[2], [3]])
        self.assertEqual(namespace["total"], 3)

    def test_comparacao_em_grupos_preserva_argumentos_nomeados_e_lambda(self):
        namespace = self.executar("""definir verificar(valor):
    retornar valor
x = 1
se (
    ((x = verificar(valor=1))) e ((lambda valor=2: valor)() = 2)
):
    x = 2
enquanto (x = 2):
    x = 3
""")
        self.assertEqual(namespace["x"], 3)
