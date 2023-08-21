from argparse import ArgumentParser
from dataset_builder import DatasetBuilder

parser = ArgumentParser(
    prog="Pan3D",
    description="Launch the Pan3D Dataset Viewer / Builder",
)

parser.add_argument("-b", "--bookmark_path")
parser.add_argument("-d", "--dataset_path")

args = parser.parse_args()

viewer = DatasetBuilder(dataset_path=args.dataset_path)
if args.bookmark_path:
    viewer.import_bookmark(args.bookmark_path)
viewer.server.start()
