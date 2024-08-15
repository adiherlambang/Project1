#!/bin/bash
read file_path
# echo $file_path
# Check if file exists
if [ -f "import/$file_path" ]; then
  # Ensure correct permissions are set on the import directory and files
  chmod -R 755 import/
  # Create PyATS testbed file
  pyats create testbed file --path "import/$file_path" --output testbed/device.yaml
  # Check if pyats command succeeded
  if [ $? -ne 0 ]; then
    echo "Failed to create testbed file with pyats."
    exit 2
  fi
else
  echo "File not found: $file_path"
  exit 1
fi