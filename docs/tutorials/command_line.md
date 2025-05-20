# XArray Viewer command line arguments

To use the xr-viewer CLI, be sure to install the Pan3D Viewer dependencies
first. This includes Trame, a Kitware toolkit for Python servers. Learn more
about Trame [here][trame-link].

        pip install pan3d[viewer]

By default, the command `xr-viewer` will launch XArray Viewer as a local Python
server and open a tab in your default browser and navigate to `localhost:8080`.
You can change this behavior in a number of ways. For example, you can disable
the browser tab launch by adding `--server` to the command.

In response, `xr-viewer` will display this message in the terminal:

        App running at:
        - Local:   http://localhost:8080/
        - Network: http://127.0.0.1:8080/

As the message indicates, pointing a browser to http://localhost:8080/ will open
the application.

There are other arguments to initialize features and data. Here is the full
list:

```bash
usage: xr-viewer [-h] [--server] [--banner] [--app] [--no-http] [--authKeyFile AUTHKEYFILE] [--hot-reload] [--trame-args TRAME_ARGS] [--debug] [--nosignalhandlers] [--host HOST] [-p PORT]
                 [--timeout TIMEOUT] [--content CONTENT] [--authKey AUTHKEY] [--ws-endpoint WS] [--no-ws-endpoint] [--fs-endpoints FSENDPOINTS] [--reverse-url REVERSE_URL] [--ssl SSL]
                 [--import-state IMPORT_STATE] [--xarray-file XARRAY_FILE] [--xarray-url XARRAY_URL] [--wasm] [--vtkjs]

Kitware trame

options:
  -h, --help            show this help message and exit
  --server              Prevent your browser from opening at startup
  --banner              Print trame banner
  --app                 Use OS built-in browser
  --no-http             Do not serve anything over http
  --authKeyFile AUTHKEYFILE
                        Path to a File that contains the Authentication key for clients to connect to the WebSocket. This takes precedence over '-a, --authKey' from wslink.
  --hot-reload          Automatically reload state/controller callback functions for every function call. This allows live editing of the functions. Functions located in the site-packages
                        directories are skipped.
  --trame-args TRAME_ARGS
                        If specified, trame will ignore all other arguments, and only the contents of the `--trame-args` will be used. For example: `--trame-args="-p 8081 --server"`.
                        Alternatively, the environment variable `TRAME_ARGS` may be set instead.
  --debug               log debugging messages to stdout
  --nosignalhandlers    Prevent installation of signal handlers so server can be started inside a thread.
  --host HOST           the interface for the web-server to listen on (default: 0.0.0.0)
  -p PORT, --port PORT  port number for the web-server to listen on (default: 8080)
  --timeout TIMEOUT     timeout for reaping process on idle in seconds (default: 300s, 0 to disable)
  --content CONTENT     root for web-pages to serve (default: none)
  --authKey AUTHKEY     Authentication key for clients to connect to the WebSocket.
  --ws-endpoint WS      Specify WebSocket endpoint. (e.g. foo/bar/ws, Default: ws)
  --no-ws-endpoint      If provided, disables the websocket endpoint
  --fs-endpoints FSENDPOINTS
                        add another fs location to a specific endpoint (i.e: data=/Users/seb/Download|images=/Users/seb/Pictures)
  --reverse-url REVERSE_URL
                        Make the server act as a client to connect to a ws relay
  --ssl SSL             add a tuple file [certificate, key] (i.e: --ssl 'certificate,key') or adhoc string to generate temporary certificate (i.e: --ssl 'adhoc')
  --import-state IMPORT_STATE
                        Pass a string with this argument to specify a startup configuration. This value must be a local path to a JSON file which adheres to the schema specified in the
                        [Configuration Files documentation](../api/configuration.md). A dataset specified in this configuration will override any value passed to `--xarray-*`
  --xarray-file XARRAY_FILE
                        Provide path to xarray file
  --xarray-url XARRAY_URL
                        Provide URL to xarray dataset
  --wasm                Use WASM for local rendering
  --vtkjs               Use vtk.js for local rendering
```

<!-- Links -->

[trame-link]: https://kitware.github.io/trame/
