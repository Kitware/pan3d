FROM pangeo/pangeo-notebook:latest

RUN pip install pan3d[all] imageio trame-jupyter-extension
RUN pip uninstall -y vtk
RUN pip install --extra-index-url https://wheels.vtk.org vtk-osmesa

COPY ./examples /shared/pan3d_examples

# For 2i2c deployment, create a symlink to examples folder in jovyan home folder
ENTRYPOINT ["ln", "-s", "/shared/pan3d_examples", "/home/jovyan/shared/pan3d_examples"]
