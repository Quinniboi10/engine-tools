from pathlib import Path
from uci import UCIHandler
from tests.perft_tests import debug_perft, debug_perft_suite
from tests.speedup_tests import compare_bench_speeds

import logging
import argparse

version_string = f"Engine Tools 0.0.1"

parser = argparse.ArgumentParser(
                    prog=version_string,
                    description="Various Python tools to make engine debugging easier")
parser.add_argument("-e", "--engine", help="Primary engine to run tests on", required=True)
parser.add_argument("-r", "--reference-engine", help="Reference engine to use as a baseline", required=True)

parser.add_argument("--no-bulk", help="Use perft instead of bulk for the engine", action="store_true")
parser.add_argument("--no-bulk-reference", help="Use perft instead of bulk for the reference engine", action="store_true")

parser.add_argument("--perft-pos", help="Debug an individual perft position, formatted <fen>:<depth>")
parser.add_argument("--perft-suite", help="Path to an standard .epd file")

parser.add_argument("--speedup", help="Compare the bench speed between the engines", action="store_true")

args = parser.parse_args()

def load_engines() -> tuple[UCIHandler, UCIHandler]:
    engine = UCIHandler(Path(args.engine), use_bulk=not args.no_bulk)
    working_eng = UCIHandler(Path(args.reference_engine), use_bulk=not args.no_bulk_reference)
    return engine, working_eng

def main():
    logging.basicConfig(filename="engine-bench.log", level=logging.DEBUG)

    if args.perft_pos is not None:
        fen, depth = args.perft_pos.strip().split(":")
        debug_perft(fen, int(depth), *load_engines())
    if args.perft_suite is not None:
        debug_perft_suite(Path(args.perft_suite), *load_engines())
    
    if args.speedup:
        compare_bench_speeds(Path(args.engine), Path(args.reference_engine))

if __name__ == "__main__":
    main()