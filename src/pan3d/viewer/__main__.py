from trame.app import dev, get_server

from . import engine, ui


def _reload():
    server = get_server()
    dev.reload(ui)
    ui.initialize(server)


def main(server=None, dataset_path=None, **kwargs):
    # Get or create server
    if server is None:
        server = get_server()

    if isinstance(server, str):
        server = get_server(server)

    if dataset_path is None:
        server.cli.add_argument(
            "--data", help="Path to dataset", dest="data", required=False
        )
        args, _ = server.cli.parse_known_args()
        dataset_path = args.data

    # Make UI auto reload
    server.controller.on_server_reload.add(_reload)

    # Init application
    engine.initialize(server)
    ui.initialize(server)

    server.state.dataset_path = dataset_path

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    main()
