#!/bin/bash
set -e

conda shell.bash activate venv/

rm -f dist/*.*

call python -m build
call python -m twine upload dist/*
