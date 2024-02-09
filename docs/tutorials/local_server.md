# Pan3D command line arguments

By default, invoking `pan3d-viewer`  will launch a tab in your default browser and navigate to `localhost:8080`. You can change this behavior in a number of ways. For example, you can launch the Pan3D viewer as a local Python server by running

        pan3d-viewer --server

In response, `pan3d-viewer` will display this message in the terminal:

        App running at:
        - Local:   http://localhost:8080/
        - Network: http://127.0.0.1:8080/

As the message indicates, pointing a browser to http://localhost:8080/ will open the application.

There are other arguments to initialize features and data. Here is the full list:

```bash
--help/-h:        Write command info including the list of options to the terminal and exit.
--server/-S:      Launch in server mode, which disables the default behavior of opening a browser tab on startup.
--pangeo/-P:      Launch with a default catalog of Pangeo Forge example datasets available in the dataset selection box in the left drawer.
--dataset/-D:     Pass a string with this argument to specify a target dataset. This value can be either a local path or remote URL. This value must be readable by `xarray.open_dataset()`.
--config_path/-C: Pass a string with this argument to specify a startup configuration. This value must be a local path to a JSON file which adheres to the schema specified in the [Configuration Files documentation](../api/configuration.md). A dataset specified in this configuration will override any value passed to `--dataset`/`-D`.
--debug/-d:       Launch in debug mode, which will include more terminal output. Intended for developer use.
```
