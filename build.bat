cd /D "%~dp0"
@RD /S /Q "dist"
py setup.py sdist bdist_wheel
pause