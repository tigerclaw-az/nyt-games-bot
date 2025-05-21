import aiosqlite, re
from datetime import date

from handlers.database import BaseDatabaseHandler
from models import PuzzleName
from models.strands import StrandsPuzzleEntry
from utils.bot_utilities import BotUtilities

class StrandsDatabaseHandler(BaseDatabaseHandler):
  def __init__(self, utils: BotUtilities, connection: aiosqlite.Connection) -> None:
    # init
    super().__init__(utils, connection)
    self.puzzle_name = PuzzleName.STRANDS.value.lower()

    # puzzles
    self._arbitrary_date = date(2024, 3, 5)
    self._arbitrary_date_puzzle = 2

  ####################
  #  PUZZLE METHODS  #
  ####################

  async def add_entry(self, user_id: str, title: str, puzzle: str) -> bool:
    self._utils.bot.logger.debug(f"Strands->add_entry() :: {title} | {puzzle}")
    puzzle_id_title = re.findall(r'[\d,]+', title)
    hints: int = puzzle.count('💡')

    if puzzle_id_title:
      puzzle_id = int(str(puzzle_id_title[0]).replace(',', ''))
    else:
      return False

    await self.add_user_if_not_exists(user_id)

    if await self.entry_exists(user_id, puzzle_id):
      self._utils.bot.logger.debug(f"Entry already exists for {user_id} and {puzzle_id}.")
      await self.connection.execute(
        f"update {self.puzzle_name} set hints = {hints}, puzzle_str = '{puzzle}' "
            + f"where user_id = '{user_id}' and puzzle_id = '{puzzle_id}'"
      )
    else:
      self._utils.bot.logger.debug(f"Adding entry for {user_id} and {puzzle_id}.")
      await self.connection.execute(
        f"insert into {self.puzzle_name} values (?, ?, ?, ?, ?)",
        (puzzle_id, user_id, puzzle, hints, None)
      )

    await self.connection.commit()
    self._utils.bot.logger.debug(f"total_changes: {self.connection.total_changes}")
    return self.connection.total_changes > 0

  ####################
  #  PLAYER METHODS  #
  ####################

  async def get_entries_by_player(self, user_id: str, puzzle_list: list[int] = []) -> list[StrandsPuzzleEntry]:
    if not puzzle_list or len(puzzle_list) == 0:
      query = f"select puzzle_id, hints, puzzle_str from {self.puzzle_name} where user_id = {user_id}"
    else:
      puzzle_list_str = ','.join([str(p_id) for p_id in puzzle_list])
      query = f"select puzzle_id, hints, puzzle_str from {self.puzzle_name} where user_id = {user_id} and puzzle_id in ({puzzle_list_str})"
    async with self.connection.execute_fetchall(query) as rows:
      entries: list[StrandsPuzzleEntry] = []
      for row in rows:
          entries.append(StrandsPuzzleEntry(row[0], user_id, row[1], row[2]))
      return entries
