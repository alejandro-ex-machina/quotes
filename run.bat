@echo off
setlocal
rem py -3.11 -m pip install -r requirements.txt
py -3.11 -m uvicorn app:app --reload
endlocal

















