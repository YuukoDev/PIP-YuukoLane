# yuukolane_transpiler.py
import os
import re, json, sys, io, tokenize, uuid
from pathlib import Path
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

# ── proteção de strings & comentários ──────────────────────────────────────
def proteger(codigo: str, state=None) -> str:
    """Replace Python string and comment tokens with placeholders before translation."""
    if state is None:
        state = _new_state(codigo)
    linhas = codigo.splitlines(keepends=True)
    deslocamentos = [0]
    for linha in linhas:
        deslocamentos.append(deslocamentos[-1] + len(linha))

    def offset(posicao):
        linha, coluna = posicao
        return deslocamentos[min(linha - 1, len(deslocamentos) - 1)] + coluna

    try:
        tokens = tokenize.generate_tokens(io.StringIO(codigo).readline)
        substituicoes = []
        for token in tokens:
            if token.type == tokenize.STRING:
                marcador = f"{state['prefix']}STR_{len(state['strings'])}__"
                state['strings'][marcador] = token.string
                substituicoes.append((offset(token.start), offset(token.end), marcador))
            elif token.type == tokenize.COMMENT:
                marcador = f"{state['prefix']}COM_{len(state['comments'])}__"
                state['comments'][marcador] = token.string
                substituicoes.append((offset(token.start), offset(token.end), marcador))
    except tokenize.TokenError as erro:
        raise SyntaxError(str(erro)) from erro

    for inicio, fim, marcador in reversed(substituicoes):
        codigo = codigo[:inicio] + marcador + codigo[fim:]
    return codigo

def restaurar(codigo: str, state) -> str:
    for tok, txt in {**state["comments"], **state["strings"]}.items():
        codigo = codigo.replace(tok, txt)
    return codigo

# ── tradução lexical dos termos da linguagem ────────────────────────────────
def traduzir_termos(codigo: str, preservar_identificadores=False) -> str:
    linhas = codigo.splitlines(keepends=True)
    deslocamentos = [0]
    for linha in linhas:
        deslocamentos.append(deslocamentos[-1] + len(linha))

    def offset(posicao):
        linha, coluna = posicao
        return deslocamentos[min(linha - 1, len(deslocamentos) - 1)] + coluna

    tokens = list(tokenize.generate_tokens(io.StringIO(codigo).readline))
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

    protegidos = set()
    if preservar_identificadores:
        # Protect declared names and assignment targets across the source.
        for i, t in enumerate(tokens):
            if t.type != tokenize.NAME:
                continue
            anterior = tokens[i - 1].string if i else ""
            proximo = tokens[i + 1].string if i + 1 < len(tokens) else ""
            if anterior in ("def", "class", "definir", "funcao", "classe", "as"):
                protegidos.add(t.string)
            if proximo == "=" and (anterior in ("", "(", ",") or t.start[1] == 0):
                protegidos.add(t.string)
            # Attribute names (obj.adicionar) are user/API-defined, not keywords.
            if anterior == ".":
                protegidos.add(t.string)
            # Parameter names in a function declaration.
            if any(tok.string in ("def", "definir", "funcao") for tok in tokens[max(0, i - 8):i]) and proximo in (",", ")", "=", ":"):
                protegidos.add(t.string)

    substituicoes = []
    indice_nome = 0
    while indice_nome < len(nomes):
        token_indice, token, inicio, fim = nomes[indice_nome]
        encontrado = False
        for partes in frases:
            if indice_nome + len(partes) > len(nomes):
                continue
            grupo = nomes[indice_nome:indice_nome + len(partes)]
            if tuple(item[1].string for item in grupo) != partes:
                continue
            if preservar_identificadores and any(item[1].string in protegidos for item in grupo):
                continue
            if any(
                not re.fullmatch(r"[ \t]+", codigo[grupo[pos][3]:grupo[pos + 1][2]])
                for pos in range(len(grupo) - 1)
            ):
                continue
            substituicoes.append((grupo[0][2], grupo[-1][3], compostos[partes]))
            indice_nome += len(partes)
            encontrado = True
            break
        if encontrado:
            continue

        traducao = token.string if token.string in protegidos else simples.get(token.string)
        if token.string == "somar" and token.string not in protegidos:
            proximo = tokens[token_indice + 1] if token_indice + 1 < len(tokens) else None
            traducao = "sum" if proximo and proximo.type == tokenize.OP and proximo.string == "(" else "+"
        if traducao is not None and traducao != token.string:
            substituicoes.append((inicio, fim, traducao))
        indice_nome += 1

    for inicio, fim, traducao in reversed(substituicoes):
        codigo = codigo[:inicio] + traducao + codigo[fim:]
    return codigo


# ── Conditional comparison sugar; preserve nested keyword arguments ──
def corrigir_comparacoes(codigo: str) -> str:
    linhas = codigo.splitlines(keepends=True)
    saida = []
    for linha in linhas:
        try:
            toks = list(tokenize.generate_tokens(io.StringIO(linha).readline))
        except (tokenize.TokenError, IndentationError):
            saida.append(linha)
            continue
        nomes = [t for t in toks if t.type not in (tokenize.INDENT, tokenize.DEDENT, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER)]
        if not nomes or nomes[0].string not in ("if", "elif", "while"):
            saida.append(linha)
            continue
        profundidade = 0
        posicoes = []
        for t in nomes[1:]:
            if t.string in ("(", "[", "{"):
                profundidade += 1
            elif t.string in (")", "]", "}"):
                profundidade -= 1
            elif t.string == ":" and profundidade == 0:
                break
            elif t.string == "=" and profundidade == 0:
                posicoes.append(t.start[1])
        for pos in reversed(posicoes):
            linha = linha[:pos] + "==" + linha[pos+1:]
        saida.append(linha)
    return "".join(saida)

# ── saída de texto e interpolação ───────────────────────────────────────────
def tratar_interpolacao(codigo: str, state) -> str:
    def envolver_expressao(match):
        indent, expressao, comentario = match.groups()
        comentario = comentario or ""
        expressao = expressao.rstrip()
        for token in state['strings']:
            if token not in expressao:
                continue
            string = state['strings'][token]
            if ('{' in string and '}' in string and
                    not re.match(r'(?i)(?:f|fr|rf|r|b|u|br|rb)[\'"]', string) and
                    re.search(r'(?<!\{)\{[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*\}', string)):
                state['strings'][token] = 'f' + string
        return f"{indent}print({expressao}){comentario}"

    return re.sub(
        r'(?m)^([ \t]*)print[ \t]+(?!\()(.*?)([ \t]+__YK_[a-f0-9]+_COM_\d+__)?$',
        envolver_expressao,
        codigo,
    )


def converter(codigo_yl: str, filename: str = "<yuukolane>") -> str:
    state = _new_state(codigo_yl)
    codigo = proteger(codigo_yl, state)
    codigo = traduzir_termos(codigo, preservar_identificadores=True)
    codigo = corrigir_comparacoes(codigo)
    codigo = tratar_interpolacao(codigo, state)

    # VALIDAÇÃO com strings e comentários protegidos
    validar_codigo(codigo)

    # restauração final de strings e comentários
    codigo = restaurar(codigo, state)
    compile(codigo, filename, "exec")
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
