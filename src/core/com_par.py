from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
    "-sS", "--source-select",
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
    type=str,
    dest="cache_id",
    default=None
)

parser.add_argument(
    "-nA", "--no-animate", action="store_true", dest="animate", default=False
)

parser.add_argument(
    "-F", "--frame", type=int, dest="frame", default=0
)

parser.add_argument(
    "-f", "--filter", action="append", type=str, dest="filters", default=[]
)

parser.add_argument(
    "-fG", "--filter-grouping", type=str, dest="f_group", default="START",
    choices=["BEFORE", "AFTER"]
)
