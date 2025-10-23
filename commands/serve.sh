#!/bin/sh

rm -rf .temp/report
rm -rf .temp/report-sm
python commands/deployment/report_preconditions.py
mkdir .temp/report
cp -r .temp/report-sm/allure-results .temp/report/report-sm

if [ -d ".temp/test-results" ]; then
  cp -r .temp/test-results .temp/report/pw-results
fi
export REPORT_PATH=$PWD/.temp/report.zip

unzip -o commands/deployment/report-ui.zip -d .temp/report-sm
