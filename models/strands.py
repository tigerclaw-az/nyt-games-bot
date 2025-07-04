import statistics as stats
import typing

from handlers.database import BaseDatabaseHandler
from models import BasePlayerStats, BasePuzzleEntry, PuzzleName

class StrandsPlayerStats(BasePlayerStats):
  # strands-specific stats
  avg_hints: float
  avg_spangram_index: float
  avg_rating_raw: float
  avg_rating_adj: float

  def __init__(self) -> None:
    super().__init__()
    # strands-specific stats
    self.puzzle_name: typing.LiteralString = PuzzleName.STRANDS.value.lower()
    self.raw_mean: float = 0.0
    self.adj_mean: float = 0.0
    self.rank: int = -1

  async def initialize(self, user_id: int, puzzle_list: list[int], db: BaseDatabaseHandler) -> typing.Self:
    self.user_id = user_id

    player_puzzles: list[int] = await db.get_puzzles_by_player(self.user_id)
    player_entries: list[StrandsPuzzleEntry] = await db.get_entries_by_player(self.user_id, puzzle_list)

    self.missed_games = len([p for p in puzzle_list if p not in player_puzzles])

    if len(player_entries) > 0:
      self.avg_rating_raw = stats.mean([e.rating for e in player_entries])
      self.avg_rating_adj = stats.mean([e.rating for e in player_entries] + ([1.0] * self.missed_games))
      self.avg_hints = stats.mean([e.hints for e in player_entries])
      self.avg_spangram_index = stats.mean([e.spangram_index for e in player_entries])
    else:
      self.avg_rating_raw = 0
      self.avg_rating_adj = 0
      self.avg_hints = 0
      self.avg_spangram_index = 0

    return self

  def get_stat_list(self) -> tuple[float, float, float, float]:
    return self.avg_rating_raw, self.avg_rating_adj, self.avg_hints, self.avg_spangram_index

class StrandsPuzzleEntry(BasePuzzleEntry):
  # strands-specific details
  hints: int
  spangram_index: int
  rating: float
  puzzle_str: str

  # contants
  HINT_PENALTY: float = 0.25

  def __init__(self, puzzle_id: int, user_id: int, hints: int, puzzle_str: str) -> None:
    self.puzzle_id = puzzle_id
    self.user_id = user_id
    self.hints = hints
    self.puzzle_str = self.__clean_puzzle_str(puzzle_str)
    self.spangram_index = self.__get_spangram_index(self.puzzle_str)
    self.rating = self.__get_rating(self.hints, self.spangram_index, self.puzzle_str)

  def __clean_puzzle_str(self, puzzle_str: str) -> str:
    return puzzle_str.strip().replace('\n', '').replace(' ', '')

  def __get_spangram_index(self, puzzle_str: str) -> int:
    for index, item in enumerate(puzzle_str):
      if item == '🟡':
        return index + 1
    return len(puzzle_str) + 1

  def __get_rating(self, hints: int, spangram_index: int, puzzle_str: str) -> float:
    word_count = puzzle_str.count('🔵')
    hint_penalty = hints * self.HINT_PENALTY
    if word_count > 0:
      spangram_penalty = ((spangram_index - 1.0) / word_count) * self.HINT_PENALTY
      return 1.0 + spangram_penalty + hint_penalty
    else:
      return 1.0 + hint_penalty
