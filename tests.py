import chess
from typing import Optional
import logging
from pathlib import Path

from uci import UCIHandler

def _find_perft_mismatch(fen: str, depth: int, working_eng: UCIHandler, debug_eng: UCIHandler, expected_nodes: Optional[int] = None) -> Optional[tuple[str, str]]:
    """
    Find the mismatch in perft numbers between 2 engines

    Args:
        fen (str): Position to search from
        depth (int): Perft depth
        working_eng (UCIHandler): Functional engine to use as reference
        debug_eng (UCIHandler): Engine to debug
    
    Returns:
        (broken fen, flagged move) or None if no issue is found
    """

    working_eng.ucinewgame()
    debug_eng.ucinewgame()

    board = chess.Board(fen)

    while depth > 0:
        working_eng.set_position(board.fen())
        debug_eng.set_position(board.fen())
        
        debug_moves, total_nodes, _ = debug_eng.perft(depth)

        if total_nodes == expected_nodes:
            return None

        exp_moves, _, _ = working_eng.perft(depth)

        e_moves_set = set(exp_moves)
        d_moves_set = set(debug_moves)

        bad_moves = e_moves_set ^ d_moves_set

        if len(bad_moves) > 0:
            return board.board_fen(), next(iter(bad_moves))
        
        for move, nodes in exp_moves.items():
            if debug_moves[move] != nodes:
                logging.info(f"Found bad move at depth {depth}: {move}")
                board.push_uci(move)
                break

        depth -= 1
    
    return None

def debug_perft(fen: str, depth: int, working_eng: UCIHandler, debug_eng: UCIHandler) -> None:
    """
    Debugs an individual FEN and finds a move that's behaving unexpectedly
    """
    result = _find_perft_mismatch(fen, depth, working_eng, debug_eng)

    if result is None:
        print("No issues found")
    else:
        fen, move = result
        print(f"Found issue! {fen} - {move}")

def debug_perft_suite(suite: Path, working_eng: UCIHandler, debug_eng: UCIHandler, stop_on_first_pos: bool = True) -> None:
    """
    Parses a file containing perft positions
    See https://github.com/AndyGrant/Ethereal/blob/master/src/perft/standard.epd for an example
    """
    with open(suite) as f:
        for line in f:
            tokens = line.split(';')

            # Eat the \n char
            tokens[-1] = tokens[-1][:-1]

            fen = tokens.pop(0).strip()

            # Iterate over given depths
            while len(tokens) > 0:
                depth, nodes = tokens.pop(0).strip().split(' ')
                
                depth = int(depth[1:])
                nodes = int(nodes)

                result = _find_perft_mismatch(fen, depth, working_eng, debug_eng, nodes)

                if result is not None:
                    debug_perft(fen, depth, working_eng, debug_eng)
                    if stop_on_first_pos:
                        return