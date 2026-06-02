from pathlib import Path
from uci import UCIHandler
import logging

import argparse

version_string = f"Engine Tools 0.0.1"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
                    prog=version_string,
                    description="Various Python tools to make engine debugging easier")
    parser.add_argument("-e", "--engine", help="Primary engine to run tests on", metavar="PATH", required=True)
    parser.add_argument("-r", "--reference-engine", help="Reference engine to use as a baseline", metavar="PATH", required=True)

    parser.add_argument("--no-bulk", help="Use perft instead of bulk for the engine", action="store_true")
    parser.add_argument("--no-bulk-reference", help="Use perft instead of bulk for the reference engine", action="store_true")

    parser.add_argument("--perft-pos", help="Debug an individual perft position", metavar="<fen>:<depth>")
    parser.add_argument("--perft-suite", help="Path to an standard .epd file", metavar="PATH")

    parser.add_argument("--speedup", help="Compare the bench speed between the engines", action="store_true")
    parser.add_argument("--perft-speedup", help="Compare the movegen speed between the engines", metavar="<fen>:<depth>")
    parser.add_argument("--bulk-speedup", help="Compare the bulk movegen speed between the engines", metavar="<fen>:<depth>")
 
    return parser

def load_engines(args: argparse.Namespace) -> tuple[UCIHandler, UCIHandler]:
    engine = UCIHandler(Path(args.engine), use_bulk=not args.no_bulk)
    working_eng = UCIHandler(Path(args.reference_engine), use_bulk=not args.no_bulk_reference)
    return engine, working_eng

def main(argv: list[str] | None = None) -> int:
    # Call this before dependency-reliant imports in case "--help" is passed
    args = build_parser().parse_args(argv)
    
    from perft import debug_perft, debug_perft_suite
    from speedup import compare_speeds

    logging.basicConfig(filename="engine-bench.log", level=logging.DEBUG)

    if args.perft_pos is not None:
        fen, depth = args.perft_pos.strip().split(":")
        debug_perft(fen, int(depth), *load_engines(args))
    if args.perft_suite is not None:
        debug_perft_suite(Path(args.perft_suite), *load_engines(args))
    
    if args.speedup:
        compare_speeds(Path(args.engine), Path(args.reference_engine), None)
    if args.perft_speedup is not None:
        compare_speeds(Path(args.engine), Path(args.reference_engine), args.perft_speedup, False)
    if args.bulk_speedup is not None:
        compare_speeds(Path(args.engine), Path(args.reference_engine), args.bulk_speedup, True)
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())