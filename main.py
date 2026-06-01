from pathlib import Path
from uci import UCIHandler
from tests.perft_tests import debug_perft, debug_perft_suite

import logging
import argparse

version_string = f"Engine Tools 0.0.1"

parser = argparse.ArgumentParser(
                    prog=version_string,
                    description="Various Python tools to make engine debugging easier")
parser.add_argument("-e", "--engine", help="Primary engine to run tests on", required=True)
parser.add_argument("-r", "--reference-engine", help="Reference engine to use as a baseline", required=True)

parser.add_argument("--perft-pos", help="Debug an individual perft position, formatted <fen>:<depth>")
parser.add_argument("--perft-suite", help="Path to an standard .epd file")

args = parser.parse_args()

def main():
    logging.basicConfig(filename="engine-bench.log", level=logging.DEBUG)

    engine = UCIHandler(Path(args.engine))

    working_eng = UCIHandler(Path(args.reference_engine))

    if args.perft_pos is not None:
        fen, depth = args.perft_pos.strip().split(":")
        debug_perft(fen, int(depth), working_eng, engine)
    if args.perft_suite is not None:
        debug_perft_suite(Path(args.perft_suite), working_eng, engine)

if __name__ == "__main__":
    main()