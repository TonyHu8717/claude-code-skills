#!/bin/bash
# Assembles the course from parts, including submodules.
# Run from the course directory: bash build.sh
set -e

# First, recursively build all submodules
if [ -d "submodules" ]; then
  for submodule in submodules/*; do
    if [ -d "$submodule" ] && [ -f "$submodule/build.sh" ]; then
      echo "Building submodule: $submodule"
      (cd "$submodule" && bash build.sh)
    fi
  done
fi

# Assemble the main index.html
cat _base.html modules/*.html _footer.html > index.html
echo "Built index.html — open it in your browser."
