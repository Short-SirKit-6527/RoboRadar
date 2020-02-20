cmd /c "build.bat"
py -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
timeout 60
py -m twine upload dist/*
timeout 60
pip install --upgrade roboradar
