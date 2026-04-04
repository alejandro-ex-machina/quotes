import json
import random
from pathlib import Path
from typing import Final

QUOTES_FILE  = Path(__file__).with_name("quotes.json")

with QUOTES_FILE.open ("r", encoding="utf-8") as f:
    quotes = json.load (f)

if not quotes:
    raise SystemExit ( QUOTES_FILE._str() + " esta vacio.")

def quote() -> None:
    quote = random.choice (quotes)
    
    text   = quote.get ("quote", "").strip()
    author = quote.get ("author", "").strip()
    ref    = " (" + quote.get ("ref", "").strip() + ")" if quote.get ("ref", "").strip() else ""

    author = "\033[1m"+ author + "\033[0m" + ref    

    print (f'\n«{text}».\n')
    print (f'{author}\n')


if __name__ == "__main__":
    quote()
