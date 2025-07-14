from enum import Enum, auto
from typing import Protocol

class PuzzleName(Enum):
  CONNECTIONS = 'Connections'
  CROSSWORDS = 'Crosswords'
  SPELLING_BEE = 'Spelling Bee'
  LETTERBOXED = 'Letterboxed'
  WORDLE = 'Wordle'
  STRANDS = 'Strands'

class PuzzleQueryType(Enum):
  SINGLE_PUZZLE = auto()
  MULTI_PUZZLE = auto()
  ALL_TIME = auto()

class BasePlayerStats(Protocol):
  missed_games: int
  puzzle_name: str
  rank: int
  user_id: int

  def __init__(self) -> None:
    self.missed_games = 0
    self.puzzle_name = ""
    self.rank = -1
    self.user_id = -1

class BasePuzzleEntry(Protocol):
  puzzle_id: int
  user_id: int
