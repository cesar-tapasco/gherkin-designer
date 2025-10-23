import httpx
from src.utils.core.query_jq import JSONQueryJQ


class MagicResponse:
  def __init__(self, res, status, status_text, json, jq):
    self.res: httpx.Response = res
    self.status = status
    self.status_text = status_text
    self.json = json
    self.jq: JSONQueryJQ = jq
