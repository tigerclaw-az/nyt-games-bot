import aiosqlite, re
from datetime import date

from handlers.database import BaseDatabaseHandler
from models import PuzzleName
from models.wordle import WordlePuzzleEntry
from utils.bot_utilities import BotUtilities

class WordleDatabaseHandler(BaseDatabaseHandler):
  def __init__(self, utils: BotUtilities, connection: aiosqlite.Connection) -> None:
    # init
    super().__init__(utils, connection)

    # puzzles
    self._arbitrary_date = date(2022, 1, 10)
    self._arbitrary_date_puzzle = 205
    self._puzzle_name = PuzzleName.WORDLE.name.lower()

  ####################
  #  PUZZLE METHODS  #
  ####################

  async def add_entry(self, user_id: str, title: str, puzzle: str) -> bool:
    if 'X/6' in title:
      reg_match = re.search(r'\d{1,3}(,\d{3})*', title)
      if reg_match:
        puzzle_id = reg_match.group(0).replace(',', '')
        score = 7
      else:
        return False
    else:
      reg_match = re.search(r'\d{1,3}(,\d{3})*', title)
      if reg_match:
        puzzle_id = reg_match.group(0).replace(',', '')
        reg_match = re.search(r'(\d)\/(\d)', title)
        if reg_match:
          score = reg_match.group(1)
        else:
          return False
      else:
        return False

    puzzle_id = int(puzzle_id)
    score = int(score)

    total_green = puzzle.count('🟩')
    total_yellow = puzzle.count('🟨')
    total_other = puzzle.count('⬜') + puzzle.count('⬛')

    await self.add_user_if_not_exists(user_id)

    if self.entry_exists(user_id, puzzle_id):
      await self.connection.execute(
          f"update {self._puzzle_name} set score = {score}, green = {total_green}, yellow = {total_yellow}, other = {total_other} "
            + f"where user_id = '{user_id}' and puzzle_id = '{puzzle_id}'"
      )
    else:
      await self.connection.execute(
        f"insert into {self._puzzle_name} (puzzle_id, user_id, score, green, yellow, other) "
          + f"values ({puzzle_id}, {user_id}, {score}, {total_green}, {total_yellow}, {total_other})"
      )

    self.connection.commit()
    return self.connection.total_changes > 0

  ####################
  #  PLAYER METHODS  #
  ####################

  async def get_entries_by_player(self, user_id: str, puzzle_list: list[int] = []) -> list[WordlePuzzleEntry]:
    if not puzzle_list or len(puzzle_list) == 0:
      query = f"select puzzle_id, score, green, yellow, other from {self._puzzle_name} where user_id = {user_id} AND puzzle_name = {self._puzzle_name}"
    else:
      puzzle_list_str = ','.join([str(p_id) for p_id in puzzle_list])
      query = f"select puzzle_id, score, green, yellow, other from {self._puzzle_name} where user_id = {user_id} and puzzle_id in ({puzzle_list_str})"
    async with self.connection.execute_fetchall(query) as rows:
      entries: list[WordlePuzzleEntry] = []
      for row in rows:
        entries.append(WordlePuzzleEntry(row[0], user_id, row[1], row[2], row[3], row[4]))
      return entries
