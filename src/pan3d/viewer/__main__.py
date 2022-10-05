import xarray as xr
from trame.app import dev, get_server

from . import engine, ui


def _reload():
    server = get_server()
    dev.reload(ui)
    ui.initialize(server)


def main(server=None, zarr=None, **kwargs):
    # Get or create server
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    if zarr is None:
        server.cli.add_argument(
            "--data", help="Path to dataset", dest="data", required=True
        )
        args, _ = server.cli.parse_known_args()
        zarr = args.data

    # Make UI auto reload
    server.controller.on_server_reload.add(_reload)

    # Init application
    dataset = xr.open_dataset(zarr, engine="zarr", consolidated=False)
    engine.initialize(server, dataset)
    ui.initialize(server)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    main()
