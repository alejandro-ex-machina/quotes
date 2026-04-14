#!/data/data/com.termux/files/usr/bin/bash
set -e
python -m pip install -r requirements-termux.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000