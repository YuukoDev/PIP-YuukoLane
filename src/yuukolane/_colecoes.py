"""Resolução de aliases de coleções no Python gerado."""

import ast
import re


ALIASES_COLECOES = {
    "adicionar": "append",
    "remover": "remove",
    "ordenar": "sort",
    "reverter": "reverse",
    "contar": "count",
    "indexar": "index",
    "copiar": "copy",
}

# Emit the resolver only when it is used, so the generated .py stays standalone.
_RESOLVEDOR = """\
def {nome}(objeto, indice):
    import builtins
    original, alias = {aliases}[indice]
    try:
        return builtins.getattr(objeto, original)
    except builtins.AttributeError:
        tipos = (builtins.list, builtins.tuple, builtins.dict, builtins.set,
                 builtins.frozenset, builtins.str, builtins.bytes,
                 builtins.bytearray, builtins.range)
        if builtins.issubclass(builtins.type(objeto), tipos):
            from inspect import getattr_static
            ausente = builtins.object()
            if (getattr_static(objeto, original, ausente) is ausente
                    and getattr_static(objeto, alias, ausente) is not ausente):
                return builtins.getattr(objeto, alias)
        raise

"""


def resolver_aliases(codigo, arvore, nome):
    linhas = codigo.split("\n")
    inicios = [0]
    for linha in linhas:
        inicios.append(inicios[-1] + len(linha) + 1)

    def offset(linha, coluna):
        # AST columns are UTF-8 byte offsets, while source slices use characters.
        return inicios[linha - 1] + len(linhas[linha - 1].encode()[:coluna].decode())

    indices = {alias: indice for indice, alias in enumerate(ALIASES_COLECOES)}
    restritos = set()
    for no in ast.walk(arvore):
        if isinstance(no, getattr(ast, "pattern", ())):
            restritos.update(ast.walk(no))
        anotacao = getattr(no, "annotation", None) or getattr(no, "returns", None)
        if anotacao is not None:
            restritos.update(ast.walk(anotacao))
        if isinstance(no, ast.FormattedValue):
            valor = no.value
            fim_valor = offset(valor.end_lineno, valor.end_col_offset)
            if re.match(r"[) \t]*=(?!=)", codigo[fim_valor:]):
                # Rewriting a debug f-string would also change its visible label.
                restritos.update(ast.walk(valor))
        for decorador in getattr(no, "decorator_list", ()):
            # Python 3.8 only accepts a dotted name, optionally followed by a call.
            restritos.update(ast.walk(decorador.func if isinstance(decorador, ast.Call) else decorador))

    edicoes = []
    for no in ast.walk(arvore):
        if (not isinstance(no, ast.Attribute) or not isinstance(no.ctx, ast.Load)
                or no.attr not in indices or no in restritos):
            continue
        inicio = offset(no.lineno, no.col_offset)
        fim = offset(no.end_lineno, no.end_col_offset)
        fim_receptor = offset(no.value.end_lineno, no.value.end_col_offset)
        inicio_atributo = fim - len(no.attr)
        separador = re.match(r"(?:[)\s]|\\\r?\n|#[^\n]*\n)*\.", codigo[fim_receptor:inicio_atributo])
        if separador is None or codigo[inicio_atributo:fim] != no.attr:
            continue
        ponto = fim_receptor + separador.end() - 1
        edicoes.extend([
            (inicio, inicio, nome + "("),
            (ponto, ponto + 1, ""),
            (inicio_atributo, fim, f", {indices[no.attr]})"),
        ])

    if not edicoes:
        return codigo

    corpo = arvore.body
    primeiro = 1 if ast.get_docstring(arvore) is not None else 0
    while primeiro < len(corpo):
        no = corpo[primeiro]
        if not isinstance(no, ast.ImportFrom) or no.module != "__future__" or no.level:
            break
        primeiro += 1

    resolver = _RESOLVEDOR.format(nome=nome, aliases=tuple(ALIASES_COLECOES.items()))
    if primeiro:
        ultimo = corpo[primeiro - 1]
        fim = offset(ultimo.end_lineno, ultimo.end_col_offset)
        separador = re.match(r"[ \t]*;[ \t]*", codigo[fim:])
        if separador:
            preludio = (fim, fim + separador.end(), "\n" + resolver)
        else:
            ponto = inicios[ultimo.end_lineno]
            if ponto > len(codigo):
                preludio = (len(codigo), len(codigo), "\n" + resolver)
            else:
                preludio = (ponto, ponto, resolver)
    else:
        no = corpo[0]
        linha = min([no.lineno, *(d.lineno for d in getattr(no, "decorator_list", ()))])
        ponto = inicios[linha - 1]
        preludio = (ponto, ponto, resolver)

    for inicio, fim, texto in sorted(edicoes, reverse=True):
        codigo = codigo[:inicio] + texto + codigo[fim:]
    inicio, fim, texto = preludio
    return codigo[:inicio] + texto + codigo[fim:]
