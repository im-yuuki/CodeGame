#!/bin/bash

cd "$(dirname "$0")" || exit

export PYTHONIOENCODING=utf-8

if [ -d ".venv" ]; then
    .venv/Scripts/python src/main.py
else
    python src/main.py
fi