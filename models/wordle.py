import typing
import statistics as stats
from handlers.database import BaseDatabaseHandler
from models import BasePlayerStats, BasePuzzleEntry, PuzzleName

class WordlePlayerStats(BasePlayerStats):
  # wordle-specific stats
  avg_green: float
  avg_yellow: float
  avg_other: float
  raw_mean: float
  adj_mean: float

  def __init__(self) -> None:
    super().__init__()

    # wordle-specific stats
    self.puzzle_name: typing.LiteralString = PuzzleName.WORDLE.value.lower()
    self.avg_green: float = 0.0
    self.avg_yellow: float = 0.0
    self.avg_other: float = 0.0
    self.adj_mean: float = 0.0
    self.raw_mean: float = 0.0

  async def initialize(self, user_id: int, puzzle_list: list[int], db: BaseDatabaseHandler) -> typing.Self:
    self.user_id = user_id

    player_puzzles: list[int] = await db.get_puzzles_by_player(self.user_id)
    player_entries: list[WordlePuzzleEntry] = await db.get_entries_by_player(self.user_id, puzzle_list)

    self.missed_games = len([p for p in puzzle_list if p not in player_puzzles])

    if len(player_entries) > 0:
      self.raw_mean = stats.mean([e.score for e in player_entries])
      self.adj_mean = stats.mean([e.score for e in player_entries] + ([7] * self.missed_games))
      self.avg_green = stats.mean([e.green for e in player_entries])
      self.avg_yellow = stats.mean([e.yellow for e in player_entries])
      self.avg_other = stats.mean([e.other for e in player_entries])
    else:
      self.raw_mean = 0
      self.adj_mean = 0
      self.avg_green = 0
      self.avg_yellow = 0
      self.avg_other = 0

    return self

  def get_stat_list(self) -> tuple[float, float, float, float, float]:
    return (self.raw_mean, self.adj_mean, self.avg_green, self.avg_yellow, self.avg_other)

class WordlePuzzleEntry(BasePuzzleEntry):
  # wordle-specific details
  score: int
  green: int
  yellow: int
  other: int

  def __init__(self, puzzle_id: int, user_id: int, score: int, green: int, yellow: int, other: int) -> None:
    self.puzzle_id = puzzle_id
    self.user_id = user_id
    self.score = score
    self.green = green
    self.yellow = yellow
    self.other = other
