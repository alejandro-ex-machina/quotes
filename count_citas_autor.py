#!/usr/bin/env python3

import sys
import json
from collections import Counter


def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <archivo.json>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        sys.exit(1)

    # Contar citas por autor
    counts = Counter(item.get("author", "Desconocido") for item in data)

    # Orden alfabético por autor
    for author in sorted(counts):
        print(f"- {author} ({counts[author]})")


if __name__ == "__main__":
    main()