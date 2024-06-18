from pathlib import Path

# Compute local path to serve
serve_path = str(Path('pan3d/ui/pan3d_components/module'))

# Serve directory for JS/CSS files
serve = {"__pan3d_components": serve_path}

# List of JS files to load (usually from the serve path above)
scripts = ["__pan3d_components/pan3d-components.umd.js"]

# List of Vue plugins to install/load
vue_use = ["pan3d_components"]
