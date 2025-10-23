#!/bin/sh
set -e

# Ensure .temp directory exists
mkdir -p .temp

# Clean up old report directories
rm -rf .temp/report
rm -rf .temp/report-sm

# Run report preconditions (creates necessary directories and files)
python commands/deployment/report_preconditions.py

# Create report directory
mkdir -p .temp/report

# Copy allure results if they exist
if [ -d ".temp/report-sm/allure-results" ]; then
  cp -r .temp/report-sm/allure-results .temp/report/report-sm
else
  echo "Warning: .temp/report-sm/allure-results does not exist"
  mkdir -p .temp/report/report-sm
fi

# Copy test results if they exist
if [ -d ".temp/test-results" ]; then
  cp -r .temp/test-results .temp/report/pw-results
fi

export REPORT_PATH=$PWD/.temp/report.zip

# Unzip report UI
if [ -f "commands/deployment/report-ui.zip" ]; then
  unzip -o commands/deployment/report-ui.zip -d .temp/report-sm
else
  echo "Error: commands/deployment/report-ui.zip not found"
  exit 1
fi
