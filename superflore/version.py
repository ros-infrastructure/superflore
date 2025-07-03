VERSION = 'unset'

try:
    import importlib.metadata
    try:
        VERSION = importlib.metadata.metadata("superflore").get("version")
    except importlib.metadata.PackageNotFoundError:
        pass
except (ImportError, OSError):
    pass
