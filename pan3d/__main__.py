from argparse import ArgumentParser, BooleanOptionalAction
from pan3d.dataset_builder import DatasetBuilder


def main():
    parser = ArgumentParser(
        prog="Pan3D",
        description="Launch the Pan3D Dataset Builder",
    )

    parser.add_argument("-C", "--config_path")
    parser.add_argument("-D", "--dataset")
    parser.add_argument("-P", "--pangeo", action=BooleanOptionalAction)
    parser.add_argument("-S", "--server", action=BooleanOptionalAction)

    args = parser.parse_args()

    builder = DatasetBuilder(dataset_path=args.dataset, pangeo=args.pangeo)
    if args.config_path:
        builder.import_config(args.config_path)
    builder.viewer.server.start()


if __name__ == "__main__":
    main()
