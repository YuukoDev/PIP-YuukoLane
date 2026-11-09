import ast
import io
import json
import os
import tokenize

# Carrega termos reservados do dicionário oficial
CAMINHO_DICIONARIO = os.path.join(os.path.dirname(__file__), "dicionario.json")
with open(CAMINHO_DICIONARIO, "r", encoding="utf-8") as f:
    dicionario = json.load(f)

# Conjunto de identificadores reservados derivados do dicionário
PALAVRAS_RESERVADAS = set()
for grupo in dicionario.values():
    PALAVRAS_RESERVADAS.update(grupo.keys())
PALAVRAS_RESERVADAS.update({"def", "import", "class", "True", "False", "None", "async", "await"})

# Tokens que não podem receber valores (literais fixos)
TOKENS_PROIBIDOS_ATRIB = {"verdadeiro", "falso", "nulo"}

def contar_indentacao(linha):
    return len(linha) - len(linha.lstrip(' '))


def _arvore(codigo):
    try:
        return ast.parse(codigo)
    except SyntaxError:
        # The public validator also accepts the YuukoLane spelling of return.
        # Only normalize a command position, never an attribute or string.
        linhas = io.StringIO(codigo).readlines()
        edicoes = []
        anterior = tokenize.NEWLINE
        try:
            for token in tokenize.generate_tokens(io.StringIO(codigo).readline):
                if token.type == tokenize.NAME and token.string == "retornar" and (
                    anterior in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)
                    or anterior in (":", ";")
                ):
                    linha, inicio = token.start
                    fim = token.end[1]
                    edicoes.append((linha - 1, inicio, fim))
                if token.type not in (tokenize.NL, tokenize.COMMENT):
                    anterior = token.string if token.type == tokenize.OP else token.type
            for linha, inicio, fim in reversed(edicoes):
                original = linhas[linha]
                linhas[linha] = original[:inicio] + "return" + original[fim:]
            return ast.parse("".join(linhas))
        except (SyntaxError, tokenize.TokenError):
            return None  # The transpiler's compile step reports syntax errors.


def _atribuicoes(arvore):
    for no in ast.walk(arvore):
        if isinstance(no, ast.Assign):
            yield from (alvo for alvo in no.targets if isinstance(alvo, ast.Name))
        elif isinstance(no, (ast.AnnAssign, ast.AugAssign)) and isinstance(no.target, ast.Name):
            yield no.target


def _erros_atribuicao(arvore, literais):
    erros = []
    reservados = TOKENS_PROIBIDOS_ATRIB if literais else PALAVRAS_RESERVADAS
    for alvo in _atribuicoes(arvore):
        if alvo.id in reservados:
            mensagem = (f"YK101 - Atribuição proibida a literal reservado '{alvo.id}'"
                        if literais else
                        f"YK102 - Identificador reservado '{alvo.id}' usado como variável")
            erros.append((alvo.lineno, mensagem))
    return erros


class _ContextoBlocos(ast.NodeVisitor):
    def __init__(self):
        self.escopo = None
        self.erros = []

    def _visitar_escopo(self, no, escopo):
        # Defaults, decorators, bases and annotations belong to the
        # surrounding scope. Only the body belongs to the new scope.
        for campo, valor in ast.iter_fields(no):
            if campo == "body":
                continue
            if isinstance(valor, ast.AST):
                self.visit(valor)
            elif isinstance(valor, list):
                for item in valor:
                    if isinstance(item, ast.AST):
                        self.visit(item)
        anterior, self.escopo = self.escopo, escopo
        for item in no.body if isinstance(no.body, list) else [no.body]:
            self.visit(item)
        self.escopo = anterior

    def visit_FunctionDef(self, no):
        self._visitar_escopo(no, "funcao")

    def visit_AsyncFunctionDef(self, no):
        self._visitar_escopo(no, "async")

    def visit_ClassDef(self, no):
        self._visitar_escopo(no, None)

    def visit_Lambda(self, no):
        self._visitar_escopo(no, "funcao")

    def visit_Expr(self, no):
        if isinstance(no.value, ast.Name) and no.value.id == "retornar":
            self.visit_Return(no)
        else:
            self.generic_visit(no)

    def visit_Return(self, no):
        if self.escopo is None:
            self.erros.append((no.lineno, "YK201 - 'retornar' fora de função"))
        self.generic_visit(no)

    def visit_Await(self, no):
        if self.escopo != "async":
            self.erros.append((no.lineno, "YK202 - 'await' fora de função async"))
        self.generic_visit(no)


def _erros_contexto(arvore):
    validador = _ContextoBlocos()
    validador.visit(arvore)
    return validador.erros


def _formatar(erros):
    return [f"{mensagem} (linha {linha})" for linha, mensagem in erros]


def validar_tokens_reservados(codigo):
    arvore = _arvore(codigo)
    return _formatar(_erros_atribuicao(arvore, True)) if arvore else []


def validar_identificadores_proibidos(codigo):
    arvore = _arvore(codigo)
    return _formatar(_erros_atribuicao(arvore, False)) if arvore else []


def validar_contexto_blocos(codigo):
    arvore = _arvore(codigo)
    return _formatar(_erros_contexto(arvore)) if arvore else []


def validar_codigo(codigo, filename=None, fonte=None):
    """Executa as validações YuukoLane sobre o código Python gerado."""
    arvore = _arvore(codigo)
    if arvore is None:
        return True
    erros = (_erros_atribuicao(arvore, True) + _erros_atribuicao(arvore, False)
             + _erros_contexto(arvore))
    if erros:
        mensagem = "\n".join(_formatar(erros))
        if filename is None:
            raise SyntaxError(mensagem)
        linha = erros[0][0]
        linhas = io.StringIO(codigo if fonte is None else fonte).readlines()
        raise SyntaxError(mensagem, (filename, linha, None, linhas[linha - 1]))
    return True
