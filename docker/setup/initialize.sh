# Install app from local directory
pip install "/local-app[all]"
pip uninstall -y vtk
pip install --extra-index-url https://wheels.vtk.org vtk-osmesa
