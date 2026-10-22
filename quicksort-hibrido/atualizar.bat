@echo off
REM Envia esta versao para https://github.com/Arthur-Gmb/quicksort-hibrido
cd /d "%~dp0"
git remote get-url origin >nul 2>nul || git remote add origin https://github.com/Arthur-Gmb/quicksort-hibrido.git
git push -u origin main
echo.
echo Pronto. Falta so ligar o GitHub Pages:
echo Settings ^> Pages ^> Branch: main ^> pasta /docs ^> Save
start https://github.com/Arthur-Gmb/quicksort-hibrido/settings/pages
pause
