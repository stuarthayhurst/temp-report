#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

exportFiles() {
  echo "Copying and compressing files to export:"
  mkdir TEMP
  cp data/addresses.csv data/config.csv data/sender.csv TEMP/
  cd TEMP
  echo "Data will be encryted for security:"
  zip -e ../export.zip *
  cd ../ && rm -rf TEMP
  echo "Done"
}

importFiles() {
  echo "Importing files:"
  unzip -u export.zip -d data
  rm export.zip
  echo "Done"
}

while [[ "$#" -gt 0 ]]; do case $1 in
  -h|--help) echo "-h | --help   : Display the help page currently shown"; echo "-e | --export : Export the address list, config and sender credentials to a .zip"; echo "-i | --import : import the .zip created by the exporter";;
  -e|--export) exportFiles;;
  -i|--import) importFiles;;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done
