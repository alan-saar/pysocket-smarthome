#!/usr/bin/env python3
"""
build_diagrams.py
=================
Ferramenta automatizada para compilação de diagramas Mermaid (.mmd)
em arquivos vetoriais (.svg) e imagens de alta resolução (.png)
utilizando temas personalizados (ex: Cyberpunk).

Uso:
    python3 tools/build_diagrams.py
    python3 tools/build_diagrams.py --help
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_DIAGRAMS_DIR = Path("doc/assets/diagrams")
DEFAULT_THEME_CSS = Path("doc/assets/themes/cyberpunk.css")
DEFAULT_BG_COLOR = "#030a16"
DEFAULT_SCALE = 2


def check_dependencies():
    """Verifica se o compilador Mermaid CLI (mmdc) está disponível no sistema."""
    mmdc_path = shutil.which("mmdc")
    if not mmdc_path:
        print("\033[91m[ERRO]\033[0m O utilitário 'mmdc' (Mermaid CLI) não foi encontrado no PATH.")
        print("Para instalar execute:")
        print("    npm install -g @mermaid-js/mermaid-cli")
        return None
    return mmdc_path


def compile_diagram(mmdc_path: str, mmd_file: Path, out_dir: Path, theme_css: Path, bg_color: str, scale: int):
    """Compila um único arquivo .mmd em .svg e .png."""
    base_name = mmd_file.stem
    svg_out = out_dir / f"{base_name}.svg"
    png_out = out_dir / f"{base_name}.png"

    print(f"[*] Processando: \033[96m{mmd_file.name}\033[0m")

    # Comando base
    base_cmd = [
        mmdc_path,
        "-i", str(mmd_file),
        "-b", bg_color,
    ]

    if theme_css.exists():
        base_cmd.extend(["-C", str(theme_css)])

    # 1. Gera SVG
    cmd_svg = base_cmd + ["-o", str(svg_out)]
    res_svg = subprocess.run(cmd_svg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_svg.returncode != 0:
        print(f"    \033[91m[FALHA SVG]\033[0m {res_svg.stderr.strip()}")
        return False
    print(f"    -> \033[92m[OK]\033[0m SVG: {svg_out.relative_to(Path.cwd()) if svg_out.is_relative_to(Path.cwd()) else svg_out}")

    # 2. Gera PNG
    cmd_png = base_cmd + ["-s", str(scale), "-o", str(png_out)]
    res_png = subprocess.run(cmd_png, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_png.returncode != 0:
        print(f"    \033[91m[FALHA PNG]\033[0m {res_png.stderr.strip()}")
        return False
    print(f"    -> \033[92m[OK]\033[0m PNG: {png_out.relative_to(Path.cwd()) if png_out.is_relative_to(Path.cwd()) else png_out}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Compilador automatizado de diagramas Mermaid para SVG/PNG com tema Cyberpunk."
    )
    parser.add_argument(
        "--diagrams-dir",
        type=Path,
        default=DEFAULT_DIAGRAMS_DIR,
        help=f"Diretório contendo os arquivos .mmd (padrão: {DEFAULT_DIAGRAMS_DIR})"
    )
    parser.add_argument(
        "--theme",
        type=Path,
        default=DEFAULT_THEME_CSS,
        help=f"Arquivo CSS do tema visual (padrão: {DEFAULT_THEME_CSS})"
    )
    parser.add_argument(
        "--bg-color",
        type=str,
        default=DEFAULT_BG_COLOR,
        help=f"Cor de fundo do canvas (padrão: {DEFAULT_BG_COLOR})"
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=DEFAULT_SCALE,
        help=f"Fator de escala de resolução para o PNG (padrão: {DEFAULT_SCALE})"
    )

    args = parser.parse_args()

    print("==================================================================")
    print("  COMPILADOR DE DIAGRAMAS MERMAID - SMART HOME (TEMA CYBERPUNK)   ")
    print("==================================================================")

    mmdc = check_dependencies()
    if not mmdc:
        sys.exit(1)

    if not args.diagrams_dir.exists():
        print(f"\033[91m[ERRO]\033[0m Diretório '{args.diagrams_dir}' não encontrado.")
        sys.exit(1)

    mmd_files = sorted(list(args.diagrams_dir.glob("*.mmd")))
    if not mmd_files:
        print(f"\033[93m[AVISO]\033[0m Nenhum arquivo .mmd encontrado em '{args.diagrams_dir}'.")
        sys.exit(0)

    print(f"Compilador : {mmdc}")
    print(f"Tema CSS   : {args.theme}")
    print(f"Fundo      : {args.bg_color}")
    print(f"Total .mmd : {len(mmd_files)}\n")

    success_count = 0
    for mmd_path in mmd_files:
        if compile_diagram(mmdc, mmd_path, args.diagrams_dir, args.theme, args.bg_color, args.scale):
            success_count += 1

    print("\n------------------------------------------------------------------")
    print(f"Processamento concluído: {success_count}/{len(mmd_files)} diagramas compilados com sucesso.")
    print("------------------------------------------------------------------\n")


if __name__ == "__main__":
    main()
