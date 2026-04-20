#!/usr/bin/env python3
import argparse
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_QUOTES_FILE = "quotes.json"
DEFAULT_CANONICAL_THEMES = [
    "acción",
    "carácter",
    "disciplina",
    "pensamiento",
    "pragmatismo",
    "creación",
    "técnica",
    "estrategia",
    "guerra",
    "ética",
    "tiempo",
    "sociedad",
    "vínculos",
    "estilo",
    "",
]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.lower().strip().split())


def load_quotes(path: Path) -> list[dict]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        raise SystemExit(f"No se encuentra el archivo: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON inválido en {path}: {exc}")

    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise SystemExit(f"{path} debe contener una lista JSON de objetos.")

    return data


def dedupe_key(item: dict) -> tuple[str, str]:
    return (
        normalize(item.get("author", "")),
        normalize(item.get("quote", "")),
    )


def author_quote_signature(item: dict) -> str:
    author = str(item.get("author", "")).strip() or "Desconocido"
    quote = str(item.get("quote", "")).strip()
    return f"{author} :: {quote}"


def quote_text_signature(item: dict) -> str:
    return normalize(item.get("quote", ""))


def bigram_jaccard(a: str, b: str) -> float:
    a = normalize(a)
    b = normalize(b)

    if not a or not b:
        return 0.0

    def bigrams(s: str) -> set[str]:
        if len(s) < 2:
            return {s}
        return {s[i:i+2] for i in range(len(s) - 1)}

    ba = bigrams(a)
    bb = bigrams(b)
    union = ba | bb
    if not union:
        return 0.0
    return len(ba & bb) / len(union)


def suspicious_near_duplicates(quotes: list[dict], threshold: float = 0.86, max_pairs: int = 100):
    pairs = []
    seen = set()

    for i in range(len(quotes)):
        qi = quotes[i]
        ai = normalize(qi.get("author", ""))
        ti = normalize(qi.get("quote", ""))

        if not ai or not ti:
            continue

        for j in range(i + 1, len(quotes)):
            qj = quotes[j]
            aj = normalize(qj.get("author", ""))
            tj = normalize(qj.get("quote", ""))

            if not aj or not tj:
                continue

            same_author = ai == aj
            same_quote = ti == tj
            if same_author and same_quote:
                continue

            # Solo comparamos si comparten autor o si el texto es muy parecido
            score = bigram_jaccard(ti, tj)
            if same_author or score >= threshold:
                key = tuple(sorted((author_quote_signature(qi), author_quote_signature(qj))))
                if key not in seen:
                    seen.add(key)
                    pairs.append({
                        "score": round(score, 3),
                        "left": qi,
                        "right": qj,
                        "same_author": same_author,
                    })

            if len(pairs) >= max_pairs:
                return sorted(pairs, key=lambda x: (-x["score"], not x["same_author"]))

    return sorted(pairs, key=lambda x: (-x["score"], not x["same_author"]))


def report_missing_refs(quotes: list[dict]) -> list[dict]:
    return [q for q in quotes if not str(q.get("ref", "")).strip()]


def report_missing_theme_key(quotes: list[dict]) -> list[dict]:
    return [q for q in quotes if "theme" not in q]


def report_empty_theme(quotes: list[dict]) -> list[dict]:
    return [q for q in quotes if not str(q.get("theme", "")).strip()]


def report_invalid_themes(quotes: list[dict], canonical_themes: list[str]) -> list[dict]:
    allowed = {normalize(t) for t in canonical_themes}
    bad = []
    for q in quotes:
        theme = normalize(q.get("theme", ""))
        if theme not in allowed:
            bad.append(q)
    return bad


def report_missing_required(quotes: list[dict]) -> list[dict]:
    bad = []
    for q in quotes:
        if not str(q.get("author", "")).strip() or not str(q.get("quote", "")).strip() or not str(q.get("category", "")).strip():
            bad.append(q)
    return bad


def count_by_field(quotes: list[dict], field: str, default: str) -> Counter:
    c = Counter()
    for q in quotes:
        value = str(q.get(field, "")).strip() or default
        c[value] += 1
    return c


def low_quality_by_author(quotes: list[dict], min_count: int = 2) -> dict[str, int]:
    counts = Counter()
    for q in quotes:
        quality = normalize(q.get("source_quality", ""))
        if quality == "low":
            author = str(q.get("author", "")).strip() or "Desconocido"
            counts[author] += 1
    return {k: v for k, v in counts.items() if v >= min_count}


def exact_duplicates(quotes: list[dict]) -> list[list[dict]]:
    groups = defaultdict(list)
    for q in quotes:
        groups[dedupe_key(q)].append(q)
    return [items for items in groups.values() if len(items) > 1]


def format_quote(q: dict) -> str:
    author = str(q.get("author", "")).strip() or "Desconocido"
    quote = str(q.get("quote", "")).strip()
    ref = str(q.get("ref", "")).strip()
    category = str(q.get("category", "")).strip()
    theme = str(q.get("theme", "")).strip()

    parts = [f"- {author}: «{quote}»"]
    meta = []
    if ref:
        meta.append(ref)
    if category:
        meta.append(f"category={category}")
    if theme or "theme" in q:
        meta.append(f"theme={theme}")
    if meta:
        parts.append(f"  [{' · '.join(meta)}]")
    return "\n".join(parts)


