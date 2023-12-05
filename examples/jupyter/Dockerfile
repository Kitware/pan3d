FROM ghcr.io/pyvista/pyvista:latest

USER root

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
    libosmesa6-dev cmake ninja-build libboost-all-dev libxrender1

COPY . ${HOME}
WORKDIR ${HOME}
RUN pip install -r requirements.txt
RUN pip install --extra-index-url https://wheels.vtk.org vtk-osmesa
