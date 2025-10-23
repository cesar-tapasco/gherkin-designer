import json
from src.utils.core.api import APIX
from config import Config, ConfigDict
from src.utils.logger import get_logger
from mimesis import Generic


class ClientConfig:
  def __init__(self, client_id: int = None, client_name: str = None):
    self.id = client_id
    self.name = client_name


class APIAdapterBase:
  ctx = {}

  def __init__(self, base_url=None, ctx: ConfigDict = None):
    self.ctx = ctx or {"config": Config()}
    self.config: Config = self.ctx["config"]
    self.base_url = base_url or self.config.BASE_URL
    self.logger = get_logger(self.__class__.__name__)
    self.gen = Generic("en")

    self.req: APIX = APIX(
      ctx=self.ctx,
      base_url=self.base_url,
    )

  def gen_name(self, words_number=1):
    # Use different sources to make the folder name more interesting
    project_name = " ".join(
      self.gen.text.words(quantity=words_number)
    )  # Random word to simulate a project name
    random_number = self.gen.code.pin()  # Random number for uniqueness
    date = self.gen.datetime.formatted_date(fmt="%d%m%Y")  # Add a formatted date for context

    # Combine everything to form a folder name
    folder_name = f"{project_name}-{random_number}-{date}"
    return folder_name

  def read_json_by_file(self, storage_file):
    try:
      with open(storage_file, "r") as file:
        return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
      raise ValueError(f"Storage session file {storage_file} not found")
