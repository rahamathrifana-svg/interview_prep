@echo off
setlocal
cd /d "%~dp0"
if exist ".python-runtime\python.exe" (
  ".python-runtime\python.exe" backend.py
) else (
  py backend.py
)
