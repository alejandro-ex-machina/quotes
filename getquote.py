import json
import random
from pathlib import Path
import shutil
import textwrap

GREEN = "\033[32m"
GRAY = "\033[90m"
RESET = "\033[0m"

QUOTES_FILE  = "quotes.json"


with Path(__file__).with_name(QUOTES_FILE).open ("r", encoding="utf-8" ) as f:
    quotes = json.load (f)

if not quotes:
    raise SystemExit ( QUOTES_FILE + " esta vacio." )

def get_terminal_width ( margin=4, min_width=40 ) :
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
    quote = random.choice (quotes)
    
    # Obtener valores y formatear

    text   = quote.get ("quote", "").strip()
    author = quote.get ("author", "").strip()
    ref    = quote.get ("ref", "").strip() if quote.get ("ref", "").strip() else ""

    #  Color

    author = f"{GREEN}{author}{RESET}"

    if ref:
        ref = f"{GRAY}{ref}{RESET}\n"
    else:
        ref = ""

    width = get_terminal_width()

    # Maquetar y salida

    print ( wrap_text( f'«{text}».' , width) )
    print ( f'\n{author}' )
    print ( f'{ref}' )

    print ( len(quotes), "quotes\n" )

if __name__ == "__main__":
    quote()
