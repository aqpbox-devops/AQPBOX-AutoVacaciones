def get_error(obj: object) -> str:
    attr = 'error'
    if not hasattr(obj, attr) and not isinstance(getattr(obj, attr), str):
        raise AttributeError(f"Atribute [error] not found in {type(obj).__name__}")
    
    return obj.error