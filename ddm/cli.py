import argparse
from dask.diagnostics import ProgressBar

from ddm import read_file


def main(filepath: str, xscale: float, tscale: float):
    # Load data
    data = read_file(filename=filepath, xscale=xscale, tscale=tscale)

    # Process data

    # Data fitting

    # Data plotting

    # Exporting results


def create_parser() -> argparse.Namespace:
    """Create a CLI argument parser

    Returns
    -------
    args
        defined arguments for CLI
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)

    parser.add_argument("--file", type=str, required=True, help="path to the datafile")
    parser.add_argument(
        "--xscale",
        type=float,
        required=False,
        help="pixel size in microns",
    )
    parser.add_argument(
        "--tscale",
        type=float,
        required=False,
        help="time per frame in milliseconds",
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = create_parser()
    main(args.file, args.xscale, args.tscale)
