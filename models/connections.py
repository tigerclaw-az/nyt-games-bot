import statistics as stats
import typing

from handlers.database import BaseDatabaseHandler
from models import BasePlayerStats, BasePuzzleEntry, PuzzleName

class ConnectionsPlayerStats(BasePlayerStats):
  # connections-specific stats
  raw_mean: float
  adj_mean: float

  def __init__(self) -> None:
    super().__init__()

    # connections-specific stats
    self.puzzle_name: typing.LiteralString = PuzzleName.CONNECTIONS.value.lower()
    self.raw_mean: float = 0.0
    self.adj_mean: float = 0.0

  async def initialize(self, user_id: int, puzzle_list: list[int], db: BaseDatabaseHandler) -> typing.Self:
    self.user_id = user_id

    player_puzzles: list[int] = await db.get_puzzles_by_player(self.user_id)
    player_entries: list[ConnectionsPuzzleEntry] = await db.get_entries_by_player(self.user_id, puzzle_list)

    self.missed_games = len([p for p in puzzle_list if p not in player_puzzles])

    if len(player_entries) > 0:
      self.raw_mean = stats.mean([e.score for e in player_entries])
      self.adj_mean = stats.mean([e.score for e in player_entries] + ([8] * self.missed_games))
    else:
      self.raw_mean = 0
      self.adj_mean = 0

    return self

  def get_stat_list(self) -> tuple[float, float]:
    return self.raw_mean, self.adj_mean

class ConnectionsPuzzleEntry(BasePuzzleEntry):
  # connections-specific details
  score: int
  puzzle_str: str

  def __init__(self, puzzle_id: int, user_id: int, score: int, puzzle_str: str) -> None:
    self.puzzle_id = puzzle_id
    self.user_id = user_id
    self.score = score
    self.puzzle_str = puzzle_str
