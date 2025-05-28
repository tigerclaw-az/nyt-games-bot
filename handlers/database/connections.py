import discord, re
from collections import Counter
from datetime import date

from handlers.database import BaseDatabaseHandler
from models import PuzzleName
from models.connections import ConnectionsPuzzleEntry
from utils.bot_utilities import BotUtilities

class ConnectionsDatabaseHandler(BaseDatabaseHandler):
  def __init__(self, utils: BotUtilities) -> None:
    utils.bot.logger.debug(f"Initializing {self.__class__.__name__} class.")

    # init
    super().__init__(utils)
    self.puzzle_name = PuzzleName.CONNECTIONS.value.lower()

    # puzzles
    self._arbitrary_date = date(2024, 1, 7)
    self._arbitrary_date_puzzle = 210

  ####################
  #  PUZZLE METHODS  #
  ####################

  async def add_entry(self, user: discord.User | discord.Member, title: str, puzzle: str, datetime) -> bool:
    puzzle_id_title: list[str] = re.findall(r'[\d,]+', title)
    score: int = self.__get_score_from_puzzle(puzzle)
    self.utils.bot.logger.debug(f"Connections->add_entry() :: {puzzle_id_title}\n{puzzle}\n->{score}")

    if puzzle_id_title:
      puzzle_id = int(str(puzzle_id_title[0]).replace(',', ''))
    else:
      return False

    await self.add_user_if_not_exists(user)
    user_id: int = user.id

    if await self.entry_exists(user_id, puzzle_id):
      self.utils.bot.logger.debug(f"Entry already exists for {user_id} and {puzzle_id}.")
      await self.connection.execute(
        f"update {self.puzzle_name} set score = ? where user_id = ? and puzzle_id = ?",
        (score, user_id, puzzle_id,)
      )
    else:
      self.utils.bot.logger.debug(f"Adding entry for {user_id} and {puzzle_id}.")
      await self.connection.execute(
        f"insert into {self.puzzle_name} values (?, ?, ?, ?, ?)",
        (puzzle_id, user_id, puzzle, score, datetime,)
      )

    await self.connection.commit()
    self.utils.bot.logger.debug(f"total_changes: {self.connection.total_changes}")
    return self.connection.total_changes > 0

  ####################
  #  PLAYER METHODS  #
  ####################

  async def get_entries_by_player(self, user_id: int, puzzle_list: list[int] = []) -> list[ConnectionsPuzzleEntry]:
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
