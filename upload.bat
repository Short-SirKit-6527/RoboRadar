cmd /c "build.bat"
py -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pause
py -m twine upload dist/*
pause