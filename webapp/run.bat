@echo off
setlocal
py -3.11 -m uvicorn app:app --reload --log-level debug
endlocal