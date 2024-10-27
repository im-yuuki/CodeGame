@echo off

cd /d %~dp0

set PYTHONIOENCODING=utf-8

@if exist .venv (
    .venv\Scripts\python.exe src\main.py
) else (
    python src\main.py
)