from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from quoteslib import counter_values, filter_quotes, load_quotes, random_quote


BASE_DIR = Path(__file__).resolve().parent
QUOTES_FILE = Path(os.getenv("QUOTES_FILE", BASE_DIR / "../quotes.json"))

app = FastAPI(title="Quotes Toolkit")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_quotes() -> list[dict]:
    return load_quotes(QUOTES_FILE)


@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    q: str | None = Query(default=None),
    author: str | None = Query(default=None),
    category: str | None = Query(default=None),
    theme: str | None = Query(default=None),
    quality: str | None = Query(default=None),
    hardcore: bool = Query(default=False),
    mode: str = Query(default="search"),
):
    quotes = get_quotes()
    filtered = filter_quotes(
        quotes,
        text=q,
        author=author,
        category=category,
        theme=theme,
        quality=quality,
        hardcore=hardcore,
    )

    random_result = random_quote(filtered or quotes) if mode == "random" else None

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "quotes_total": len(quotes),
            "results_total": len(filtered),
            "results": filtered[:200],
            "random_result": random_result,
            "authors": counter_values(quotes, "author", "Desconocido"),
            "categories": counter_values(quotes, "category", "Sin categoría"),
            "themes": counter_values(quotes, "theme", ""),
            "qualities": [("high", "high"), ("medium", "medium"), ("low", "low")],
            "params": {
                "q": q or "",
                "author": author or "",
                "category": category or "",
                "theme": theme or "",
                "quality": quality or "",
                "hardcore": hardcore,
            },
        },
    )


@app.get("/health")
def health():
    quotes = get_quotes()
    return {"ok": True, "quotes": len(quotes), "quotes_file": str(QUOTES_FILE)}
