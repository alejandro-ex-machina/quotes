from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[2]
WEBAPP_DIR = ROOT_DIR / "webapp"

if str(WEBAPP_DIR) not in sys.path:
    sys.path.insert(0, str(WEBAPP_DIR))

from app import app  # noqa: E402

client = TestClient(app)


def _first_link(html: str, prefix: str) -> str:
    links = re.findall(r'href="([^"]+)"', html)
    for href in links:
        path = urlsplit(href).path
        if path.startswith(prefix):
            return path
    raise AssertionError(f"No link found with prefix {prefix!r}")


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert isinstance(payload["quotes"], int)


def test_core_list_pages_render() -> None:
    for path in ("/", "/authors", "/themes", "/categories"):
        response = client.get(path)
        assert response.status_code == 200


def test_home_serves_random_quote_card() -> None:
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "Cita aleatoria" in html
    assert "ml-quote-card" in html
    assert 'title="Copiar cita"' in html


def test_theme_detail_uses_new_layout() -> None:
    themes_page = client.get("/themes")
    assert themes_page.status_code == 200
    theme_link = _first_link(themes_page.text, "/themes/")

    detail = client.get(theme_link)
    assert detail.status_code == 200
    html = detail.text
    assert "ml-author-wrap" in html
    assert "ml-quote-list" in html
    assert 'title="Copiar cita"' in html


def test_category_detail_uses_new_layout() -> None:
    categories_page = client.get("/categories")
    assert categories_page.status_code == 200
    category_link = _first_link(categories_page.text, "/categories/")

    detail = client.get(category_link)
    assert detail.status_code == 200
    html = detail.text
    assert "ml-author-wrap" in html
    assert "ml-quote-list" in html
    assert 'title="Copiar cita"' in html
