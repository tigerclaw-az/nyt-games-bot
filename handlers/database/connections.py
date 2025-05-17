import aiosqlite, re
from collections import Counter
from datetime import date

from handlers.database import BaseDatabaseHandler
from models import PuzzleName
from models.connections import ConnectionsPuzzleEntry
from utils.bot_utilities import BotUtilities

class ConnectionsDatabaseHandler(BaseDatabaseHandler):
  def __init__(self, utils: BotUtilities, connection: aiosqlite.Connection) -> None:
    # init
    super().__init__(utils, connection)

    # puzzles
    self._arbitrary_date = date(2024, 1, 7)
    self._arbitrary_date_puzzle = 210
    self._puzzle_name = PuzzleName.CONNECTIONS.name.lower()

  ####################
  #  PUZZLE METHODS  #
  ####################

  async def add_entry(self, user_id: str, title: str, puzzle: str) -> bool:
    puzzle_id_title = re.findall(r'[\d,]+', title)
    score = self.__get_score_from_puzzle(puzzle)

    if puzzle_id_title:
      puzzle_id = int(str(puzzle_id_title[0]).replace(',', ''))
    else:
      return False

    await self.add_user_if_not_exists(user_id)

    if self.entry_exists(user_id, puzzle_id):
      await self.connection.execute(
        f"update {self._puzzle_name} set score = {score}, puzzle_str = '{puzzle}' "
            + f"where user_id = '{user_id}' and puzzle_id = '{puzzle_id}'"
      )
    else:
      await self.connection.execute(
        f"insert into {self._puzzle_name} (puzzle_id, user_id, score, puzzle_str) "
            + f"values ({puzzle_id}, {user_id}, {score}, '{puzzle}')"
      )

    self.connection.commit()
    return self.connection.total_changes > 0

  ####################
  #  PLAYER METHODS  #
  ####################

  async def get_entries_by_player(self, user_id: str, puzzle_list: list[int] = []) -> list[ConnectionsPuzzleEntry]:
    if not puzzle_list or len(puzzle_list) == 0:
      query = f"select puzzle_id, score, puzzle_str from {self._puzzle_name} where user_id = {user_id}"
    else:
      puzzle_list_str = ','.join([str(p_id) for p_id in puzzle_list])
      query = f"select puzzle_id, score, puzzle_str from {self._puzzle_name} where user_id = {user_id} and puzzle_id in ({puzzle_list_str})"
    async with self.connection.execute_fetchall(query) as rows:
      entries: list[ConnectionsPuzzleEntry] = []
      for row in rows:
        entries.append(ConnectionsPuzzleEntry(row[0], user_id, row[1], row[2]))
      return entries

  ####################
  #  HELPER METHODS  #
  ####################

  async def __get_score_from_puzzle(self, puzzle: str) -> int:
    puzzle_lines = puzzle.split('\n')
    if len(Counter(puzzle_lines[-1]).keys()) == 1:
      return len(puzzle_lines)
    else:
      return 8
