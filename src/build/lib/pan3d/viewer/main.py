from trame.app import get_server
from . import engine, ui


def main(server=None, zarr=None, **kwargs):
    # Get or create server
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    # Init application
    engine.initialize(server, zarr)
    ui.initialize(server)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    server = get_server()
    server.cli.add_argument("--data", help="Path to dataset", dest="data", required=True)
    args, _ = server.cli.parse_known_args()
    main(server, args.data)
