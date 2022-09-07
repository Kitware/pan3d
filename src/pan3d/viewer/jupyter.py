from trame.app import get_server, jupyter
from pan3d.viewer import engine, ui
from trame_vtk.modules import vtk
from .. import logger, logging


def show(server=None, zarr=None, **kwargs):
    """Run and display the trame application in jupyter's event loop

    The kwargs are forwarded to IPython.display.IFrame()
    """
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

        # Needed to support multi-instance in Jupyter
        server.enable_module(vtk)

    # Disable logging
    logger.setLevel(logging.WARNING)

    # Initialize app
    engine.initialize(server, zarr)
    ui.initialize(server)

    # Show as cell result
    jupyter.show(server, **kwargs)


def jupyter_proxy_info():
    """Get the config to run the trame application via jupyter's server proxy

    This is provided to the `jupyter_serverproxy_servers` entrypoint, and the
    jupyter server proxy will use it to start the application as a separate
    process.
    """
    return {
        "command": ["pan3d-viewer", "-p", "0", "--server"],
    }
