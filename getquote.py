import json
import random
import sys
from pathlib import Path
import shutil
import textwrap

GREEN = "\033[32m"
GRAY = "\033[90m"
RESET = "\033[0m"

QUOTES_FILE = "quotes.json"


# --- Parseo simple de argumentos ---
category_filter = None
for arg in sys.argv[1:]:
    if arg.startswith("--category="):
        category_filter = arg.split("=", 1)[1].strip()


with Path(__file__).with_name(QUOTES_FILE).open("r", encoding="utf-8") as f:
    quotes = json.load(f)

if not quotes:
    raise SystemExit(QUOTES_FILE + " está vacío.")


# --- Filtrado ---
if category_filter:
    quotes = [q for q in quotes if q.get("category") == category_filter]

    if not quotes:
        raise SystemExit(f"No hay citas para la categoría: {category_filter}")


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


def quote() -> None:
    q = random.choice(quotes)

    text = q.get("quote", "").strip()
    author = q.get("author", "").strip()
    ref = q.get("ref", "").strip() if q.get("ref", "").strip() else ""

    author = f"{GREEN}{author}{RESET}"
    ref = f"{GRAY}{ref}{RESET}\n" if ref else ""

    width = get_terminal_width()

    print(wrap_text(f'«{text}».', width))
    print(f'\n{author}')
    print(f'{ref}')

    print(len(quotes), "quotes\n")


if __name__ == "__main__":
    quote()