

if [ $# -eq 0 ]; then
  echo "Usage: $0 <markdown_file>"
  echo "Or use: $0 --all to build all templates"
  exit 1
fi

build_file() {
  local input_file=$1
  local filename=$(basename "$input_file" .md)
  local output_file="${input_file%.*}.docx"
  
  echo "Building $input_file -> $output_file"
  pandoc "$input_file" --citeproc -o "$output_file"
  
  if [ $? -eq 0 ]; then
    echo "✅ Successfully built $output_file"
  else
    echo "❌ Failed to build $output_file"
    exit 1
  fi
}

build_all_templates() {
  echo "Building all template files..."
  mkdir -p build
  
  for file in templates/*.md; do
    local filename=$(basename "$file" .md)
    local output_file="build/${filename}.docx"
    
    echo "Building $file -> $output_file"
    pandoc "$file" --citeproc -o "$output_file"
    
    if [ $? -eq 0 ]; then
      echo "✅ Successfully built $output_file"
    else
      echo "❌ Failed to build $output_file"
      exit 1
    fi
  done
  
  echo "All templates built successfully in the build directory."
}

if [ "$1" == "--all" ]; then
  build_all_templates
else
  build_file "$1"
fi

exit 0
