@echo off
REM Publica este projeto no GitHub (conta Arthur-Gmb).
REM Requer Git instalado. Se o GitHub CLI (gh) estiver instalado e logado, cria o repositorio sozinho.
cd /d "%~dp0"
where gh >nul 2>nul
if %errorlevel%==0 (
  gh repo create Arthur-Gmb/quicksort-hibrido --public --source . --remote origin --push --description "Quicksort hibrido (quicksort + insercao): onde fica o ponto de troca"
) else (
  echo Crie antes um repositorio VAZIO chamado quicksort-hibrido em https://github.com/new
  pause
  git remote remove origin 2>nul
  git remote add origin https://github.com/Arthur-Gmb/quicksort-hibrido.git
  git push -u origin main
)
pause
