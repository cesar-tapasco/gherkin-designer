from functools import wraps
from config import Config


def check_env_vars(env_vars):
  """Validate if variables are defined in environment"""

  def decorator(func):
    config = Config()

    @wraps(func)
    def wrapper(*args, **kwargs):
      for element in env_vars:
        if not hasattr(config, element) or not getattr(config, element):
          raise ValueError(f"{element} configuration value must be set")
      result = func(*args, **kwargs)
      return result

    return wrapper

  return decorator


def parse_datatable():
  """Parses de datatable object into a dict"""

  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      if "datatable" in kwargs:
        datatable = kwargs["datatable"]
        kwargs["datatable"] = [dict(zip(datatable[0], row)) for row in datatable[1:]]
      result = func(*args, **kwargs)
      return result

    return wrapper

  return decorator
