import jq


class JSONQueryJQ:
  def __init__(self, json_data):
    # Initialize with JSON data (can be a dict or a list)
    self.data = json_data

  def all(self, jq_filter):
    """Executes a jq filter to return all matching elements."""
    try:
      result = jq.compile(jq_filter).input(self.data).all()
      return result
    except Exception as e:
      print(f"Error executing jq query: {e}")
      return []

  def one(self, jq_filter):
    """Executes a jq filter to return the first matching element."""
    try:
      result = jq.compile(jq_filter).input(self.data).first()
      return result
    except Exception as e:
      print(f"Error executing jq query: {e}")
      return None
