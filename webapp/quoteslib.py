from __future__ import annotations

import json
import random
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable


CATEGORY_ALIASES = {
    "ingenieria": {
        "Ingeniería",
        "Ingeniería Aeroespacial",
        "Ingeniería Aeronáutica",
        "Ingeniería Automotriz",
    },
    "aeroespacial": {"Ingeniería Aeroespacial"},
    "aeronautica": {"Ingeniería Aeronáutica"},
    "automotriz": {"Ingeniería Automotriz"},
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.lower().strip().split())


def load_quotes(quotes_file: str | Path) -> list[dict]:
    quotes_path = Path(quotes_file)
    with quotes_path.open("r", encoding="utf-8") as f:
        quotes = json.load(f)

    if not isinstance(quotes, list):
        raise ValueError(f"{quotes_path} no contiene una lista JSON válida.")

    out = []
    for q in quotes:
        if not isinstance(q, dict):
            continue
        item = dict(q)
        item.setdefault("theme", "")
        out.append(item)
    return out


def matches_partial(value: str, expected: str) -> bool:
    return normalize(expected) in normalize(value)


def category_match(quote_category: str, query_category: str) -> bool:
    query_norm = normalize(query_category)
    cat_norm = normalize(quote_category)

    if not query_norm:
        return True
    if cat_norm == query_norm:
        return True
    if query_norm in CATEGORY_ALIASES:
        expanded = {normalize(x) for x in CATEGORY_ALIASES[query_norm]}
        return cat_norm in expanded

    return query_norm in cat_norm


def filter_quotes(
    quotes: Iterable[dict],
    *,
    text: str | None = None,
    category: str | None = None,
    author: str | None = None,
    theme: str | None = None,
    hardcore: bool = False,
    quality: str | None = None,
) -> list[dict]:
    filtered = list(quotes)

    if text:
        text_norm = normalize(text)
        filtered = [
            q for q in filtered
            if text_norm in normalize(q.get("quote", ""))
            or text_norm in normalize(q.get("author", ""))
            or text_norm in normalize(q.get("ref", ""))
            or text_norm in normalize(q.get("category", ""))
            or text_norm in normalize(q.get("theme", ""))
        ]

    if category:
        filtered = [q for q in filtered if category_match(q.get("category", ""), category)]

    if author:
        filtered = [q for q in filtered if matches_partial(q.get("author", ""), author)]

    if theme:
        filtered = [q for q in filtered if normalize(q.get("theme", "")) == normalize(theme)]

    if hardcore:
        filtered = [q for q in filtered if bool(q.get("hardcore", False))]

    if quality:
        filtered = [
            q for q in filtered
            if normalize(q.get("source_quality", "medium")) == normalize(quality)
        ]

    return filtered


def random_quote(quotes: Iterable[dict]) -> dict | None:
    quotes = list(quotes)
    return random.choice(quotes) if quotes else None


def counter_values(quotes: Iterable[dict], field: str, empty_label: str) -> list[tuple[str, int]]:
    counter = Counter()
    for q in quotes:
        value = str(q.get(field, "")).strip() or empty_label
        counter[value] += 1
    return sorted(counter.items(), key=lambda x: normalize(x[0]))
