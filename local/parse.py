
from . import source


def inspect(path, onlyName):
    if onlyName:
        return source.processFileName(path)
    return source.processDirName(path) or \
            source.processFileName(path)
