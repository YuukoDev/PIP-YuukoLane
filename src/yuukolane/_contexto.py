"""Contexto lexical para nomes que também aparecem no dicionário."""

import tokenize


_ABRE = {"(", "[", "{"}
_FECHA = {")", "]", "}"}
_DECLARACOES = {"def", "definir", "funcao", "class", "classe"}
_CLASSES = {"class", "classe"}


class _Escopo:
    def __init__(self, pai=None, classe=False):
        self.pai = pai
        self.classe = classe
        self.nomes = set()

    def vincula(self, nome):
        escopo = self
        while escopo is not None:
            if nome in escopo.nomes:
                return True
            escopo = escopo.pai
        return False


def _cabecalho(partes, tokens):
    """Localiza os parâmetros e o fim do cabeçalho, inclusive em várias linhas."""
    declaracao = 1 if tokens[partes[0]].string == "async" else 0
    if len(partes) <= declaracao + 1:
        return None
    tipo = tokens[partes[declaracao]].string
    nome = partes[declaracao + 1]
    if tipo not in _DECLARACOES or tokens[nome].type != tokenize.NAME:
        return None
    parametros = []
    profundidade = 0
    assinatura = False
    espera_parametro = False
    for pos in range(declaracao + 2, len(partes)):
        indice = partes[pos]
        token = tokens[indice]
        termo = token.string
        if termo == ":" and profundidade == 0:
            return tipo, nome, parametros, pos
        if pos == declaracao + 2 and termo == "(" and tipo not in _CLASSES:
            assinatura = espera_parametro = True
        elif assinatura and profundidade == 1:
            if espera_parametro and token.type == tokenize.NAME:
                parametros.append(indice)
            if termo not in {"*", "**"}:
                espera_parametro = termo == ","
        if termo in _ABRE:
            profundidade += 1
        elif termo in _FECHA:
            profundidade -= 1
            if profundidade == 0:
                assinatura = False
    return None


def analisar_identificadores(tokens):
    """Retorna posições literais e escopos das referências em cada instrução."""
    raiz = _Escopo()
    blocos = [raiz]
    escopos = {}
    literais = set()
    pendente = None
    partes = []

    def instrucao(indices, escopo):
        if not indices:
            return
        termos = [tokens[i].string for i in indices]
        importacao = termos[0] in {"import", "from"}
        profundidade = 0
        for pos, indice in enumerate(indices):
            escopos[indice] = escopo
            token = tokens[indice]
            termo = token.string
            anterior = termos[pos - 1] if pos else ""
            seguinte = termos[pos + 1] if pos + 1 < len(termos) else ""
            if token.type == tokenize.NAME:
                if anterior == "." or importacao:
                    literais.add(indice)
                if anterior == "as":
                    literais.add(indice)
                    escopo.nomes.add(termo)
                if seguinte == "=" and profundidade and anterior in {"(", ","}:
                    literais.add(indice)
                if pos == 0 and seguinte in {"=", "atribuir"}:
                    # Keep simple assignment targets intact for YK101/YK102.
                    literais.add(indice)
            if termo in _ABRE:
                profundidade += 1
            elif termo in _FECHA:
                profundidade -= 1

        if importacao:
            inicio = termos.index("import") + 1 if "import" in termos else len(termos)
            for grupo in " ".join(termos[inicio:]).split(","):
                nomes = grupo.replace("(", "").replace(")", "").split()
                if nomes and "as" not in nomes and nomes[0].isidentifier():
                    escopo.nomes.add(nomes[0])

    for indice, token in enumerate(tokens):
        if token.type == tokenize.INDENT:
            blocos.append(pendente or blocos[-1])
            pendente = None
        elif token.type == tokenize.DEDENT:
            blocos.pop()
        elif token.type in {tokenize.NL, tokenize.COMMENT}:
            continue
        elif token.type in {tokenize.NEWLINE, tokenize.ENDMARKER}:
            if not partes:
                continue
            escopo = blocos[-1]
            pendente = None
            cabecalho = _cabecalho(partes, tokens)
            if cabecalho is None:
                instrucao(partes, escopo)
            else:
                tipo, nome, parametros, fim = cabecalho
                literais.update([nome, *parametros])
                escopo.nomes.add(tokens[nome].string)
                instrucao(partes[:fim + 1], escopo)
                pai = escopo.pai if escopo.classe else escopo
                interno = _Escopo(pai, classe=tipo in _CLASSES)
                interno.nomes.update(tokens[i].string for i in parametros)
                if fim + 1 == len(partes):
                    pendente = interno
                else:
                    instrucao(partes[fim + 1:], interno)
            partes = []
        else:
            partes.append(indice)

    return literais, escopos
