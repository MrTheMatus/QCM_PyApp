import logging

logging.basicConfig(level=logging.INFO)

def log_calls(func):
    """Decorator that logs function calls."""
    def wrapper(*args, **kwargs):
        logging.info(f"Called function: {func.__name__} | args: {args} | kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper


def log_all_methods(cls):
    """Class decorator to log calls to all methods of a class."""
    for attr_name, attr_value in list(cls.__dict__.items()):
        # Check if the attribute is a callable (i.e., a method or function)
        if callable(attr_value) and not attr_name.startswith("__"):
            # Wrap the original method with the log_calls decorator
            setattr(cls, attr_name, log_calls(attr_value))
    return cls
