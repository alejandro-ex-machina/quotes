#!/usr/bin/env python3
import argparse
import json
import random
import shutil
import subprocess
import sys
import textwrap
import unicodedata
from collections import Counter
from pathlib import Path

GREEN = "\033[32m"
GRAY = "\033[90m"
RESET = "\033[0m"

QUOTES_FILE = "quotes.json"
EXPORT_BASENAME = "quotes_export"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.lower().strip().split())


def get_terminal_width(margin: int = 4, min_width: int = 40) -> int:
    width = shutil.get_terminal_size(fallback=(80, 20)).columns - margin
    return max(min_width, width)


def wrap_text(text: str, width: int) -> str:
    return textwrap.fill(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Muestra una cita aleatoria o filtrada desde quotes.json."
    )

    parser.add_argument("--category", help="Filtra por categoría exacta (ignora mayúsculas/tildes).")
    parser.add_argument("--author", help="Filtra por autor. Acepta coincidencia parcial.")
    parser.add_argument("--theme", help="Filtra por theme exacto (ignora mayúsculas/tildes).")
    parser.add_argument("--hardcore", action="store_true", help="Filtra solo citas con hardcore=true.")
    parser.add_argument("--random", action="store_true", help="Fuerza salida aleatoria. Es el comportamiento por defecto.")
    parser.add_argument("--list_authors", action="store_true", help="Lista autores y número de citas.")
    parser.add_argument("--list_categories", action="store_true", help="Lista categorías y número de citas.")
    parser.add_argument("--list_themes", action="store_true", help="Lista themes y número de citas.")
    parser.add_argument("--all", action="store_true", help="Muestra todas las citas filtradas.")
    parser.add_argument("--count", action="store_true", help="Muestra solo el número de citas resultantes.")
    parser.add_argument("--seed", type=int, help="Semilla para selección aleatoria reproducible.")
    parser.add_argument("--export", choices=["md", "pdf"], help="Exporta las citas filtradas a Markdown o PDF.")
    parser.add_argument("--output", help="Ruta de salida para la exportación.")
    parser.add_argument("--quotes-file", default=QUOTES_FILE, help="Ruta al fichero JSON de citas.")

    return parser.parse_args()


def load_quotes(quotes_file: str):
    quotes_path = Path(quotes_file)
    if not quotes_path.is_absolute():
        quotes_path = Path(__file__).with_name(quotes_file)

    try:
        with quotes_path.open("r", encoding="utf-8") as f:
            quotes = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"No se encuentra {quotes_path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"JSON inválido en {quotes_path}: {e}")

    if not isinstance(quotes, list) or not quotes:
        raise SystemExit(f"{quotes_path} no contiene una lista válida de citas.")

    return quotes


def matches_exact(value: str, expected: str) -> bool:
    return normalize(value) == normalize(expected)


def matches_partial(value: str, expected: str) -> bool:
    return normalize(expected) in normalize(value)


def filter_quotes(quotes, category=None, author=None, theme=None, hardcore=False):
    filtered = quotes

    if category:
        filtered = [q for q in filtered if matches_exact(q.get("category", ""), category)]

    if author:
        filtered = [q for q in filtered if matches_partial(q.get("author", ""), author)]

    if theme:
        filtered = [q for q in filtered if matches_exact(q.get("theme", ""), theme)]

    if hardcore:
        filtered = [q for q in filtered if bool(q.get("hardcore", False))]

    return filtered


def print_counter(title: str, values):
    counts = Counter((v or title).strip() if isinstance(v, str) else title for v in values)
    for item in sorted(counts, key=lambda s: normalize(s)):
        print(f"- {item} ({counts[item]})")


def print_author_list(quotes):
    print_counter("Desconocido", [q.get("author", "Desconocido") for q in quotes])


def print_category_list(quotes):
    print_counter("Sin categoría", [q.get("category", "Sin categoría") for q in quotes])


def print_theme_list(quotes):
    print_counter("Sin theme", [q.get("theme", "Sin theme") for q in quotes])


def build_meta(q):
    meta_parts = []

    ref = str(q.get("ref", "")).strip()
    category = str(q.get("category", "")).strip()
    theme = str(q.get("theme", "")).strip()
    hardcore = bool(q.get("hardcore", False))

    if ref:
        meta_parts.append(ref)
    if category:
        meta_parts.append(category)
    if theme:
        meta_parts.append(f"theme={theme}")
    if hardcore:
        meta_parts.append("hardcore")

    return " · ".join(meta_parts)


