# yuukolane_transpiler.py
import os
import re, json, sys
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
    def _str(m):
        tok = f"__STR_{len(TOKENS_STR)}__"
        TOKENS_STR[tok] = m.group(0)
        return tok
    def _com(m):
        tok = f"__COM_{len(TOKENS_COM)}__"
        TOKENS_COM[tok] = m.group(0)
        return tok

    # strings (simples & multilinha)
    codigo = re.sub(r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')',
                    _str, codigo, flags=re.DOTALL)
    # comentários linha
    codigo = re.sub(r'#.*', _com, codigo)
    return codigo

def restaurar(codigo: str) -> str:
    for tok, txt in {**TOKENS_COM, **TOKENS_STR}.items():   # restaura comentários e strings
        codigo = codigo.replace(tok, txt)
    return codigo

# ── operadores compostos (‘somar’, ‘maior ou igual’ …) ─────────────────────
def substituir_operadores_compostos(codigo: str) -> str:
    compostos = sorted(
        [k for k in DIC["operadores"] if " " in k],
        key=len, reverse=True
    )
    for termo in compostos:
        tok = f"__OP_{termo.upper().replace(' ', '_')}__"
        codigo = re.sub(fr'\b{re.escape(termo)}\b', tok, codigo)
    return codigo

def restaurar_operadores_compostos(codigo: str) -> str:
    for termo, py in DIC["operadores"].items():
        if " " in termo:
            tok = f"__OP_{termo.upper().replace(' ', '_')}__"
            codigo = codigo.replace(tok, py)
    return codigo

# ── tradução token-a-token (simples) ────────────────────────────────────────
def traduzir_tokens_simples(codigo: str) -> str:
    for categoria, pares in DIC.items():
        for pt, py in pares.items():
            if " " not in pt:
                codigo = re.sub(fr'\b{re.escape(pt)}\b', py, codigo)
    return codigo

# ── correção ‘=’ → ‘==’ em cabeçalhos condicionais ─────────────────────────
COND_PATTERN = re.compile(r'^(\s*)(if|elif|while)(\s+[^:]+?)\s*:', re.MULTILINE)
def corrigir_comparacoes(codigo: str) -> str:
    def repl(m):
        indent, kw, cond = m.groups()
        cond_fix = re.sub(r'(?<![=!<>])=(?!=)', '==', cond)
        return f"{indent}{kw}{cond_fix}:"
    return COND_PATTERN.sub(repl, codigo)

# ── interpolação: mostrar "…" → print(f"…") ────────────────────────────────
def tratar_interpolacao(codigo: str) -> str:
    def repl(m):
        s = m.group(1)
        if '{' in s and '}' in s and not re.match(r'f[\'"]', s):
            s = 'f' + s
        return f"print({s})"
    pattern = r'(?<!\.)\bmostrar\b\s+(("""(?:.|\n)*?"""|\'\'\'(?:.|\n)*?\'\'\'|' \
              r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'))'
    return re.sub(pattern, repl, codigo)

# ── pipeline principal ──────────────────────────────────────────────────────
def converter(codigo_yl: str) -> str:
    _reset_tokens()
    codigo = proteger(codigo_yl)
    codigo = substituir_operadores_compostos(codigo)
    codigo = traduzir_tokens_simples(codigo)
    codigo = corrigir_comparacoes(codigo)
    codigo = restaurar_operadores_compostos(codigo)
    codigo = tratar_interpolacao(codigo)

    # VALIDAÇÃO com strings e comentários protegidos
    validar_codigo(codigo)

    # restauração final de strings e comentários
    codigo = restaurar(codigo)
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
