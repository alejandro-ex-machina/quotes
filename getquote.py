import json
import random
import sys
from pathlib import Path
import shutil
import textwrap
from collections import Counter

GREEN = "\033[32m"
GRAY = "\033[90m"
RESET = "\033[0m"

QUOTES_FILE = "quotes.json"


def get_terminal_width(margin=4, min_width=40):
    width = shutil.get_terminal_size(fallback=(80, 20)).columns - margin
    return max(min_width, width)


def wrap_text(text, width):
    return textwrap.fill(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False
    )


def parse_args(argv):
    category_filter = None
    author_filter = None
    list_authors = False
    list_categories = False

    for arg in argv[1:]:
        if arg.startswith("--category="):
            category_filter = arg.split("=", 1)[1].strip()
        elif arg.startswith("--suthor="):   # soporta el nombre que has pedido
            author_filter = arg.split("=", 1)[1].strip()
        elif arg.startswith("--author="):   # alias sensato
            author_filter = arg.split("=", 1)[1].strip()
        elif arg == "--list-autors":        # respetando tu nombre pedido
            list_authors = True
        elif arg == "--list-authors":       # alias correcto
            list_authors = True
        elif arg == "--list_categories":
            list_categories = True
        else:
            print(f"Parámetro no reconocido: {arg}", file=sys.stderr)
            sys.exit(1)

    return category_filter, author_filter, list_authors, list_categories


def load_quotes():
    quotes_path = Path(__file__).with_name(QUOTES_FILE)

    try:
        with quotes_path.open("r", encoding="utf-8") as f:
            quotes = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"No se encuentra {QUOTES_FILE}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"JSON inválido en {QUOTES_FILE}: {e}")

    if not quotes:
        raise SystemExit(f"{QUOTES_FILE} está vacío.")

    return quotes


def filter_quotes(quotes, category_filter=None, author_filter=None):
    filtered = quotes

    if category_filter:
        filtered = [
            q for q in filtered
            if q.get("category", "").strip().lower() == category_filter.lower()
        ]

    if author_filter:
        filtered = [
            q for q in filtered
            if q.get("author", "").strip().lower() == author_filter.lower()
        ]

    return filtered


def print_author_list(quotes):
    counts = Counter(q.get("author", "Desconocido").strip() or "Desconocido" for q in quotes)
    for author in sorted(counts, key=lambda s: s.lower()):
        print(f"- {author} ({counts[author]})")


def print_category_list(quotes):
    counts = Counter(q.get("category", "Sin categoría").strip() or "Sin categoría" for q in quotes)
    for category in sorted(counts, key=lambda s: s.lower()):
        print(f"- {category} ({counts[category]})")


def print_random_quote(quotes):
    q = random.choice(quotes)

    text = q.get("quote", "").strip()
    author = q.get("author", "").strip()
    ref = q.get("ref", "").strip()
    category = q.get("category", "").strip()

    width = get_terminal_width()

    author_colored = f"{GREEN}{author}{RESET}" if author else ""
    meta_parts = []

    if ref:
        meta_parts.append(ref)
    if category:
        meta_parts.append(category)

    meta = " · ".join(meta_parts)
    meta_colored = f"{GRAY}{meta}{RESET}\n" if meta else ""

    print(wrap_text(f"«{text}».", width))
    print(f"\n{author_colored}")
    if meta_colored:
        print(meta_colored)

    print(f"{len(quotes)} quotes\n")


def main():
    category_filter, author_filter, list_authors, list_categories = parse_args(sys.argv)
    quotes = load_quotes()

    # Los listados se hacen sobre el conjunto completo
    if list_authors:
        print_author_list(quotes)
        return

    if list_categories:
        print_category_list(quotes)
        return

    quotes = filter_quotes(quotes, category_filter, author_filter)

    if not quotes:
        filters = []
        if category_filter:
            filters.append(f"category={category_filter}")
        if author_filter:
            filters.append(f"author={author_filter}")
        raise SystemExit("No hay citas para el filtro: " + ", ".join(filters))

    print_random_quote(quotes)


if __name__ == "__main__":
    main()