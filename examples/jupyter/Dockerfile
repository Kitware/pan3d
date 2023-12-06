FROM jupyter/scipy-notebook:cf6258237ff9

USER root
RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
    libosmesa6-dev cmake ninja-build libboost-all-dev libxrender1 \
    libglu1-mesa libxi-dev libxmu-dev libgl1-mesa-dev libglib2.0-0
USER ${NB_USER}

COPY . ${HOME}
WORKDIR ${HOME}
RUN pip install -r requirements.txt
RUN pip uninstall vtk -y
RUN pip install vtk-osmesa --index-url https://gitlab.kitware.com/api/v4/projects/13/packages/pypi/simple
