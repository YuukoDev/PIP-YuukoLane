import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from yuukolane.cli import main
from yuukolane.cli import carregar_modulos_yl_em_memoria


class CliTests(unittest.TestCase):
    def run_cli(self, source, *options):
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "programa.yl"
            source_path.write_text(source, encoding="utf-8")
            output = StringIO()
            with patch("sys.argv", ["yuuko", str(source_path), *options]):
                with redirect_stdout(output):
                    status = main()
            return output.getvalue(), status

    def test_transpile_only_prints_generated_python(self):
        output, status = self.run_cli("mostrar 42\n", "--so-transpilar")
        self.assertEqual(output, "print(42)\n")
        self.assertIsNone(status)

    def test_check_reports_valid_program(self):
        output, status = self.run_cli("se verdadeiro:\n    vazio\n", "--checar")
        self.assertIn("[OK] Código válido", output)
        self.assertIsNone(status)

    def test_check_reports_python_syntax_errors(self):
        output, status = self.run_cli("resultado =\n", "--checar")
        self.assertIn("[ERRO]", output)
        self.assertNotIn("[OK]", output)
        self.assertEqual(status, 1)

    def test_both_validation_modes_show_the_original_source(self):
        for modo in ("--checar", "--so-transpilar"):
            with self.subTest(modo=modo):
                output, status = self.run_cli("retornar 1\n", modo)
                self.assertEqual(status, 1)
                self.assertIn('programa.yl", line 1', output)
                self.assertIn("retornar 1", output)
                self.assertIn("YK201", output)

    def test_import_errors_point_to_the_local_yl_module(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            main_path = root / "programa.yl"
            helper_path = root / "auxiliar.yl"
            main_path.write_text("import auxiliar\n", encoding="utf-8")
            helper_path.write_text("mostrar (\n", encoding="utf-8")
            with self.assertRaises(SyntaxError) as erro:
                carregar_modulos_yl_em_memoria(main_path)
            self.assertEqual(erro.exception.filename, str(helper_path))

    def test_cli_process_exits_nonzero_on_validation_error(self):
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "ruim.yl"
            source_path.write_text("resultado =\n", encoding="utf-8")
            env = os.environ.copy()
            package_root = Path(__file__).resolve().parents[1] / "src"
            env["PYTHONPATH"] = str(package_root)
            result = subprocess.run(
                [sys.executable, "-m", "yuukolane.cli", str(source_path), "--checar"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("[ERRO]", result.stdout)

    def test_local_yuukolane_module_can_be_imported_and_executed(self):
        module_name = "_yuukolane_test_helpers"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            helper_path = root / f"{module_name}.yl"
            main_path = root / "programa.yl"
            helper_path.write_text(
                "definir triplo(valor):\n    retornar valor multiplicar 3\n",
                encoding="utf-8",
            )
            main_path.write_text(
                f"from {module_name} import triplo\nmostrar triplo(4)\n",
                encoding="utf-8",
            )

            try:
                generated = carregar_modulos_yl_em_memoria(main_path)
                output = StringIO()
                with redirect_stdout(output):
                    exec(generated, {})
                self.assertEqual(output.getvalue(), "12\n")
            finally:
                import sys

                sys.modules.pop(module_name, None)

    def test_nested_local_yuukolane_module_can_be_imported(self):
        import sys

        package_name = "_yuukolane_test_package"
        module_name = f"{package_name}.helpers"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            package_dir = root / package_name
            package_dir.mkdir()
            helper_path = package_dir / "helpers.yl"
            main_path = root / "programa.yl"
            helper_path.write_text(
                "definir triplo(valor):\n    retornar valor multiplicar 3\n",
                encoding="utf-8",
            )
            main_path.write_text(
                f"from {module_name} import triplo\nmostrar triplo(4)\n",
                encoding="utf-8",
            )

            old_path = sys.path[:]
            sys.path.insert(0, str(root))
            try:
                generated = carregar_modulos_yl_em_memoria(main_path)
                output = StringIO()
                with redirect_stdout(output):
                    exec(generated, {})
                self.assertEqual(output.getvalue(), "12\n")
            finally:
                sys.path[:] = old_path
                sys.modules.pop(module_name, None)
                sys.modules.pop(package_name, None)

    def test_relative_import_inside_local_package_module(self):
        import sys

        package_name = "_yuukolane_relative_package"
        helper_name = f"{package_name}.helpers"
        common_name = f"{package_name}.common"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            package_dir = root / package_name
            package_dir.mkdir()
            (package_dir / "helpers.yl").write_text(
                "from .common import FATOR\ndefinir quadruplicar(valor):\n    retornar valor multiplicar FATOR\n",
                encoding="utf-8",
            )
            (package_dir / "common.yl").write_text("FATOR = 4\n", encoding="utf-8")
            main_path = root / "programa.yl"
            main_path.write_text(
                f"from {helper_name} import quadruplicar\nmostrar quadruplicar(3)\n",
                encoding="utf-8",
            )

            try:
                generated = carregar_modulos_yl_em_memoria(main_path)
                output = StringIO()
                with redirect_stdout(output):
                    exec(generated, {})
                self.assertEqual(output.getvalue(), "12\n")
            finally:
                for name in (helper_name, common_name, package_name):
                    sys.modules.pop(name, None)

    def test_circular_imports_load_like_python_modules(self):
        import sys

        first_name = "_yuukolane_cycle_a"
        second_name = "_yuukolane_cycle_b"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / f"{first_name}.yl").write_text(
                f"definir primeiro():\n    retornar 'A'\nfrom {second_name} import segundo\n",
                encoding="utf-8",
            )
            (root / f"{second_name}.yl").write_text(
                f"definir segundo():\n    retornar 'B'\nfrom {first_name} import primeiro\n",
                encoding="utf-8",
            )
            main_path = root / "programa.yl"
            main_path.write_text(
                f"from {first_name} import primeiro\nmostrar primeiro()\n",
                encoding="utf-8",
            )

            try:
                generated = carregar_modulos_yl_em_memoria(main_path)
                output = StringIO()
                with redirect_stdout(output):
                    exec(generated, {})
                self.assertEqual(output.getvalue(), "A\n")
            finally:
                sys.modules.pop(first_name, None)
                sys.modules.pop(second_name, None)


if __name__ == "__main__":
    unittest.main()
