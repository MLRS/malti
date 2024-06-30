@echo off

call conda create --prefix venv\ python=3.9 || pause && exit /b
call conda activate venv\ || pause && exit /b

call pip install -r requirements.txt || pause && exit /b
call pip install -e . || pause && exit /b
