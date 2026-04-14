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



@app.get("/themes", response_class=HTMLResponse)
def themes_page(request: Request):
    quotes = get_quotes()
    themes = [(name, count) for name, count in counter_values(quotes, "theme", "") if name]

    return templates.TemplateResponse(
        "themes.html",
        {
            "request": request,
            "themes": themes,
            "quotes_total": len(quotes),
        },
    )

@app.get("/themes/{theme}", response_class=HTMLResponse)
def theme_detail(request: Request, theme: str):
    quotes = get_quotes()
    results = filter_quotes(quotes, theme=theme)

    authors_in_theme = counter_values(results, "author", "Desconocido")
    categories_in_theme = counter_values(results, "category", "Sin categoría")

    return templates.TemplateResponse(
        "theme_detail.html",
        {
            "request": request,
            "theme": theme,
            "results": results[:200],
            "results_total": len(results),
            "authors_in_theme": authors_in_theme,
            "categories_in_theme": categories_in_theme,
        },
    )

@app.get("/authors", response_class=HTMLResponse)
def authors_page(request: Request):
    quotes = get_quotes()
    authors = counter_values(quotes, "author", "Desconocido")

    return templates.TemplateResponse(
        "authors.html",
        {
            "request": request,
            "authors": authors,
            "quotes_total": len(quotes),
        },
    )


@app.get("/authors/{author}", response_class=HTMLResponse)
def author_detail(request: Request, author: str):
    quotes = get_quotes()
    results = filter_quotes(quotes, author=author)

    themes_for_author = [(name, count) for name, count in counter_values(results, "theme", "") if name]
    categories_for_author = counter_values(results, "category", "Sin categoría")

    return templates.TemplateResponse(
        "author_detail.html",
        {
            "request": request,
            "author": author,
            "results": results[:200],
            "results_total": len(results),
            "themes_for_author": themes_for_author,
            "categories_for_author": categories_for_author,
        },
    )

@app.get("/categories", response_class=HTMLResponse)
def categories_page(request: Request):
    quotes = get_quotes()
    categories = counter_values(quotes, "category", "Sin categoría")

    return templates.TemplateResponse(
        "categories.html",
        {
            "request": request,
            "categories": categories,
            "quotes_total": len(quotes),
        },
    )


@app.get("/categories/{category}", response_class=HTMLResponse)
def category_details(request: Request, category: str):
    quotes = get_quotes()
    results = filter_quotes(quotes, category=category)

    authors_in_category = counter_values(results, "author", "Desconocido")
    themes_in_category = [(name, count) for name, count in counter_values(results, "theme", "") if name]

    return templates.TemplateResponse(
        "category_detail.html",
        {
            "request": request,
            "category": category,
            "results": results[:200],
            "results_total": len(results),
            "authors_in_category": authors_in_category,
            "themes_in_category": themes_in_category,
        },
    )