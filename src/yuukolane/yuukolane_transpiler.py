# yuukolane_transpiler.py
import os
import re, json, sys, io, tokenize
from pathlib import Path
from .validador import validar_codigo

# Caminho absoluto do dicionario.json relativo a este arquivo:
caminho_atual = os.path.dirname(__file__)
caminho_dicionario = os.path.join(caminho_atual, "dicionario.json")

with open(caminho_dicionario, encoding="utf-8") as f:
    DIC = json.load(f)

# ── tokens temporários ──────────────────────────────────────────────────────
TOKENS_STR, TOKENS_COM = {}, {}

def _reset_tokens():
    global TOKENS_STR, TOKENS_COM
    TOKENS_STR, TOKENS_COM = {}, {}

# ── proteção de strings & comentários ──────────────────────────────────────
def proteger(codigo: str) -> str:
    """Replace Python string and comment tokens with placeholders before translation."""
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
                marcador = f"__STR_{len(TOKENS_STR)}__"
                TOKENS_STR[marcador] = token.string
                substituicoes.append((offset(token.start), offset(token.end), marcador))
            elif token.type == tokenize.COMMENT:
                marcador = f"__COM_{len(TOKENS_COM)}__"
                TOKENS_COM[marcador] = token.string
                substituicoes.append((offset(token.start), offset(token.end), marcador))
    except tokenize.TokenError as erro:
        raise SyntaxError(str(erro)) from erro

    for inicio, fim, marcador in reversed(substituicoes):
        codigo = codigo[:inicio] + marcador + codigo[fim:]
    return codigo

def restaurar(codigo: str) -> str:
    for tok, txt in {**TOKENS_COM, **TOKENS_STR}.items():   # restaura comentários e strings
        codigo = codigo.replace(tok, txt)
    return codigo

# ── tradução lexical dos termos da linguagem ────────────────────────────────
def traduzir_termos(codigo: str) -> str:
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

        traducao = simples.get(token.string)
        if token.string == "somar":
            proximo = tokens[token_indice + 1] if token_indice + 1 < len(tokens) else None
            traducao = "sum" if proximo and proximo.type == tokenize.OP and proximo.string == "(" else "+"
        if traducao is not None and traducao != token.string:
            substituicoes.append((inicio, fim, traducao))
        indice_nome += 1

    for inicio, fim, traducao in reversed(substituicoes):
        codigo = codigo[:inicio] + traducao + codigo[fim:]
    return codigo


# ── correção ‘=’ → ‘==’ em cabeçalhos condicionais ─────────────────────────
COND_PATTERN = re.compile(r'^(\s*)(if|elif|while)(\s+[^:]+?)\s*:', re.MULTILINE)
def corrigir_comparacoes(codigo: str) -> str:
    def repl(m):
        indent, kw, cond = m.groups()
        cond_fix = re.sub(r'(?<![=!<>])=(?!=)', '==', cond)
        return f"{indent}{kw}{cond_fix}:"
    return COND_PATTERN.sub(repl, codigo)

# ── saída de texto e interpolação ───────────────────────────────────────────
def tratar_interpolacao(codigo: str) -> str:
    def envolver_expressao(match):
        indent, expressao, comentario = match.groups()
        comentario = comentario or ""
        expressao = expressao.rstrip()
        for token in re.findall(r'__STR_\d+__', expressao):
            string = TOKENS_STR[token]
            if '{' in string and '}' in string and not re.match(r'(?i)(?:f|fr|rf)[\'"]', string):
                TOKENS_STR[token] = 'f' + string
        return f"{indent}print({expressao}){comentario}"

    return re.sub(
        r'(?m)^([ \t]*)print[ \t]+(?!\()(.*?)([ \t]+__COM_\d+__)?$',
        envolver_expressao,
        codigo,
    )


def converter(codigo_yl: str) -> str:
    _reset_tokens()
    codigo = proteger(codigo_yl)
    codigo = traduzir_termos(codigo)
    codigo = corrigir_comparacoes(codigo)
    codigo = tratar_interpolacao(codigo)

    # VALIDAÇÃO com strings e comentários protegidos
    validar_codigo(codigo)

    # restauração final de strings e comentários
    codigo = restaurar(codigo)
    compile(codigo, "<yuukolane>", "exec")
    return codigo

# ── I/O de arquivo (.yl → .py) ──────────────────────────────────────────────
def processar_arquivo_yl(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"YK404 - Arquivo {path} não encontrado.")
    codigo_yl = path.read_text(encoding="utf-8")
    codigo_py = converter(codigo_yl)
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
