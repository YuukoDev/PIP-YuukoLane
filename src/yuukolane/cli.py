import argparse
import ast
import importlib
import importlib.util
import sys
import tempfile
import traceback
import subprocess
import os
from pathlib import Path
from .yuukolane_transpiler import converter

def carregar_modulos_yl_em_memoria(arquivo_principal: Path, debug=False, salvar_transpilados_em=None):
    """Transpile local imports, stage them as Python modules, and preload them."""
    base_dir = arquivo_principal.parent.resolve()
    codigo_main = arquivo_principal.read_text(encoding="utf-8")
    if arquivo_principal.suffix != ".yl":
        return codigo_main

    codigo_main = converter(codigo_main, filename=str(arquivo_principal))
    arquivos_modulos = {}
    imports_principais = set()

    def achar_modulo_local(nome: str):
        caminho = base_dir.joinpath(*nome.split("."))
        if caminho.is_dir():
            for nome_init in ("__init__.yl", "__init__.py"):
                candidato = caminho / nome_init
                if candidato.is_file():
                    return candidato
        for sufixo in (".yl", ".py"):
            candidato = caminho.with_suffix(sufixo)
            if candidato.is_file():
                return candidato
        return None

    def descobrir_imports(codigo: str, pacote: str = ""):
        encontrados = set()
        arvore = ast.parse(codigo)
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                encontrados.update(alias.name for alias in no.names)
            elif isinstance(no, ast.ImportFrom):
                if no.level:
                    if not pacote:
                        continue
                    relativo = "." * no.level + (no.module or "")
                    try:
                        nome_modulo = importlib.util.resolve_name(relativo, pacote)
                    except ImportError:
                        continue
                else:
                    nome_modulo = no.module or ""
                if nome_modulo:
                    encontrados.add(nome_modulo)
                    for alias in no.names:
                        if alias.name != "*":
                            encontrados.add(f"{nome_modulo}.{alias.name}")
        return encontrados

    pendentes = list(descobrir_imports(codigo_main))
    imports_principais.update(pendentes)
    while pendentes:
        nome = pendentes.pop()
        if not nome or nome in arquivos_modulos:
            continue
        origem = achar_modulo_local(nome)
        if origem is None:
            continue

        if origem.name.startswith("__init__."):
            nome_real = nome
            pacote_modulo = nome
        else:
            nome_real = nome
            pacote_modulo = nome.rpartition(".")[0]

        if origem.suffix == ".yl":
            codigo = converter(origem.read_text(encoding="utf-8"), filename=str(origem))
        else:
            codigo = origem.read_text(encoding="utf-8")
        arquivos_modulos[nome_real] = (origem, codigo)
        novos_imports = descobrir_imports(codigo, pacote_modulo)
        pendentes.extend(novos_imports - arquivos_modulos.keys())
        if debug:
            print(f"✔️ Módulo local preparado: {nome_real} ({origem})")

    def carregar_preparados(diretorio_temp: Path):
        diretorio_temp = diretorio_temp.resolve()
        for nome, (origem, codigo) in arquivos_modulos.items():
            caminho_modulo = diretorio_temp.joinpath(*nome.split("."))
            if origem.name.startswith("__init__."):
                destino = caminho_modulo / "__init__.py"
            else:
                destino = caminho_modulo.with_suffix(".py")
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(codigo, encoding="utf-8")

            pasta_atual = destino.parent
            while pasta_atual != diretorio_temp:
                init_file = pasta_atual / "__init__.py"
                init_file.touch(exist_ok=True)
                pasta_atual = pasta_atual.parent

        caminho_main = diretorio_temp / arquivo_principal.with_suffix(".py").name
        caminho_main.write_text(codigo_main, encoding="utf-8")

        caminhos_sys = [str(diretorio_temp), str(base_dir)]
        sys.path[:0] = caminhos_sys
        try:
            for nome in sorted(imports_principais, key=lambda item: item.count(".")):
                if nome in arquivos_modulos:
                    importlib.import_module(nome)
        finally:
            for caminho in caminhos_sys:
                try:
                    sys.path.remove(caminho)
                except ValueError:
                    pass

    if salvar_transpilados_em:
        carregar_preparados(Path(salvar_transpilados_em))
    else:
        with tempfile.TemporaryDirectory(prefix="yuukolane-") as temporario:
            carregar_preparados(Path(temporario))

    return codigo_main

def contem_asyncio_run(codigo: str) -> bool:
    return "asyncio.run" in codigo or "async def main" in codigo

def executar_em_subprocesso_via_tempdir(main_py_path: Path, tempdir: Path, projeto_dir: Path):
    print(f"🚀 Executando via subprocesso com PYTHONPATH: {tempdir} + {projeto_dir}")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tempdir) + os.pathsep + str(projeto_dir) + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, str(main_py_path)],
        capture_output=True,
        text=True,
        env=env
    )

    if result.stdout:
        print("🟢 STDOUT:")
        print(result.stdout)

    if result.stderr:
        print("🔴 STDERR:")
        print(result.stderr)

    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Transpila e executa código YuukoLane (.yl)")
    parser.add_argument("arquivo", help="Caminho do arquivo .yl ou .py")
    parser.add_argument("--so-transpilar", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--checar", action="store_true")
    args = parser.parse_args()
    caminho = Path(args.arquivo)

    sys.path.insert(0, str(caminho.parent.resolve()))

    if not caminho.exists() or caminho.suffix not in [".yl", ".py"]:
        print(f"[ERRO] Arquivo inválido: {caminho}")
        return 2

    try:
        if args.checar:
            codigo_yl = caminho.read_text(encoding="utf-8")
            converter(codigo_yl, filename=str(caminho))
            print("[OK] Código válido. Nenhum erro encontrado.")
            return

        if args.so_transpilar:
            codigo_yl = caminho.read_text(encoding="utf-8")
            codigo_py = converter(codigo_yl, filename=str(caminho))
            sys.stdout.write(codigo_py)
            return

        print("🚀 Executando código em memória...\n")

        if caminho.suffix == ".yl":
            with tempfile.TemporaryDirectory() as tempdir:
                codigo_py = carregar_modulos_yl_em_memoria(
                    caminho, debug=args.debug, salvar_transpilados_em=tempdir
                )
                if args.debug:
                    print("📜 Código transpilado:\n")
                    print(codigo_py)
                    print("\n🔚 Fim da transpilação\n")

                if contem_asyncio_run(codigo_py):
                    main_path = Path(tempdir) / caminho.with_suffix('.py').name
                    projeto_dir = caminho.parent.resolve()
                    return executar_em_subprocesso_via_tempdir(main_path, Path(tempdir), projeto_dir)
                else:
                    exec(codigo_py, globals())
        else:
            codigo = caminho.read_text(encoding="utf-8")
            if contem_asyncio_run(codigo):
                projeto_dir = caminho.parent.resolve()
                return executar_em_subprocesso_via_tempdir(caminho, caminho.parent, projeto_dir)
            else:
                exec(codigo, globals())

    except SyntaxError as erro:
        mensagem = "".join(traceback.format_exception_only(type(erro), erro)).rstrip()
        print(f"[ERRO] {mensagem}")
        return 1
    except Exception as e:
        print(f"[ERRO] {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
