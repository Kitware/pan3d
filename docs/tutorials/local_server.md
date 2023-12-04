# How to run Pan3D as a local Python server

Pan3D is intended to aid data scientists in exploring a given multidimensional dataset, so for this tutorial we will refer to a public dataset provided by Pangeo Forge. This dataset, provided by the National Oceanic and Atmospheric Administration (NOAA), maps global sea surface temperatures over time.  Visit [https://pangeo-forge.org/dashboard/feedstock/3](https://pangeo-forge.org/dashboard/feedstock/3) to view more information about this data.

1. In a Python environment, install Pan3D.

        pip install pan3d

2. Run the following command to launch the Pan3D viewer with the target dataset loaded.

        pan3d-viewer --dataset=https://ncsa.osn.xsede.org/Pangeo/pangeo-forge/noaa-coastwatch-geopolar-sst-feedstock/noaa-coastwatch-geopolar-sst.zarr

3. If you have an exported configuration file for the dataset, you can replace the dataset argument with `--config_path=/path/to/pan3d_state.json`.

4. The server will automatically launch a browser window to `localhost:8080`. To run the server without automatically launching a browser window, add the `--server` argument to the `pan3d-viewer` command.
