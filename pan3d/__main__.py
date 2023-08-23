from argparse import ArgumentParser
from dataset_builder import DatasetBuilder

parser = ArgumentParser(
    prog="Pan3D",
    description="Launch the Pan3D Dataset Builder",
)

parser.add_argument("-b", "--config_path")
parser.add_argument("-d", "--dataset_path")

args = parser.parse_args()

builder = DatasetBuilder(dataset_path=args.dataset_path)
if args.config_path:
    builder.import_config(args.config_path)
builder.viewer.server.start()
