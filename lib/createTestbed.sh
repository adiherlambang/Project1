#!/bin/bash
read file_path

# Check if file exists
if [ -f "assets/import/$file_path" ]; then
  # Replace all semicolons with commas in the file
  sed -i 's/[;\t|]/,/g' "assets/import/$file_path"
  echo "Semicolons replaced with commas in file: assets/import/$file_path"
  
  # Create PyATS testbed file
  pyats create testbed file --path "assets/import/$file_path" --output testbed/device.yaml
else
  echo "File not found: $file_path"
fi