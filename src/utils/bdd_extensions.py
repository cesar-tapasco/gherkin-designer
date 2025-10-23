import os
import re
import pytest
from pytest_bdd import exceptions
from pytest_bdd.utils import get_caller_module_locals, get_caller_module_path
from typing import Any, Iterable
from pytest_bdd.scenario import (
  get_features_base_dir,
  get_features,
  scenario,
)


def _parse_qase_tag(tag):
  match = re.match(r"Q:(\w+)-(\d+)", tag)
  if match:
    return match.group(1), match.group(2)  # Return just the numeric part
  return None, None


def scenarios(*feature_paths: str, **kwargs: Any) -> None:
  """Parse features from the paths and put all found scenarios in the caller module.

  :param *feature_paths: feature file paths to use for scenarios
  """
  caller_locals = get_caller_module_locals()
  caller_path = get_caller_module_path()

  features_base_dir = kwargs.get("features_base_dir")
  if features_base_dir is None:
    features_base_dir = get_features_base_dir(caller_path)

  abs_feature_paths = []
  for path in feature_paths:
    if not os.path.isabs(path):
      path = os.path.abspath(os.path.join(features_base_dir, path))
    abs_feature_paths.append(path)
  found = False

  module_scenarios = frozenset(
    (attr.__scenario__.feature.filename, attr.__scenario__.name)
    for name, attr in caller_locals.items()
    if hasattr(attr, "__scenario__")
  )

  for feature in get_features(abs_feature_paths):
    all_tags = []
    # Iterate over the list of features and collect all tags
    for tag in feature.tags:
      all_tags.append(tag)
    for scenario_name, scenario_object in feature.scenarios.items():
      # skip already bound scenarios
      if (scenario_object.feature.filename, scenario_name) not in module_scenarios:
        description = ""
        qase_ids = []
        qase_project_id = None
        is_skip = False
        for tag in scenario_object.tags:
          qase_project_id, qase_id = _parse_qase_tag(tag)
          if str.lower(tag) == "skip":
            is_skip = True
          if qase_id is not None:
            qase_ids.append(int(qase_id))
        if not is_skip:
          for step in scenario_object.steps:
            description += f"{step.keyword} {step.name}\n"

          @pytest.mark.qase_tag(ids=qase_ids, project=qase_project_id)
          @pytest.mark.title(scenario_name)
          @pytest.mark.feature_tags(all_tags)
          @pytest.mark.description(description)
          @scenario(feature.filename, scenario_name, **kwargs)
          def _scenario() -> None:
            pass  # pragma: no cover

          for test_name in get_python_name_generator(scenario_name):
            if test_name not in caller_locals:
              # found an unique test name
              caller_locals[test_name] = _scenario
              break
      found = True
  if not found:
    raise exceptions.NoScenariosFound(abs_feature_paths)


def get_python_name_generator(name: str) -> Iterable[str]:
  """Generate a sequence of suitable python names out of given arbitrary string name."""
  python_name = make_python_name(name)
  suffix = ""
  index = 0

  def get_name() -> str:
    return f"test: {python_name}{suffix}"

  while True:
    yield get_name()
    index += 1
    suffix = f"_{index}"


def make_python_name(string: str) -> str:
  """Make python attribute name out of a given string."""
  # string = re.sub(PYTHON_REPLACE_REGEX, "", string.replace(" ", "_"))
  # return re.sub(ALPHA_REGEX, "", string).lower()
  return string
