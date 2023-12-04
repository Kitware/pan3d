FROM ghcr.io/pyvista/pyvista:latest

COPY . ${HOME}
WORKDIR ${HOME}
RUN pip install -r requirements.txt
RUN pip uninstall vtk -y
RUN pip install --extra-index-url https://wheels.vtk.org vtk-osmesa
