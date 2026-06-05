#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
from latex_to_asciimath import convert_latex_to_asciimath


def main():
    parser = argparse.ArgumentParser(
        description="Convert LaTeX math to IMathAS AsciiMath.",
        usage="%(prog)s [-e EXPR] [input_file output_file]",
    )
    parser.add_argument(
        "-e", "--expr",
        metavar="EXPR",
        help="Convert a single LaTeX expression and print result to stdout",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read LaTeX text from stdin and write AsciiMath to stdout",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="input_file output_file for file-to-file conversion",
    )

    args = parser.parse_args()

    if args.expr is not None:
        print(convert_latex_to_asciimath(args.expr))
        return

    if args.stdin:
        content = sys.stdin.read()
        sys.stdout.write(convert_latex_to_asciimath(content))
        return

    if len(args.files) != 2:
        parser.print_usage()
        sys.exit(1)

    input_path, output_path = args.files

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(convert_latex_to_asciimath(content))

    print(f"Successfully converted '{input_path}' to '{output_path}'.")


if __name__ == "__main__":
    main()
