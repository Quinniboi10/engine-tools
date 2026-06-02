from errors import EngineBenchmarkError

from typing import Optional
from pathlib import Path
import subprocess
import logging
import math
import re

import datetime

from uci import UCIHandler

def _run_bench(engine: Path) -> tuple[int, int]:
    """
    Takes the path to an engine and runs './Engine bench'

    Returns:
        nodes, nps
    """
    try:
        result = subprocess.run([engine, "bench"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise EngineBenchmarkError(f"'{e.cmd}' returned non-zero exit code of {e.returncode}")
    
    pattern = re.compile(r"(\d+)\s*nodes\s+(\d+)\s*nps")

    for line in reversed(result.stdout.splitlines()): # Iterate backwards because usually you would end with the summary
        if (match := re.fullmatch(pattern, line)) is not None:
            return int(match.group(1)), int(match.group(2))
    
    raise EngineBenchmarkError(f"Failed to extract node count and nps from '{engine}'")
    
def _get_standard_error(values: list[float | int]) -> float:
    mean = sum(values) / len(values)
    std = math.sqrt(sum(((v - mean) ** 2) for v in values)/(len(values)))
    return std / math.sqrt(len(values))

def _avg(values: list[int | float]) -> float:
    return sum(values) / len(values)

def compare_speeds(dev_path: Path, base_path: Path, perft_depth: Optional[str] = None, use_bulk: bool = True) -> None:
    relative_speeds: list[float] = []

    # Yes, this could be one line, but this makes it more intuitive
    print("Beginning benchmark speed test")
    print("To stop, press Ctrl+C\n")

    avg_speedup = 1.0
    error = float("inf")

    if perft_depth is not None:
        fen, depth = perft_depth.rsplit(":", 1)
        depth = int(depth)

    try:
        while True:
            if perft_depth is not None:
                # Reinit every time to clear things like a movegen TT
                dev = UCIHandler(dev_path, use_bulk=use_bulk)
                base = UCIHandler(base_path, use_bulk=use_bulk)
                dev.ucinewgame()
                base.ucinewgame()
                dev.set_position(fen) # pyright: ignore[reportPossiblyUnboundVariable]
                base.set_position(fen) # pyright: ignore[reportPossiblyUnboundVariable]
                _, _, dev_nps, _, _, base_nps = *dev.perft(depth), *base.perft(depth) # pyright: ignore[reportPossiblyUnboundVariable]
            else:
                _, dev_nps, _, base_nps = *_run_bench(dev_path), *_run_bench(base_path)

            relative_speeds.append(dev_nps / base_nps)

            avg_speedup = _avg(relative_speeds)
            error = _get_standard_error(relative_speeds) if len(relative_speeds) > 1 else float("inf")

            logging.info(f"run {len(relative_speeds)} finished - relative speed of {relative_speeds[-1]}")

            print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - run {len(relative_speeds)} > ", end="")
            if abs(1 - avg_speedup) < error:
                print("Uncertainty too high to draw meaningful conclusions     ", end="\r")
            else:
                print(f"Dev bench ran {avg_speedup:.3f} ± {error:.3f} times faster than base bench", end="\r")
    except KeyboardInterrupt:
        pass

    # Clear the old \r
    print("\nBenchmark complete.")
    if abs(1 - avg_speedup) < error: # If the information was previously withheld, provide it now
        print(f"Dev bench ran {avg_speedup:.3f} ± {error:.3f} times faster than base bench")