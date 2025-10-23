import shutil
import json
import os


def create_json_file(folder_path, output_file):
  json_files_info = []

  # Ensure the output directory exists
  output_dir = os.path.dirname(output_file)
  os.makedirs(output_dir, exist_ok=True)

  # Check if folder exists before listing
  if not os.path.exists(folder_path):
    print(f"Warning: Folder '{folder_path}' does not exist. Creating empty tests.json")
    with open(output_file, "w") as f:
      json.dump(json_files_info, f, indent=4)
    return

  # List all files in the directory
  for file_name in os.listdir(folder_path):
    # Check if the file ends with '.json'
    if file_name.endswith("-result.json"):
      json_files_info.append(file_name)

  # Write the list of dictionaries to a JSON file
  with open(output_file, "w") as f:
    json.dump(json_files_info, f, indent=4)


def copy_folder(source_folder, destination_folder):
  # Check if source folder exists
  if not os.path.exists(source_folder):
    print(f"Warning: Source folder '{source_folder}' does not exist. Creating empty destination folder.")
    os.makedirs(destination_folder, exist_ok=True)
    return

  try:
    shutil.copytree(source_folder, destination_folder)
    print(f"Folder '{source_folder}' copied to '{destination_folder}' successfully.")
  except FileExistsError:
    print(f"Folder '{destination_folder}' already exists.")
  except Exception as e:
    print(f"Error: {e}")


# Ensure .temp directory exists
os.makedirs(".temp", exist_ok=True)

copy_folder(".temp/allure-results", ".temp/report-sm/allure-results")
create_json_file(".temp/report-sm/allure-results", ".temp/report-sm/allure-results/tests.json")

# Only copy parsed_data.json if it exists
if os.path.exists(".temp/parsed_data.json"):
  shutil.copy(".temp/parsed_data.json", ".temp/report-sm/allure-results/parsed_data.json")
else:
  print("Warning: .temp/parsed_data.json does not exist. Skipping copy.")
  # Create an empty parsed_data.json
  with open(".temp/report-sm/allure-results/parsed_data.json", "w") as f:
    json.dump({}, f)
