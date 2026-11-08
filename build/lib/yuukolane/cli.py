import argparse
import sys
import types
import re
import tempfile
import subprocess
import os
from pathlib import Path
from importlib.util import find_spec
from .yuukolane_transpiler import converter
from .validador import validar_codigo

IMPORT_PATTERN = re.compile(
    r'^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))', re.MULTILINE
)

def carregar_modulos_yl_em_memoria(arquivo_principal: Path, debug=False, salvar_transpilados_em=None):
    base_dir = arquivo_principal.parent.resolve()
    modulos_carregados = {}

    def eh_modulo_local(modulo: str) -> bool:
        # Verifica se o arquivo está na estrutura do projeto
        caminho_yl = base_dir / Path(*modulo.split('.')).with_suffix('.yl')
        caminho_py = base_dir / Path(*modulo.split('.')).with_suffix('.py')
        return caminho_yl.exists() or caminho_py.exists()

    def achar_caminho_modulo(modulo: str):
        caminho_yl = base_dir / Path(*modulo.split('.')).with_suffix('.yl')
        if caminho_yl.exists():
            if debug:
                print(f"✔️ Encontrado .yl de '{modulo}': {caminho_yl}")
            return caminho_yl

        caminho_py = base_dir / Path(*modulo.split('.')).with_suffix('.py')
        if caminho_py.exists():
            if debug:
                print(f"✔️ Encontrado .py de '{modulo}': {caminho_py}")
            return caminho_py

        return None

    def transpilar_modulo(modulo: str):
        if modulo in modulos_carregados:
            return

        # Ignora módulos do sistema (pip/padrão)
        if not eh_modulo_local(modulo):
            if debug:
                print(f"🔹 Módulo externo ignorado: {modulo}")
            return

        caminho = achar_caminho_modulo(modulo)
        if caminho is None:
            raise ImportError(
                f"\n[ERRO] Módulo '{modulo}' não encontrado.\n"
                f"🧩 Caminho esperado: {base_dir / Path(*modulo.split('.')).with_suffix('.yl')}\n"
                f"📁 Verifique se o arquivo existe e o nome está correto.\n"
            )

        if caminho.suffix == ".yl":
            codigo = converter(caminho.read_text(encoding="utf-8"))
        else:
            codigo = caminho.read_text(encoding="utf-8")

        # Salva no diretório temporário
        if salvar_transpilados_em:
            caminho_dest = Path(salvar_transpilados_em) / Path(*modulo.split('.')).with_suffix('.py')
            caminho_dest.parent.mkdir(parents=True, exist_ok=True)
            caminho_dest.write_text(codigo, encoding="utf-8")

            # Criar __init__.py recursivamente
            pasta_atual = caminho_dest.parent
            base_temp = Path(salvar_transpilados_em).resolve()
            while True:
                init_file = pasta_atual / '__init__.py'
                if not init_file.exists():
                    init_file.write_text('', encoding='utf-8')
                    if debug:
                        print(f"📦 Criado {init_file}")
                if pasta_atual == base_temp:
                    break
                pasta_atual = pasta_atual.parent

        # Transpila os submódulos importados
        for match in IMPORT_PATTERN.finditer(codigo):
            imp = match.group(1) or match.group(2)
            if imp:
                transpilar_modulo(imp)

        mod = types.ModuleType(modulo)
        try:
            exec(codigo, mod.__dict__)
        except SyntaxError as err:
            print(f"\n❌ Erro de sintaxe no módulo '{modulo}':")
            print(f"📍 Linha {err.lineno}: {err.text.strip() if err.text else 'texto indisponível'}")
            print(f"🧾 Código completo gerado:\n\n{codigo}")
            raise

        sys.modules[modulo] = mod
        modulos_carregados[modulo] = mod

    # Transpila os imports principais
    codigo_main = arquivo_principal.read_text(encoding="utf-8")
    for match in IMPORT_PATTERN.finditer(codigo_main):
        imp = match.group(1) or match.group(2)
        if imp:
            transpilar_modulo(imp)

    if arquivo_principal.suffix == ".yl":
        codigo_main_transpilado = converter(codigo_main)
        if salvar_transpilados_em:
            caminho_dest = Path(salvar_transpilados_em) / arquivo_principal.with_suffix('.py').name
            caminho_dest.write_text(codigo_main_transpilado, encoding="utf-8")
        return codigo_main_transpilado
    else:
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
        return

    try:
        if args.checar:
            codigo_yl = caminho.read_text(encoding="utf-8")
            codigo_py = converter(codigo_yl)
            validar_codigo(codigo_py)
            print("[OK] Código válido. Nenhum erro encontrado.")
            return

        if args.so_transpilar:
            codigo_yl = caminho.read_text(encoding="utf-8")
            codigo_py = converter(codigo_yl)
            print(codigo_py)
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
                    executar_em_subprocesso_via_tempdir(main_path, Path(tempdir), projeto_dir)
                    return
                else:
                    exec(codigo_py, globals())
        else:
            codigo = caminho.read_text(encoding="utf-8")
            if contem_asyncio_run(codigo):
                projeto_dir = caminho.parent.resolve()
                executar_em_subprocesso_via_tempdir(caminho, caminho.parent, projeto_dir)
            else:
                exec(codigo, globals())

    except Exception as e:
        print(f"[ERRO] {e}")

if __name__ == "__main__":
    main()
