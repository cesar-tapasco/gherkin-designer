import os
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

env_path = os.getenv("ENV_PATH")
if env_path:
  load_dotenv(dotenv_path=f"{env_path}.env", override=True)


class Config:
  BASE_URL = os.getenv("BASE_URL", "https://api-dev.healthnexus.io")

  def __init__(self):
    self.should_exist(self.BASE_URL != "", "BASE_URL")

  def should_exist(self, conditional, name):
    if not conditional:
      raise ValueError(f"{name} environment variable is not set")

  def get(self, attribute_name: str, default=None):
    """
    Get a config attribute by name dynamically.

    Args:
        attribute_name (str): The name of the attribute to retrieve
        default: Default value to return if attribute doesn't exist

    Returns:
        The attribute value or default if not found
    """
    if hasattr(self, attribute_name):
      return getattr(self, attribute_name)
    return default


class ConfigDict(TypedDict):
  config: Config
