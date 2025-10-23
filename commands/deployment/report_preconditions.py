import shutil
import json
import os


def create_json_file(folder_path, output_file):
  json_files_info = []
  # List all files in the directory
  for file_name in os.listdir(folder_path):
    # Check if the file ends with '.json'
    if file_name.endswith("-result.json"):
      json_files_info.append(file_name)

  # Write the list of dictionaries to a JSON file
  with open(output_file, "w") as f:
    json.dump(json_files_info, f, indent=4)


def copy_folder(source_folder, destination_folder):
  try:
    shutil.copytree(source_folder, destination_folder)
    print(f"Folder '{source_folder}' copied to '{destination_folder}' successfully.")
  except FileExistsError:
    print(f"Folder '{destination_folder}' already exists.")
  except Exception as e:
    print(f"Error: {e}")


copy_folder(".temp/allure-results", ".temp/report-sm/allure-results")
create_json_file(".temp/report-sm/allure-results", ".temp/report-sm/allure-results/tests.json")
shutil.copy(".temp/parsed_data.json", ".temp/report-sm/allure-results/parsed_data.json")
