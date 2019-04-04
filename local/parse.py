
from . import source


def inspect(path, onlyName=False):
    if onlyName:
        return source.processFileName(path)
    return source.processDirName(path) or \
            source.processFileName(path)
