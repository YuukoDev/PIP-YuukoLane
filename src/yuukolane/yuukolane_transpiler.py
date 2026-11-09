# yuukolane_transpiler.py
import ast
import keyword
import os
import io
import json
import re
import sys
import tokenize
import uuid
from pathlib import Path
from ._contexto import analisar_identificadores
from .validador import validar_codigo

# Caminho absoluto do dicionario.json relativo a este arquivo:
caminho_atual = os.path.dirname(__file__)
caminho_dicionario = os.path.join(caminho_atual, "dicionario.json")

with open(caminho_dicionario, encoding="utf-8") as f:
    DIC = json.load(f)

# ── tokens temporários ──────────────────────────────────────────────────────
def _new_state(source):
    prefix = "__YK_" + uuid.uuid4().hex + "_"
    while prefix in source:
        prefix = "__YK_" + uuid.uuid4().hex + "_"
    return {"strings": {}, "comments": {}, "prefix": prefix}

def _offsets(codigo):
    inicios = [0]
    for linha in codigo.split("\n"):
        inicios.append(inicios[-1] + len(linha) + 1)

    def offset(posicao):
        linha, coluna = posicao
        return inicios[min(linha - 1, len(inicios) - 1)] + coluna

    return offset


def _substituir(codigo, edicoes):
    for inicio, fim, texto in reversed(edicoes):
        codigo = codigo[:inicio] + texto + codigo[fim:]
    return codigo


def _tokens(codigo):
    return tokenize.generate_tokens(io.StringIO(codigo).readline)


def proteger(codigo: str, state=None) -> str:
    """Replace strings and comments while preserving physical line numbers."""
    if state is None:
        state = _new_state(codigo)
    offset = _offsets(codigo)
    edicoes = []
    string_aberta = None
    profundidade = 0
    for token in _tokens(codigo):
        tipo = tokenize.tok_name[token.type]
        if tipo in {"FSTRING_START", "TSTRING_START"}:
            if profundidade == 0:
                string_aberta = token.start
            profundidade += 1
            continue
        if tipo in {"FSTRING_END", "TSTRING_END"}:
            profundidade -= 1
            if profundidade:
                continue
            inicio = offset(string_aberta)
        elif profundidade:
            continue
        elif token.type in (tokenize.STRING, tokenize.COMMENT):
            inicio = offset(token.start)
        else:
            continue

        fim = offset(token.end)
        original = codigo[inicio:fim]
        if token.type == tokenize.COMMENT:
            grupo, rotulo = state["comments"], "COM"
            marcador = f"# {state['prefix']}{rotulo}_{len(grupo)}__"
        else:
            grupo, rotulo = state["strings"], "STR"
            marcador = f"{state['prefix']}{rotulo}_{len(grupo)}__"
            if "\n" in original:
                marcador = '"""' + marcador + '\n' * original.count("\n") + '"""'
        grupo[marcador] = original
        edicoes.append((inicio, fim, marcador))
    return _substituir(codigo, edicoes)

def restaurar(codigo: str, state) -> str:
    for tok, txt in {**state["comments"], **state["strings"]}.items():
        codigo = codigo.replace(tok, txt)
    return codigo

# ── tradução lexical dos termos da linguagem ────────────────────────────────
def traduzir_termos(codigo: str, preservar_identificadores=False) -> str:
    offset = _offsets(codigo)
    tokens = list(_tokens(codigo))
    nomes = [
        (indice, token, offset(token.start), offset(token.end))
        for indice, token in enumerate(tokens)
        if token.type == tokenize.NAME
    ]

    simples = {}
    compostos = {}
    for categoria, pares in DIC.items():
        for termo, traducao in pares.items():
            partes = tuple(termo.split())
            if termo == "somar" and categoria == "funcoes_comuns":
                continue
            if len(partes) == 1:
                simples[partes[0]] = traducao
            else:
                compostos[partes] = traducao
    frases = sorted(compostos, key=lambda partes: (len(partes), sum(map(len, partes))), reverse=True)

    aliases = set(DIC["funcoes_comuns"]) | set(DIC["tipos"])
    literais, escopos = (analisar_identificadores(tokens)
                        if preservar_identificadores else (set(), {}))

    substituicoes = []
    indice_nome = 0
    traducoes = {}
    while indice_nome < len(nomes):
        token_indice, token, inicio, fim = nomes[indice_nome]
        encontrado = False
        for partes in frases:
            if indice_nome + len(partes) > len(nomes):
                continue
            grupo = nomes[indice_nome:indice_nome + len(partes)]
            if tuple(item[1].string for item in grupo) != partes:
                continue
            if preservar_identificadores and any(item[0] in literais for item in grupo):
                continue
            if any(
                not re.fullmatch(r"[ \t]+", codigo[grupo[pos][3]:grupo[pos + 1][2]])
                for pos in range(len(grupo) - 1)
            ):
                continue
            substituicoes.append((grupo[0][2], grupo[-1][3], compostos[partes]))
            traducoes[grupo[-1][0]] = compostos[partes]
            indice_nome += len(partes)
            encontrado = True
            break
        if encontrado:
            continue

        termo = token.string
        escopo = escopos.get(token_indice)
        anterior = tokens[token_indice - 1] if token_indice else None
        anterior_traduzido = traducoes.get(token_indice - 1, anterior.string if anterior else "")
        proximo = tokens[token_indice + 1] if token_indice + 1 < len(tokens) else None
        infixo = anterior and (
            anterior_traduzido in (")", "]", "}", "True", "False", "None")
            or anterior.type in (tokenize.NUMBER, tokenize.STRING)
            or (anterior.type == tokenize.NAME and anterior_traduzido.isidentifier()
                and anterior_traduzido not in ("print", "if", "elif", "while")
                and not keyword.iskeyword(anterior_traduzido))
        )
        sombreado = escopo and escopo.vincula(termo) and (
            termo in aliases or (termo in DIC["operadores"] and not infixo)
        )
        traducao = termo
        if token_indice not in literais and not (sombreado and (termo != "somar" or not infixo)):
            traducao = simples.get(termo, termo)
            if termo == "somar":
                traducao = "sum" if proximo and proximo.string == "(" and not infixo else "+"
        traducoes[token_indice] = traducao
        if traducao != termo:
            substituicoes.append((inicio, fim, traducao))
        indice_nome += 1

    return _substituir(codigo, substituicoes)


