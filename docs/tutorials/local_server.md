# How to run Pan3D as a local Python server

Pan3D is intended to aid data scientists in exploring a given multidimensional dataset, so for this tutorial we will refer to a public dataset provided by Pangeo Forge. This dataset, provided by the National Oceanic and Atmospheric Administration (NOAA), maps global sea surface temperatures over time.  Visit [https://pangeo-forge.org/dashboard/feedstock/3](https://pangeo-forge.org/dashboard/feedstock/3) to view more information about this data.

1. In a terminal with pip, install Pan3D.

        pip install pan3d

2. Run the following command to launch the Pan3D viewer as a local Python server. By default, this command will launch a tab in your default browser and navigate to `localhost:8080`.

        pan3d-viewer [...options]

3. This command has several argument options:.

    - `--server`/`-S`: Launch in server mode, which disables the default behavior of opening a browser tab on startup.
    - `--pangeo`/`-P`: Launch with a default catalog of Pangeo Forge example datasets available in the dataset selection box in the left drawer.
    - `--dataset`/`-D`: Pass a string with this argument to specify a target dataset. This value can be either a local path or remote URL. This value must be readable by `xarray.open_dataset()`.
    - `--config_path`/`-C`: Pass a string with this argument to specify a startup configuration. This value must be a local path to a JSON file which adheres to the schema specified in the [Configuration Files documentation](../api/configuration.md). A dataset specified in this configuration will override any value passed to `--dataset`/`-D`.
    - `--debug`/`-d`: Launch in debug mode, which will include more terminal output. Intended for developer use.
