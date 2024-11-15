# XArray Viewer command line arguments

To use the xr-viewer CLI, be sure to install the Pan3D Viewer dependencies first. This includes Trame, a Kitware toolkit for Python servers. Learn more about Trame [here][trame-link].

        pip install pan3d[viewer]

By default, the command `xr-viewer`  will launch XArray Viewer as a local Python server and open a tab in your default browser and navigate to `localhost:8080`. You can change this behavior in a number of ways. For example, you can disable the browser tab launch by adding `--server` to the command.

In response, `xr-viewer` will display this message in the terminal:

        App running at:
        - Local:   http://localhost:8080/
        - Network: http://127.0.0.1:8080/

As the message indicates, pointing a browser to http://localhost:8080/ will open the application.

There are other arguments to initialize features and data. Here is the full list:

```bash
--help/-h:      Write command info including the list of options to the terminal and exit.
--server:       Launch in server mode, which disables the default behavior of opening a browser tab on startup.
--xarray-file:  Provide path to xarray file.
--xarray-url:   Provide URL to xarray dataset.
--import-state: Pass a string with this argument to specify a startup configuration. This value must be a local path to a JSON file which adheres to the schema specified in the [Configuration Files documentation](../api/configuration.md). A dataset specified in this configuration will override any value passed to `--xarray-*`.
--debug:        Launch in debug mode, which will include more terminal output. Intended for developer use.
```


<!-- Links -->
[trame-link]: https://kitware.github.io/trame/