def corrigir_comparacoes(codigo: str) -> str:
    """Translate equality sugar in conditional headers, across physical lines."""
    offset = _offsets(codigo)
    edicoes = []
    inicio_instrucao = True
    condicional = False
    profundidade = 0
    for token in _tokens(codigo):
        if token.type in (tokenize.INDENT, tokenize.DEDENT, tokenize.NL, tokenize.COMMENT):
            continue
        if token.type == tokenize.NEWLINE:
            inicio_instrucao = True
            condicional = False
            continue
        termo = token.string
        if inicio_instrucao:
            condicional = termo in ("if", "elif", "while")
            inicio_instrucao = False
        if not condicional:
            continue
        if termo in ("(", "[", "{"):
            profundidade += 1
        elif termo in (")", "]", "}"):
            profundidade -= 1
        elif profundidade == 0:
            if termo in (":", "lambda"):
                condicional = False
            elif termo == "=":
                edicoes.append((offset(token.start), offset(token.end), "=="))
    return _substituir(codigo, edicoes)


def _interpolar(literal):
    if not literal.startswith(("'", '"')) or "{" not in literal:
        return literal
    candidato = "f" + literal
    try:
        arvore = ast.parse(candidato, mode="eval").body
    except SyntaxError:
        return literal
    campos = [parte for parte in arvore.values if isinstance(parte, ast.FormattedValue)]
    # Quoted JSON keys followed by a colon resemble f-string format fields.
    if campos and all(not (isinstance(campo.value, ast.Constant)
                           and isinstance(campo.value.value, str)
                           and campo.format_spec is not None) for campo in campos):
        return candidato
    return literal


def tratar_interpolacao(codigo: str, state) -> str:
    """Wrap shorthand print statements without touching normal Python calls."""
    offset = _offsets(codigo)
    edicoes = []
    instrucao = []
    for token in _tokens(codigo):
        if token.type in (tokenize.INDENT, tokenize.DEDENT, tokenize.NL, tokenize.COMMENT):
            continue
        if token.type not in (tokenize.NEWLINE, tokenize.ENDMARKER):
            instrucao.append(token)
            continue
        if len(instrucao) > 1 and instrucao[0].string == "print":
            primeiro, argumento = instrucao[:2]
            inicio, fim = offset(primeiro.end), offset(argumento.start)
            if codigo[inicio:fim].strip() == "" and inicio < fim and argumento.string not in {
                "(", "=", ":=", ":", ".", "+=", "-=", "*=", "/=", "//=", "**=", "%=",
                "&=", "|=", "^=", "<<=", ">>=", "@=", ";",
            }:
                edicoes.append((inicio, fim, "("))
                fim_argumento = offset(instrucao[-1].end)
                edicoes.append((fim_argumento, fim_argumento, ")"))
                for parte in instrucao[1:]:
                    if parte.string in state["strings"]:
                        state["strings"][parte.string] = _interpolar(state["strings"][parte.string])
        instrucao = []
    return _substituir(codigo, edicoes)


def converter(codigo_yl: str, filename: str = "<yuukolane>") -> str:
    state = _new_state(codigo_yl)
    linhas = io.StringIO(codigo_yl).readlines()
    try:
        codigo = proteger(codigo_yl, state)
        codigo = traduzir_termos(codigo, preservar_identificadores=True)
        codigo = corrigir_comparacoes(codigo)
        codigo = tratar_interpolacao(codigo, state)
        codigo = restaurar(codigo, state)
        validar_codigo(codigo, filename, codigo_yl)
        compile(codigo, filename, "exec")
    except tokenize.TokenError as erro:
        mensagem, (linha, coluna) = erro.args
        if linha > len(linhas) and linhas:
            linha, coluna = len(linhas), len(linhas[-1].rstrip("\r\n"))
        texto = linhas[linha - 1] if 1 <= linha <= len(linhas) else None
        raise SyntaxError(mensagem, (filename, linha, coluna + 1, texto)) from None
    except SyntaxError as erro:
        linha = erro.lineno
        texto = linhas[linha - 1] if linha and 1 <= linha <= len(linhas) else None
        # A generated column can point to the wrong place on the original line.
        mesma_linha = texto and erro.text and erro.text.rstrip("\r\n") == texto.rstrip("\r\n")
        coluna = erro.offset if mesma_linha else None
        raise type(erro)(erro.msg, (filename, linha, coluna, texto)) from None
    return codigo

# ── I/O de arquivo (.yl → .py) ──────────────────────────────────────────────
def processar_arquivo_yl(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"YK404 - Arquivo {path} não encontrado.")
    codigo_yl = path.read_text(encoding="utf-8")
    codigo_py = converter(codigo_yl, filename=str(path))
    destino = path.with_suffix(".py")
    destino.write_text(codigo_py, encoding="utf-8")
    print(f"[OK] Arquivo convertido com sucesso: {destino}")

# ── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python yuukolane_transpiler.py caminho/para/arquivo.yl")
        sys.exit(1)
    try:
        processar_arquivo_yl(Path(sys.argv[1]))
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)
