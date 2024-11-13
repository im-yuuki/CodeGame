#!/bin/bash

cd "$(dirname "$0")" || exit

export PYTHONIOENCODING=utf-8

if [ -d ".venv" ]; then
    .venv/Scripts/python main.py
else
    python main.py
fi