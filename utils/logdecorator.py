import logging

def log_calls(func):
    """Decorator that logs function calls."""
    def wrapper(*args, **kwargs):
        logging.info(f"Called function: {func.__name__} | args: {args} | kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper


def log_all_methods(cls):
    for attr_name, attr_value in list(cls.__dict__.items()):
        if callable(attr_value) and not attr_name.startswith("__") and attr_name != "__repr__":
            setattr(cls, attr_name, log_calls(attr_value))
    return cls
