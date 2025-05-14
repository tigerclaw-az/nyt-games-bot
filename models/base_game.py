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
  user_id: str
  missed_games: int
  rank: int

class BasePuzzleEntry(Protocol):
  puzzle_id: int
  puzzle_name: PuzzleName
  user_id: str
