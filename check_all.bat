@echo off

call conda activate venv\ || pause && exit /b

echo #########################################
echo mypy
echo ..checking tools
call python -m mypy tools\ || pause && exit /b
echo ..checking tests
call python -m mypy tests\ || pause && exit /b
echo ..checking malti
call python -m mypy src\malti\ || pause && exit /b
echo.

echo #########################################
echo pylint
echo ..checking tools
call python -m pylint tools\ || pause && exit /b
echo ..checking tests
call python -m pylint tests\ || pause && exit /b
echo ..checking malti
call python -m pylint src\malti\ || pause && exit /b
echo.

echo #########################################
echo sphinx api documentation
call python tools\sphinx_api_doc_maker.py || pause && exit /b
echo.

echo #########################################
echo project validation
call python tools\validate_project.py || pause && exit /b
echo.

echo #########################################
echo sphinx
cd docs
call make html || cd .. && pause && exit /b
cd ..
echo.

echo #########################################
echo unittest
cd tests
call python -m unittest || cd .. && pause && exit /b
cd ..
echo.
