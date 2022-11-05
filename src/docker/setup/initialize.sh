# Install app from local directory
pip install /opt/wheels/vtk-9.2.2.osmesa-*.whl
pip install /local-app
# Install again because VTK from PyPI is pulled by GeoVista
pip install /opt/wheels/vtk-9.2.2.osmesa-*.whl
