import importlib, os
fields = []
fieldFiles = {}
fieldNames = {}
fieldThemes = {}
for file in os.listdir(__file__[:-11]):
    if file.endswith(".py") and file != "__init__.py":
        if __package__:
            module = "." + file[:-3]
        else:
            module = file[:-3]
        fieldIndex = len(fields)
        fields.append(importlib.import_module(module, package=__package__))
        fieldFiles[fields[-1].Data["file"]] = fieldIndex #TODO: add version overriding
        fieldNames[fields[-1].Data["name"]] = fieldIndex
        fieldThemes[fields[-1].Data["theme"]] = fieldIndex
