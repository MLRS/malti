@echo off

call conda activate venv\ || pause && exit /b

if exist dist\*.* del dist\*.*

call python -m build
call python -m twine upload dist/*
