from pathlib import Path
from uci import UCIHandler
from tests import *

import logging

def main():
    logging.basicConfig(filename="engine-bench.log", level=logging.DEBUG)

    engine = UCIHandler(Path("../Chess/Lazarus/Lazarus.exe"))

    working_eng = UCIHandler(Path("../Chess/Chaos/Chaos.exe"))

    debug_perft_suite(Path("../../Downloads/standard.epd"), working_eng, engine)

if __name__ == "__main__":
    main()