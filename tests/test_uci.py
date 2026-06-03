from uci import UCIHandler
from pathlib import Path
import sys

import pytest

@pytest.mark.timeout(2)
def test_uci():   
    engine = UCIHandler(Path(sys.executable), Path(__file__).resolve().parent / "mock_engine.py")

    assert engine.name == "Test Engine"
    assert engine.author == "Engine Tools Author"

    engine.ucinewgame()

    # These commands WILL have side effects
    assert engine.set_option("Threads", 1) == "setoption name Threads value 1"
    assert engine.set_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "e2e4", "e7e5") == "position fen rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 moves e2e4 e7e5"
    assert engine.go(nodes=1000, depth=5) == "go nodes 1000 depth 5"

    engine.stop()

    engine.quit()
    engine.engine.wait(timeout=1)
    assert engine.engine.poll() == 0