def print_quote(q, total=None):
    text = str(q.get("quote", "")).strip()
    author = str(q.get("author", "")).strip()

    width = get_terminal_width()

    author_colored = f"{GREEN}{author}{RESET}" if author else ""
    meta = build_meta(q)
    meta_colored = f"{GRAY}{meta}{RESET}" if meta else ""

    print(wrap_text(f"«{text}».", width))
    if author_colored:
        print(f"\n{author_colored}")
    if meta_colored:
        print(meta_colored)
    if total is not None:
        print(f"\n{total} quotes")


def filter_summary(args: argparse.Namespace) -> str:
    parts = []
    if args.author:
        parts.append(f"author={args.author}")
    if args.category:
        parts.append(f"category={args.category}")
    if args.theme:
        parts.append(f"theme={args.theme}")
    if args.hardcore:
        parts.append("hardcore=true")
    return ", ".join(parts) if parts else "sin filtros"


def quote_to_md(q: dict) -> str:
    text = str(q.get("quote", "")).strip()
    author = str(q.get("author", "")).strip() or "Desconocido"
    meta = build_meta(q)

    lines = [f"> {text}", "", f"— **{author}**"]
    if meta:
        lines.append("")
        lines.append(f"*{meta}*")
    return "\n".join(lines)


def build_markdown(quotes: list, args: argparse.Namespace) -> str:
    header = ["# Quotes", ""]
    header.append(f"Filtro: {filter_summary(args)}")
    header.append("")
    header.append(f"Total: {len(quotes)}")
    header.append("")

    body = []
    for idx, quote in enumerate(quotes, start=1):
        body.append(f"## Cita {idx}")
        body.append("")
        body.append(quote_to_md(quote))
        body.append("")

    return "\n".join(header + body).rstrip() + "\n"


def resolve_export_paths(args: argparse.Namespace) -> tuple[Path, Path | None]:
    if args.output:
        output_path = Path(args.output)
        suffix = output_path.suffix.lower()

        if args.export == "md":
            md_path = output_path if suffix == ".md" else output_path.with_suffix(".md")
            return md_path, None

        pdf_path = output_path if suffix == ".pdf" else output_path.with_suffix(".pdf")
        md_path = pdf_path.with_suffix(".md")
        return md_path, pdf_path

    if args.export == "md":
        return Path(f"{EXPORT_BASENAME}.md"), None

    return Path(f"{EXPORT_BASENAME}.md"), Path(f"{EXPORT_BASENAME}.pdf")


def export_markdown(quotes: list, args: argparse.Namespace) -> Path:
    md_path, _ = resolve_export_paths(args)
    md_content = build_markdown(quotes, args)
    md_path.write_text(md_content, encoding="utf-8")
    return md_path


def export_pdf(quotes: list, args: argparse.Namespace) -> Path:
    md_path, pdf_path = resolve_export_paths(args)
    if pdf_path is None:
        raise SystemExit("Error interno: falta ruta PDF de salida.")

    md_content = build_markdown(quotes, args)
    md_path.write_text(md_content, encoding="utf-8")

    try:
        subprocess.run(["pandoc", str(md_path), "-o", str(pdf_path)], check=True)
    except FileNotFoundError:
        raise SystemExit("No se encontró pandoc en el sistema. Instálalo o exporta a Markdown con --export=md.")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Falló la exportación a PDF (pandoc devolvió código {exc.returncode}).")

    return pdf_path


def main():
    args = parse_args()
    quotes = load_quotes(args.quotes_file)

    if args.list_authors:
        print_author_list(quotes)
        return

    if args.list_categories:
        print_category_list(quotes)
        return

    if args.list_themes:
        print_theme_list(quotes)
        return

    filtered = filter_quotes(
        quotes,
        category=args.category,
        author=args.author,
        theme=args.theme,
        hardcore=args.hardcore,
    )

    if args.count:
        print(len(filtered))
        return

    if not filtered:
        filters = []
        if args.category:
            filters.append(f"category={args.category}")
        if args.author:
            filters.append(f"author={args.author}")
        if args.theme:
            filters.append(f"theme={args.theme}")
        if args.hardcore:
            filters.append("hardcore=true")
        raise SystemExit("No hay citas para el filtro: " + ", ".join(filters))

    if args.seed is not None:
        random.seed(args.seed)

    selected = filtered if args.all or args.export else [random.choice(filtered)]

    if args.export == "md":
        output_path = export_markdown(selected, args)
        print(f"Exportado a Markdown: {output_path}")
        return

    if args.export == "pdf":
        output_path = export_pdf(selected, args)
        print(f"Exportado a PDF: {output_path}")
        return

    if args.all:
        for idx, quote in enumerate(selected, start=1):
            if idx > 1:
                print("\n" + "-" * max(20, get_terminal_width()) + "\n")
            print_quote(quote)
        print(f"\n{len(selected)} quotes")
        return

    print_quote(selected[0], total=len(filtered))


if __name__ == "__main__":
    main()
