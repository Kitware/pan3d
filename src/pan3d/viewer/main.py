from trame.app import get_server, dev
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
    engine.initialize(server, zarr)
    ui.initialize(server)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    main()