def build_report(quotes: list[dict], canonical_themes: list[str], near_dup_threshold: float) -> str:
    lines = []
    lines.append("# Revisión de quotes.json")
    lines.append("")
    lines.append(f"Total de citas: {len(quotes)}")
    lines.append("")

    missing_required = report_missing_required(quotes)
    missing_refs = report_missing_refs(quotes)
    missing_theme_key = report_missing_theme_key(quotes)
    empty_theme = report_empty_theme(quotes)
    invalid_themes = report_invalid_themes(quotes, canonical_themes)
    duplicates = exact_duplicates(quotes)
    near_dups = suspicious_near_duplicates(quotes, threshold=near_dup_threshold)
    quality_counts = count_by_field(quotes, "source_quality", "sin_quality")
    theme_counts = count_by_field(quotes, "theme", "sin_theme")
    category_counts = count_by_field(quotes, "category", "sin_category")
    low_quality_authors = low_quality_by_author(quotes)

    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Entradas con campos obligatorios incompletos: {len(missing_required)}")
    lines.append(f"- Entradas sin ref: {len(missing_refs)}")
    lines.append(f'- Entradas sin clave "theme": {len(missing_theme_key)}')
    lines.append(f"- Entradas con theme vacío: {len(empty_theme)}")
    lines.append(f"- Entradas con theme fuera del canon: {len(invalid_themes)}")
    lines.append(f"- Grupos de duplicados exactos: {len(duplicates)}")
    lines.append(f"- Posibles duplicados semánticos: {len(near_dups)}")
    lines.append("")

    lines.append("## Calidad")
    lines.append("")
    for key in sorted(quality_counts, key=lambda k: normalize(k)):
        lines.append(f"- {key}: {quality_counts[key]}")
    lines.append("")

    lines.append("## Themes")
    lines.append("")
    for key in sorted(theme_counts, key=lambda k: normalize(k)):
        lines.append(f"- {key!r}: {theme_counts[key]}")
    lines.append("")

    lines.append("## Categorías")
    lines.append("")
    for key in sorted(category_counts, key=lambda k: normalize(k)):
        lines.append(f"- {key}: {category_counts[key]}")
    lines.append("")

    if low_quality_authors:
        lines.append("## Autores con varias citas de calidad baja")
        lines.append("")
        for author in sorted(low_quality_authors, key=lambda k: normalize(k)):
            lines.append(f"- {author}: {low_quality_authors[author]}")
        lines.append("")

    if missing_required:
        lines.append("## Entradas con campos obligatorios incompletos")
        lines.append("")
        for q in missing_required[:25]:
            lines.append(format_quote(q))
        lines.append("")

    if missing_refs:
        lines.append("## Entradas sin ref")
        lines.append("")
        for q in missing_refs[:50]:
            lines.append(format_quote(q))
        lines.append("")

    if missing_theme_key:
        lines.append('## Entradas sin clave "theme"')
        lines.append("")
        for q in missing_theme_key[:25]:
            lines.append(format_quote(q))
        lines.append("")

    if empty_theme:
        lines.append("## Entradas con theme vacío")
        lines.append("")
        for q in empty_theme[:50]:
            lines.append(format_quote(q))
        lines.append("")

    if invalid_themes:
        lines.append("## Entradas con theme fuera del canon")
        lines.append("")
        for q in invalid_themes[:50]:
            lines.append(format_quote(q))
        lines.append("")

    if duplicates:
        lines.append("## Duplicados exactos")
        lines.append("")
        for idx, group in enumerate(duplicates[:25], start=1):
            lines.append(f"### Grupo {idx}")
            lines.append("")
            for q in group:
                lines.append(format_quote(q))
            lines.append("")

    if near_dups:
        lines.append("## Posibles duplicados semánticos")
        lines.append("")
        for idx, pair in enumerate(near_dups[:50], start=1):
            lines.append(f"### Par {idx} · score={pair['score']} · mismo_autor={pair['same_author']}")
            lines.append("")
            lines.append(format_quote(pair["left"]))
            lines.append("")
            lines.append(format_quote(pair["right"]))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Revisa quotes.json y genera un informe de calidad y consistencia."
    )
    parser.add_argument(
        "--quotes-file",
        default=DEFAULT_QUOTES_FILE,
        help="Ruta al fichero JSON de citas. Por defecto: quotes.json"
    )
    parser.add_argument(
        "--report",
        help="Ruta del informe de salida en texto/markdown. Si no se indica, imprime por pantalla."
    )
    parser.add_argument(
        "--near-dup-threshold",
        type=float,
        default=0.86,
        help="Umbral de similitud para posibles duplicados semánticos. Por defecto: 0.86"
    )
    parser.add_argument(
        "--canonical-theme",
        action="append",
        dest="canonical_themes",
        help="Añade un theme canónico permitido. Puede repetirse."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    quotes_path = Path(args.quotes_file).expanduser().resolve()
    quotes = load_quotes(quotes_path)

    canonical_themes = args.canonical_themes or DEFAULT_CANONICAL_THEMES
    report = build_report(quotes, canonical_themes, args.near_dup_threshold)

    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8", newline="\n")
        print(f"Informe escrito en: {report_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
