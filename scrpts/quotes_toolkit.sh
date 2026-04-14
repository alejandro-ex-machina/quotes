#!/data/data/com.termux/files/usr/bin/bash
set -e

# Quotes workflow helper for Termux / Linux
# Usage:
#   ./quotes_toolkit.sh review
#   ./quotes_toolkit.sh random
#   ./quotes_toolkit.sh list themes
#   ./quotes_toolkit.sh merge nuevas.json
#   ./quotes_toolkit.sh merge nuevas.json --replace
#   ./quotes_toolkit.sh check

ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON_BIN:-python}"
GET="$ROOT/scrpts/getquote.py"
MERGE="$ROOT/scrpts/merge_quotes.py"
REVIEW="$ROOT/scrpts/review_quotes.py"
QUOTES="$ROOT/quotes.json"

help_msg() {
  cat <<'EOF'
Quotes Toolkit - helper para Termux / Linux

Uso:
  ./quotes_toolkit.sh random
  ./quotes_toolkit.sh review
  ./quotes_toolkit.sh report
  ./quotes_toolkit.sh check
  ./quotes_toolkit.sh merge nuevas.json [--replace] [--sort] [--strict-theme]
  ./quotes_toolkit.sh list authors|categories|themes
  ./quotes_toolkit.sh theme "ética"
  ./quotes_toolkit.sh author "Unamuno"
  ./quotes_toolkit.sh category "Ingeniería"

Variable opcional:
  PYTHON_BIN=python3 ./quotes_toolkit.sh review
EOF
}

if [ $# -lt 1 ]; then
  help_msg
  exit 0
fi

cmd="$1"
shift || true

case "$cmd" in
  random)
    "$PY" "$GET" --quotes-file "$QUOTES"
    ;;
  review)
    "$PY" "$REVIEW" --quotes-file "$QUOTES"
    ;;
  report)
    "$PY" "$REVIEW" --quotes-file "$QUOTES" --report "$ROOT/quotes_review.md"
    ;;
  check)
    "$PY" "$REVIEW" --quotes-file "$QUOTES" --report "$ROOT/quotes_review.md"
    echo
    echo "Informe generado en quotes_review.md"
    ;;
  merge)
    if [ $# -lt 1 ]; then
      echo "Falta el JSON de entrada."
      echo
      help_msg
      exit 1
    fi
    input="$1"
    shift || true
    "$PY" "$MERGE" "$input" --target "$QUOTES" "$@"
    ;;
  list)
    sub="${1:-}"
    case "$sub" in
      authors)
        "$PY" "$GET" --quotes-file "$QUOTES" --list_authors
        ;;
      categories)
        "$PY" "$GET" --quotes-file "$QUOTES" --list_categories
        ;;
      themes)
        "$PY" "$GET" --quotes-file "$QUOTES" --list_themes
        ;;
      *)
        echo "Valor no reconocido para list: $sub"
        echo
        help_msg
        exit 1
        ;;
    esac
    ;;
  theme)
    if [ $# -lt 1 ]; then
      echo "Falta el theme."
      echo
      help_msg
      exit 1
    fi
    "$PY" "$GET" --quotes-file "$QUOTES" --theme="$1" --all
    ;;
  author)
    if [ $# -lt 1 ]; then
      echo "Falta el autor."
      echo
      help_msg
      exit 1
    fi
    "$PY" "$GET" --quotes-file "$QUOTES" --author="$1" --all
    ;;
  category)
    if [ $# -lt 1 ]; then
      echo "Falta la categoría."
      echo
      help_msg
      exit 1
    fi
    "$PY" "$GET" --quotes-file "$QUOTES" --category="$1" --all
    ;;
  *)
    help_msg
    exit 1
    ;;
esac
