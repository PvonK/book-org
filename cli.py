from .core import organize_dir
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-d", "--dryrun", action="store_true")
    parser.add_argument("-r", "--recursive", action="store_true")
    parser.add_argument("-i", "--interactive", action="store_true")

    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    organize_dir(
        args.directory,
        dry=args.dryrun,
        interactive=args.interactive
        )


if __name__ == "__main__":
    main()
