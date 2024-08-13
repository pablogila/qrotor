#!/bin/bash

#######################################
##  Target virtual environment path  ##
#######################################
VENV_PATH="$HOME/venvs/main"
#######################################

error_handler() {
  notify-send "QRotor Update" "ERROR: $1"
  echo "ERROR: $1"
  exit 1
}
trap 'error_handler "$BASH_COMMAND"' ERR

if [ ! -d "$VENV_PATH" ]; then
  error_handler "Python virtualenv missing, create one with 'python3 -m venv $VENV_PATH'."
fi

SOURCE_FOLDER="./qrotor"
VERSION=$(python3 -c "import re; print(re.search(r'version\s*=\s*\'([^\']+)\'', open('$SOURCE_FOLDER/core.py').read()).group(1))")
PYTHON_FOLDER=$(find "$VENV_PATH/lib" -type d -name "python3.*")
PACKAGES_FOLDER=$(find "$PYTHON_FOLDER" -type d -name "site-packages")
DESTINATION_FOLDER="$PACKAGES_FOLDER/qrotor"
DEST_VERSION=""
LOG=''

if [ -d "$DESTINATION_FOLDER" ]; then
  DEST_VERSION=$(python3 -c "import re; print(re.search(r'version\s*=\s*\'([^\']+)\'', open('$DESTINATION_FOLDER/core.py').read()).group(1))")
  if [ "$VERSION" == "$DEST_VERSION" ]; then
    LOG="Version $VERSION is already installed. No update needed."
    notify-send "QRotor Update" "$LOG"
    echo "$LOG"
    exit 0
  else
    rm -rf "$DESTINATION_FOLDER"
  fi
else
  LOG="Installed QRotor version $VERSION."
fi

mkdir -p "$DESTINATION_FOLDER"
cp -r "$SOURCE_FOLDER"/* "$DESTINATION_FOLDER"

if [ -n "$DEST_VERSION" ]; then
  LOG="QRotor upgraded from version $DEST_VERSION to $VERSION."
else
  if [ -z "$LOG" ]; then
    LOG="QRotor updated to version $VERSION."
  fi
fi

notify-send "QRotor Update" "$LOG"
echo "$LOG"
