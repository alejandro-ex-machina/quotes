#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path


DEFAULT_TARGET = "quotes.json"
REQUIRED_KEYS = ("author", "quote", "category", "theme")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.lower().strip().split())


def dedupe_key(item: dict) -> tuple[str, str]:
    return (
        normalize(item.get("author", "")),
        normalize(item.get("quote", "")),
    )


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise SystemExit(f"No se encuentra el archivo: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON inválido en {path}: {exc}")


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def ensure_list_of_dicts(data, path: Path, label: str) -> list[dict]:
    if not isinstance(data, list):
        raise SystemExit(f"{label} debe contener una lista JSON en {path}")
    if not all(isinstance(x, dict) for x in data):
        raise SystemExit(f"{label} debe contener solo objetos JSON en {path}")
    return data


def normalize_item(item: dict) -> dict:
    out = dict(item)

    # Claves mínimas
    for key in REQUIRED_KEYS:
        if key not in out:
            out[key] = ""

    # Limpieza básica
    for key, value in list(out.items()):
        if isinstance(value, str):
            out[key] = value.strip()

    # Siempre presente
    out["theme"] = str(out.get("theme", "")).strip()

    return out


def validate_item(item: dict, index: int, source_name: str):
    missing_hard = [k for k in ("author", "quote", "category") if not str(item.get(k, "")).strip()]
    if missing_hard:
        joined = ", ".join(missing_hard)
        raise SystemExit(
            f"Entrada {index} de {source_name} inválida: faltan campos obligatorios con contenido: {joined}"
        )


def make_backup(target: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_suffix(target.suffix + f".bak.{timestamp}")
    shutil.copy2(target, backup)
    return backup


def merge_quotes(
    target_quotes: list[dict],
    incoming_quotes: list[dict],
    replace: bool = False,
) -> tuple[list[dict], dict]:
    merged = list(target_quotes)
    index_by_key = {dedupe_key(item): i for i, item in enumerate(merged)}

    stats = Counter()
    stats["before"] = len(target_quotes)
    stats["incoming"] = len(incoming_quotes)

    for item in incoming_quotes:
        key = dedupe_key(item)

        if key in index_by_key:
            if replace:
                merged[index_by_key[key]] = item
                stats["replaced"] += 1
            else:
                stats["skipped_duplicates"] += 1
        else:
            merged.append(item)
            index_by_key[key] = len(merged) - 1
            stats["added"] += 1

    stats["after"] = len(merged)
    return merged, dict(stats)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Incorpora citas desde un JSON a quotes.json, con backup y deduplicación."
    )
    parser.add_argument(
        "input_json",
        help="JSON de entrada con una lista de citas a incorporar."
    )
    parser.add_argument(
        "--target",
        default=DEFAULT_TARGET,
        help="Ruta al quotes.json destino. Por defecto: quotes.json"
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Si una cita ya existe (autor+cita), reemplaza la entrada existente."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No escribe cambios; solo muestra qué haría."
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="No crea copia de seguridad del fichero destino."
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        help="Ordena el resultado por categoría, autor y cita."
    )
    parser.add_argument(
        "--strict-theme",
        action="store_true",
        help='Falla si alguna entrada no trae la clave "theme" (aunque esté vacía).'
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = Path(args.input_json).expanduser().resolve()
    target_path = Path(args.target).expanduser().resolve()

    incoming_raw = load_json(input_path)
    incoming_quotes = ensure_list_of_dicts(incoming_raw, input_path, "El JSON de entrada")

    if target_path.exists():
        target_raw = load_json(target_path)
        target_quotes = ensure_list_of_dicts(target_raw, target_path, "El JSON destino")
    else:
        target_quotes = []

    normalized_incoming = []
    for i, item in enumerate(incoming_quotes, start=1):
        if args.strict_theme and "theme" not in item:
            raise SystemExit(
                f'Entrada {i} de {input_path.name} inválida: falta la clave "theme".'
            )
        normalized = normalize_item(item)
        validate_item(normalized, i, input_path.name)
        normalized_incoming.append(normalized)

    normalized_target = [normalize_item(item) for item in target_quotes]

    merged, stats = merge_quotes(
        normalized_target,
        normalized_incoming,
        replace=args.replace,
    )

    if args.sort:
        merged.sort(
            key=lambda q: (
                normalize(q.get("category", "")),
                normalize(q.get("author", "")),
                normalize(q.get("quote", "")),
            )
        )

    print(f"Destino:  {target_path}")
    print(f"Entrada:  {input_path}")
    print(f"Inicial:  {stats['before']}")
    print(f"Nuevas:   {stats['incoming']}")
    print(f"Añadidas: {stats.get('added', 0)}")
    print(f"Saltadas: {stats.get('skipped_duplicates', 0)}")
    print(f"Reemplaz.: {stats.get('replaced', 0)}")
    print(f"Final:    {stats['after']}")

    if args.dry_run:
        print("\nModo dry-run: no se ha escrito ningún fichero.")
        return

    backup_path = None
    if target_path.exists() and not args.no_backup:
        backup_path = make_backup(target_path)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(target_path, merged)

    if backup_path:
        print(f"\nBackup:   {backup_path}")
    print(f"Escrito:  {target_path}")


if __name__ == "__main__":
    main()
