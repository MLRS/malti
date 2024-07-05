#!/bin/bash
set -e

conda shell.bash activate venv/

echo "#########################################"
echo "mypy"
echo "..checking tools"
python -m mypy tools/
echo "..checking tests"
python -m mypy tests/
echo "..checking malti"
python -m mypy src/malti/
echo ""

echo "#########################################"
echo "pylint"
echo "..checking tools"
python -m pylint tools/
echo "..checking tests"
python -m pylint tests/
echo "..checking malti"
python -m pylint src/malti/
echo ""

echo "#########################################"
echo "sphinx api documentation"
python tools/sphinx_api_doc_maker.py
echo ""

echo "#########################################"
echo "project validation"
python tools/validate_project.py
echo ""

echo "#########################################"
echo "sphinx"
cd docs
make html
cd ..
echo ""

echo "#########################################"
echo "unittest"
cd tests
python -m unittest
cd ..
echo ""
