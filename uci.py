from pathlib import Path
import subprocess
import logging
import re

from errors import EngineCommunicationError

universal_id: int = 0

class UCIHandler:
    def __init__(self, engine_path: Path, use_bulk=True):
        global universal_id

        self.engine = subprocess.Popen(engine_path.resolve(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

        self.use_bulk = use_bulk

        self.id = universal_id
        universal_id += 1

        self.name = "unknown"
        self.author = "unknown"

        self.logger = logging.getLogger()

        # UCI init
        self.send("uci")

        # For now, we discard UCI options
        while (line := self.readline()) != "uciok":
            if line.startswith("id name "):
                self.name = line[len("id name "):]
            elif line.startswith("id author "):
                self.author = line[len("id author "):]
        
        assert self.name != "unknown", "Engine did not provide name"
        assert self.author != "unknown", "Engine did not provide author"

        if self.engine.stdin is None:
            self.engine.kill()
            raise EngineCommunicationError("Failed to secure stdin on engine process")
        if self.engine.stdout is None:
            self.engine.kill()
            raise EngineCommunicationError("Failed to secure stdout on engine process")

        self.searching = False
    
    def __del__(self):
        if self.engine.poll() is None:
            self.engine.kill()
    
    def send_and_await(self, command: str, expected: str) -> None:
        assert self.engine.stdout is not None
        
        self.send(command)

        while self.readline() != expected:
            pass

    def send(self, command: str) -> None:
        assert self.engine.stdin is not None

        if not command.endswith('\n'):
            command += '\n'

        self.logger.debug(f"{self.name}[{self.id}] - GUI: {command}")

        self.engine.stdin.write(command)
        self.engine.stdin.flush()
    
    def readline(self) -> str:
        assert self.engine.stdout is not None

        line = self.engine.stdout.readline()
        if line == "":
            raise EngineCommunicationError(f"Engine '{self.name}' - ID {self.id} exited early")

        line = line.strip()
        self.logger.debug(f"{self.name}[{self.id}] - ENG: {line}")

        return line
    
    # UCI commands
    
    def ucinewgame(self) -> None:
        self.send("ucinewgame")
        self.isready()
    
    def isready(self) -> None:
        self.send_and_await("isready", "readyok")
    
    def set_option(self, name: str, value: str) -> None:
        self.send(f"setoption name {name} value {value}")
        self.isready()
    
    def set_position(self, start_fen: str, *moves: str) -> None:
        self.isready()
        command = f"position fen {start_fen}"
        if len(moves) > 0:
            command += " moves " + " ".join(moves)
        self.send(command)
        self.isready()
    
    def go(self, **kargs) -> None:
        self.isready()
        command = "go"
        if len(kargs) > 0:
            command += " " + " ".join(f"{k} {v}" for k, v in kargs.items())
        self.send(command)
        self.searching = True
        
    def stop(self) -> None:
        if hasattr(self, "searching") and self.searching:
            self.send("stop")
        self.searching = False
    
    def quit(self) -> None:
        self.send("quit")
    
    # Non-UCI commands

    def eval(self) -> int:
        self.send("eval")
        line = re.search(r"-?\d+", self.readline())
        if line is None:
            raise EngineCommunicationError("Non-UCI 'eval' command didn't return a number")
        return int(line.group())
    
    # Expects the engine to support the
    # "perft <depth>" command or "bulk <depth>" depending on the ctor parameter
    # and to return
    # "<move>: <nodes>" for each move, then
    # "<nodes> nodes <nodes per second> nps"
    def perft(self, depth: int) -> tuple[dict[str, int], int, int]:
        assert depth >= 1, "Can not run perft on negative depth"

        self.isready()
        if self.use_bulk:
            self.send(f"bulk {depth}")
        else:
            self.send(f"perft {depth}")

        moves = {}

        while True:
            line = self.readline()
            if (match:= re.fullmatch(r"([a-h][1-8][a-h][1-8][nrbq]?):\s*(\d+)", line)) is not None:
                move, nodes = match.group(1), match.group(2)

                assert move not in moves, "perft returned the same move more than once"

                moves[move] = int(nodes)
            else:
                break
        
        # Get the last line with the total node count + nps
        while True:
            if re.fullmatch(r"\d+ nodes \d+ nps", line) is not None:
                tokens = line.split(" ")
                nodes, nps = int(tokens[0]), int(tokens[2])
                break
            line = self.readline()
        
        return moves, nodes, nps