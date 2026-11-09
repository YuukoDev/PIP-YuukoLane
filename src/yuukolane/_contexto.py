"""Contexto lexical para nomes que também aparecem no dicionário."""

import ast
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


def _nomes_alvo(indices, tokens):
    """Find only names bound by an assignment target, excluding attribute/index loads."""
    colunas = {}
    coluna = 0
    partes = []
    for indice in indices:
        termo = tokens[indice].string
        colunas[coluna] = indice
        coluna += len(termo.encode("utf-8")) + 1
        partes.append(termo)
    try:
        alvo = ast.parse(" ".join(partes) + " = None").body[0].targets[0]
    except (SyntaxError, IndexError, AttributeError):
        return []
    return [
        colunas[no.col_offset]
        for no in ast.walk(alvo)
        if isinstance(no, ast.Name) and isinstance(no.ctx, ast.Store)
    ]


def _grupos(indices, tokens):
    """Collect the direct children of each bracket pair and the statement root."""
    pilha = [[]]
    grupos = []
    for indice in indices:
        termo = tokens[indice].string
        if termo in _ABRE:
            pilha[-1].append(indice)
            pilha.append([indice])
        elif termo in _FECHA and len(pilha) > 1:
            grupo = pilha.pop()
            grupos.append((grupo, indice))
            pilha[-1].append(indice)
        else:
            pilha[-1].append(indice)
    return pilha[0], reversed(grupos)


def analisar_identificadores(tokens, aliases):
    """Retorna posições literais e escopos das referências em cada instrução."""
    raiz = _Escopo()
    blocos = [raiz]
    escopos = {}
    literais = set()
    pendente = None
    partes = []

    def vincular(alvo, escopo):
        for indice in _nomes_alvo(alvo, tokens):
            termo = tokens[indice].string
            if termo in aliases:
                literais.add(indice)
                escopo.nomes.add(termo)

    def alvos(indices, termos, escopo, completos):
        def trecho(inicio, fim):
            return [i for i in completos if inicio <= i < fim]
        inicio = 1 if termos[0] == "async" else 0
        if termos[inicio:inicio + 1] in (["for"], ["para"]):
            for pos in range(inicio + 1, len(termos)):
                if termos[pos] in {"in", "em"}:
                    vincular(trecho(indices[inicio] + 1, indices[pos]), escopo)
                    break
        elif termos[0] not in _DECLARACOES and termos[0] not in {
            "if", "se", "elif", "senao", "while", "enquanto", "async", "lambda",
        }:
            inicio = 0
            for pos, termo in enumerate(termos):
                if termo in {":", ";"}:
                    break
                if termo in {"=", "atribuir"}:
                    alvo = trecho(indices[inicio], indices[pos]) if inicio < pos else []
                    if len(alvo) > 1:
                        vincular(alvo, escopo)
                    inicio = pos + 1

    def compreensao(diretos, fim, completos):
        termos = [tokens[i].string for i in diretos]
        clausulas = [p for p, termo in enumerate(termos) if termo in {"for", "para"}]
        if not clausulas:
            return
        externos = escopos[diretos[0]]
        local = _Escopo(externos.pai if externos.classe else externos)
        intervalos = []
        for pos, limite in zip(clausulas, clausulas[1:] + [len(termos)]):
            separador = next((i for i in range(pos + 1, limite)
                              if termos[i] in {"in", "em"}), None)
            if separador is None or separador + 1 == limite:
                return
            intervalos.append((pos, separador, limite))
        pos, separador, limite = intervalos[0]
        filtro = next((i for i in range(separador + 1, limite)
                       if termos[i] in {"if", "se"}), limite)
        if filtro == limite and limite < len(termos) and termos[limite - 1] == "async":
            filtro -= 1
        inicio_iteravel = diretos[separador] + 1
        fim_iteravel = diretos[filtro] if filtro < len(diretos) else fim
        for indice in range(diretos[0] + 1, fim):
            if indice in escopos and not inicio_iteravel <= indice < fim_iteravel:
                escopos[indice] = local
        for pos, separador, _ in intervalos:
            vincular([i for i in completos if diretos[pos] < i < diretos[separador]], local)

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

        raiz_instrucao, grupos = _grupos(indices, tokens)
        inicio = 0
        for pos, indice in enumerate(raiz_instrucao):
            if tokens[indice].string == ";":
                trecho = raiz_instrucao[inicio:pos]
                if trecho:
                    alvos(trecho, [tokens[i].string for i in trecho], escopo, indices)
                inicio = pos + 1
        trecho = raiz_instrucao[inicio:]
        if trecho:
            alvos(trecho, [tokens[i].string for i in trecho], escopo, indices)
        for diretos, fim in grupos:
            compreensao(diretos, fim, indices)

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
