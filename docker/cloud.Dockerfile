FROM pangeo/pangeo-notebook:latest

RUN pip install pan3d[all] imageio trame-jupyter-extension
RUN pip uninstall -y vtk
RUN pip install --extra-index-url https://wheels.vtk.org vtk-osmesa

COPY ./examples /shared/pan3d_examples
COPY docker/cloud_entrypoint.sh /shared/cloud_entrypoint.sh

ENTRYPOINT ["/shared/cloud_entrypoint.sh"]
