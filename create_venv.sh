#!/bin/bash
set -e

conda create --prefix venv/ python=3.9
conda shell.bash activate venv/

pip install -r requirements.txt
pip install -e .
