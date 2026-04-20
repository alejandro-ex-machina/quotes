@echo off
setlocal

REM Quotes workflow helper for Windows
REM Usage:
REM   quotes_toolkit.bat review
REM   quotes_toolkit.bat random
REM   quotes_toolkit.bat list themes
REM   quotes_toolkit.bat merge nuevas.json
REM   quotes_toolkit.bat merge nuevas.json --replace
REM   quotes_toolkit.bat check

set "ROOT=%~dp0"
set "PY=python"
set "GET=%ROOT%scrpts\getquote.py"
set "MERGE=%ROOT%scrpts\merge_quotes.py"
set "REVIEW=%ROOT%scrpts\review_quotes.py"
set "QUOTES=%ROOT%quotes.json"

if "%~1"=="" goto :help

if /I "%~1"=="random" (
  %PY% "%GET%" --quotes-file "%QUOTES%"
  goto :end
)

if /I "%~1"=="review" (
  %PY% "%REVIEW%" --quotes-file "%QUOTES%"
  goto :end
)

if /I "%~1"=="report" (
  %PY% "%REVIEW%" --quotes-file "%QUOTES%" --report "%ROOT%quotes_review.md"
  goto :end
)

if /I "%~1"=="check" (
  %PY% "%REVIEW%" --quotes-file "%QUOTES%" --report "%ROOT%quotes_review.md"
  if errorlevel 1 goto :error
  echo.
  echo Informe generado en quotes_review.md
  goto :end
)

if /I "%~1"=="merge" (
  if "%~2"=="" (
    echo Falta el JSON de entrada.
    goto :help
  )
  shift
  set "INPUT=%~1"
  shift
  %PY% "%MERGE%" "%INPUT%" --target "%QUOTES%" %*
  goto :end
)

if /I "%~1"=="list" (
  if /I "%~2"=="authors" (
    %PY% "%GET%" --quotes-file "%QUOTES%" --list_authors
    goto :end
  )
  if /I "%~2"=="categories" (
    %PY% "%GET%" --quotes-file "%QUOTES%" --list_categories
    goto :end
  )
  if /I "%~2"=="themes" (
    %PY% "%GET%" --quotes-file "%QUOTES%" --list_themes
    goto :end
  )
  echo Valor no reconocido para list: %~2
  goto :help
)

if /I "%~1"=="theme" (
  if "%~2"=="" (
    echo Falta el theme.
    goto :help
  )
  %PY% "%GET%" --quotes-file "%QUOTES%" --theme="%~2" --all
  goto :end
)

if /I "%~1"=="author" (
  if "%~2"=="" (
    echo Falta el autor.
    goto :help
  )
  %PY% "%GET%" --quotes-file "%QUOTES%" --author="%~2" --all
  goto :end
)

if /I "%~1"=="category" (
  if "%~2"=="" (
    echo Falta la categoria.
    goto :help
  )
  %PY% "%GET%" --quotes-file "%QUOTES%" --category="%~2" --all
  goto :end
)

:help
echo.
echo Quotes Toolkit - helper para Windows
echo.
echo Uso:
echo   %~nx0 random
echo   %~nx0 review
echo   %~nx0 report
echo   %~nx0 check
echo   %~nx0 merge nuevas.json [--replace] [--sort] [--strict-theme]
echo   %~nx0 list authors^|categories^|themes
echo   %~nx0 theme "etica"
echo   %~nx0 author "Unamuno"
echo   %~nx0 category "Ingenieria"
echo.
goto :end

:error
echo.
echo Ha fallado la revision.
exit /b 1

:end
endlocal
