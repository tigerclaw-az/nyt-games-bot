import aiosqlite, re, typing
from collections import Counter
from datetime import date

from handlers.database import BaseDatabaseHandler
from models import PuzzleName
from models.connections import ConnectionsPuzzleEntry

if typing.TYPE_CHECKING:
  from utils.bot_utilities import BotUtilities

class ConnectionsDatabaseHandler(BaseDatabaseHandler):
  def __init__(self, utils: "BotUtilities", connection: aiosqlite.Connection) -> None:
    # init
    super().__init__(utils, connection)
    self.puzzle_name = PuzzleName.CONNECTIONS.value.lower()

    # puzzles
    self._arbitrary_date = date(2024, 1, 7)
    self._arbitrary_date_puzzle = 210

  ####################
  #  PUZZLE METHODS  #
  ####################

  async def add_entry(self, user_id: str, title: str, puzzle: str) -> bool:
    puzzle_id_title: list[str] = re.findall(r'[\d,]+', title)
    score: int = self.__get_score_from_puzzle(puzzle)
    self._utils.bot.logger.debug(f"add_entry() :: {puzzle_id_title} | {puzzle} | {score}")

    if puzzle_id_title:
      puzzle_id = int(str(puzzle_id_title[0]).replace(',', ''))
    else:
      return False

    await self.add_user_if_not_exists(user_id)

    if await self.entry_exists(user_id, puzzle_id):
      self._utils.bot.logger.debug(f"Entry already exists for {user_id} and {puzzle_id}.")
      await self.connection.execute(
        f"update {self.puzzle_name} set score = {score} "
            + f"where user_id = '{user_id}' and puzzle_id = '{puzzle_id}'"
      )
    else:
      self._utils.bot.logger.debug(f"Adding entry for {user_id} and {puzzle_id}.")
      await self.connection.execute(
        f"insert into {self.puzzle_name} values (?, ?, ?, ?, ?)",
        (puzzle_id, user_id, puzzle, score, None)
      )

    await self.connection.commit()
    self._utils.bot.logger.debug(f"total_changes: {self.connection.total_changes}")
    return self.connection.total_changes > 0

  ####################
  #  PLAYER METHODS  #
  ####################

  async def get_entries_by_player(self, user_id: str, puzzle_list: list[int] = []) -> list[ConnectionsPuzzleEntry]:
    if not puzzle_list or len(puzzle_list) == 0:
      query = f"select puzzle_id, score, puzzle_str from {self.puzzle_name} where user_id = {user_id}"
    else:
      puzzle_list_str = ','.join([str(p_id) for p_id in puzzle_list])
      query = f"select puzzle_id, score, puzzle_str from {self.puzzle_name} where user_id = {user_id} and puzzle_id in ({puzzle_list_str})"
    async with self.connection.execute_fetchall(query) as rows:
      entries: list[ConnectionsPuzzleEntry] = []
      for row in rows:
        entries.append(ConnectionsPuzzleEntry(row[0], user_id, row[1], row[2]))
      return entries

  ####################
  #  HELPER METHODS  #
  ####################

  def __get_score_from_puzzle(self, puzzle: str) -> int:
    puzzle_lines: list[str] = puzzle.split('\n')
    if len(Counter(puzzle_lines[-1]).keys()) == 1:
      return len(puzzle_lines)
    else:
      return 8
