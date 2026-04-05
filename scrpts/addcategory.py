#!/usr/bin/env python3

import json
import sys

CATEGORY_MAP = {
    "Alan Turing": "Informática",
    "Arnold J. Toynbee": "Filosofía",
    "Arthur Schopenhauer": "Filósofía",
    "Carl Jung": "Filósofía",
    "Carl von Clausewitz": "Milicia",
    "Cicerón": "Filósofía",
    "David Lane": "Filósofía",
    "Dennis Ritchie": "Informática",
    "Donald E. Knuth": "Informática",
    "Edsger W. Dijkstra": "Informática",
    "Epicteto": "Filosofía",
    "Ernst Jünger": "Filosofía",
    "Federico II de Prusia": "Milicia",
    "Ferdinand Porsche": "IngAutomotriz",
    "Friedrich Nietzsche": "Filosofía",
    "Henry Ford": "IngAutomotriz",
    "Hugo Junkers": "IngAeronáutica",
    "Immanuel Kant": "Filosofía",
    "John von Neumann": "Informática",
    "Marco Aurelio": "Filosofía",
    "Mark Twain": "Literatura",
    "Miyamoto Musashi": "Milicia",
    "Oswald Spengler": "Filosofía",
    "Otto Skorzeny": "Milicia",
    "Otto von Bismarck": "Milicia",
    "Richard Feynman": "Física",
    "Séneca": "Filosofía",
    "Ted Kaczynski": "Filosofía",
    "Wernher von Braun": "IngAeroespacial",
    "Willy Messerschmitt": "IngAeronáutica"
}


def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} quotes.json")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        author = item.get("author")
        item["category"] = CATEGORY_MAP.get(author, "Otros")

    # Sobrescribe el archivo (haz copia si quieres ir seguro)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()