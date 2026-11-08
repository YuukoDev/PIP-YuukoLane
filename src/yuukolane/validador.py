import os
import re
import json

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


def validar_tokens_reservados(codigo):
    """Impede atribuições para verdadeiro, falso, nulo."""
    linhas = codigo.splitlines()
    erros = []
    atrib_pattern = re.compile(r'^\s*([a-zA-Z_][\w]*)\s*=')

    for i, linha in enumerate(linhas):
        if linha.strip().startswith("#"):
            continue
        match = atrib_pattern.match(linha)
        if match:
            var = match.group(1)
            if var in TOKENS_PROIBIDOS_ATRIB:
                erros.append(f"YK101 - Atribuição proibida a literal reservado '{var}' (linha {i+1})")
    return erros


def validar_identificadores_proibidos(codigo):
    """Evita nomes de variáveis que são palavras reservadas."""
    erros = []
    linhas = codigo.splitlines()
    atrib_pattern = re.compile(r'^\s*([a-zA-Z_][\w]*)\s*=')

    for i, linha in enumerate(linhas):
        if linha.strip().startswith("#"):
            continue
        match = atrib_pattern.match(linha)
        if match:
            nome = match.group(1)
            if nome in PALAVRAS_RESERVADAS:
                erros.append(f"YK102 - Identificador reservado '{nome}' usado como variável (linha {i+1})")
    return erros


def validar_contexto_blocos(codigo):
    """Valida se 'retornar' está em função e 'await' está em função async."""
    linhas = codigo.splitlines()
    escopo = []  # Pilha de escopos: tuplas (tipo, indentacao)
    erros = []

    for i, linha in enumerate(linhas):
        linha_sem_espaco = linha.lstrip()
        if not linha_sem_espaco or linha_sem_espaco.startswith("#"):
            continue

        indent = contar_indentacao(linha)

        # Remove escopos fechados
        while escopo and indent <= escopo[-1][1]:
            escopo.pop()

        # Detecta início de escopos
        if re.match(r'async\s+def\s+', linha_sem_espaco):
            escopo.append(("async_funcao", indent))
        elif re.match(r'def\s+', linha_sem_espaco):
            escopo.append(("funcao", indent))
        elif re.match(r'class\s+', linha_sem_espaco):
            escopo.append(("classe", indent))

        # Valida comandos contextuais
        if re.search(r'\b(?:retornar|return)\b', linha_sem_espaco):
            if not any(tipo in ("funcao", "async_funcao") for tipo, _ in escopo):
                erros.append(f"YK201 - 'retornar' fora de função (linha {i+1})")
        if re.search(r'\bawait\b', linha_sem_espaco):
            if not any(tipo == "async_funcao" for tipo, _ in escopo):
                erros.append(f"YK202 - 'await' fora de função async (linha {i+1})")

    return erros


def validar_codigo(codigo):
    """Executa todas as validações sobre o código Python gerado pela YuukoLane."""
    erros = []
    erros += validar_tokens_reservados(codigo)
    erros += validar_identificadores_proibidos(codigo)
    erros += validar_contexto_blocos(codigo)

    if erros:
        raise SyntaxError("\n".join(erros))
    return True
