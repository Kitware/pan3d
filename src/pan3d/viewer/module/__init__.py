from pathlib import Path

serve_path = str(Path(__file__).with_name("assets").resolve())
serve = {"__zarr_viewer": serve_path}
styles = ["__zarr_viewer/style.css"]
