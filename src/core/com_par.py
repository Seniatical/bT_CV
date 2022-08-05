from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
    "-sS", "--source-select",
    action="store",
    type=int,
    default=-1,
    dest="ss"
)

parser.add_argument(
    "-E", "--export",
    type=str, choices=["image", "base64", "array"],
    default="image",
    dest="export-type"
)

parser.add_argument(
    "-iF", "--image-format", type=str, dest="form",
    choices=["GIF", "PNG", "JPEG", "JPG"],
    default="AUTO"
)

parser.add_argument(
    "-C", "--cache", action="store_true", dest="cache", default=False
)

parser.add_argument(
    "-Cp", "--cache-protect", action="store_true", dest="cache-protect", default=False
)

parser.add_argument(
    "-fC", "--from-cache",
    action="store",
    type=str,
    dest="cache_id",
    default=None
)

parser.add_argument(
    "-A", "--animate", action="store_true", dest="animate", default=True
)

parser.add_argument(
    "-F", "--frame", type=int, dest="frame", default=0
)
